"""Recepcao e normalizacao de formularios instantaneos da Meta.

O webhook entrega apenas IDs. Este modulo busca os dados completos na Graph
API, registra o lead no Supabase e mantem idempotencia pelo ``leadgen_id``.
Nenhum token ou dado pessoal e escrito em log.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

import requests

from core import crm, leads


class MetaErro(RuntimeError):
    """Falha segura durante a recepcao ou consulta de um lead da Meta."""


CAMPOS_GRAPH = (
    "id,created_time,ad_id,ad_name,adset_id,adset_name,"
    "campaign_id,campaign_name,form_id,field_data,platform,is_organic"
)

_CAMPOS_CONSENTIMENTO_PADRAO = {
    "whatsapp_opt_in",
    "aceita_whatsapp",
    "aceito_receber_mensagens_no_whatsapp",
    "autoriza_contato_por_whatsapp",
    "autorizo_contato_por_whatsapp",
    "consentimento_whatsapp",
}


def _texto_env(nome: str) -> str:
    return os.environ.get(nome, "").strip()


def _lista_env(nome: str) -> set[str]:
    return {item.strip() for item in _texto_env(nome).split(",") if item.strip()}


def configurado() -> bool:
    """Indica se o webhook pode validar, consultar e persistir um lead."""
    tem_token = bool(_texto_env("META_PAGE_ACCESS_TOKEN") or _texto_env("META_PAGE_ACCESS_TOKENS_JSON"))
    return bool(
        _texto_env("META_VERIFY_TOKEN")
        and _texto_env("META_APP_SECRET")
        and tem_token
        and crm.disponivel()
    )


def assinatura_valida(corpo: bytes, assinatura: str, *, segredo: str | None = None) -> bool:
    """Valida ``X-Hub-Signature-256`` sobre os bytes exatos recebidos."""
    chave = (segredo if segredo is not None else _texto_env("META_APP_SECRET")).encode()
    if not chave or not assinatura.startswith("sha256="):
        return False
    esperada = "sha256=" + hmac.new(chave, corpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, assinatura.strip())


def extrair_notificacoes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extrai apenas mudancas ``leadgen`` validas de um webhook de Page."""
    if payload.get("object") != "page":
        return []
    notificacoes: list[dict[str, Any]] = []
    for entrada in payload.get("entry") or []:
        if not isinstance(entrada, dict):
            continue
        for mudanca in entrada.get("changes") or []:
            if not isinstance(mudanca, dict) or mudanca.get("field") != "leadgen":
                continue
            valor = mudanca.get("value")
            if not isinstance(valor, dict) or not valor.get("leadgen_id"):
                continue
            notificacao = {
                "leadgen_id": str(valor["leadgen_id"]),
                "page_id": str(valor.get("page_id") or entrada.get("id") or "") or None,
                "form_id": str(valor.get("form_id") or "") or None,
                "ad_id": str(valor.get("ad_id") or valor.get("adgroup_id") or "") or None,
                "created_time": valor.get("created_time") or entrada.get("time"),
            }
            notificacoes.append(notificacao)
    return notificacoes


def _token_da_pagina(page_id: str | None) -> str:
    por_pagina = _texto_env("META_PAGE_ACCESS_TOKENS_JSON")
    if por_pagina:
        try:
            tokens = json.loads(por_pagina)
        except json.JSONDecodeError as erro:
            raise MetaErro("META_PAGE_ACCESS_TOKENS_JSON nao e um JSON valido.") from erro
        if not isinstance(tokens, dict):
            raise MetaErro("META_PAGE_ACCESS_TOKENS_JSON precisa ser um objeto.")
        token = str(tokens.get(str(page_id)) or "").strip()
        if token:
            return token
    token = _texto_env("META_PAGE_ACCESS_TOKEN")
    if not token:
        raise MetaErro("Token de acesso da pagina Meta nao configurado.")
    return token


def _versao_graph() -> str:
    versao = _texto_env("META_GRAPH_API_VERSION") or "v26.0"
    if not re.fullmatch(r"v\d+\.\d+", versao):
        raise MetaErro("META_GRAPH_API_VERSION invalida.")
    return versao


def buscar_lead(notificacao: dict[str, Any]) -> dict[str, Any]:
    """Busca os campos completos usando o ID entregue pelo webhook."""
    leadgen_id = str(notificacao.get("leadgen_id") or "").strip()
    if not leadgen_id:
        raise MetaErro("Notificacao sem leadgen_id.")
    token = _token_da_pagina(notificacao.get("page_id"))
    parametros = {"access_token": token, "fields": CAMPOS_GRAPH}
    segredo = _texto_env("META_APP_SECRET")
    if segredo:
        parametros["appsecret_proof"] = hmac.new(
            segredo.encode(), token.encode(), hashlib.sha256
        ).hexdigest()
    try:
        resposta = requests.get(
            f"https://graph.facebook.com/{_versao_graph()}/{leadgen_id}",
            params=parametros,
            timeout=15,
        )
    except requests.RequestException as erro:
        raise MetaErro("A Graph API nao respondeu a tempo.") from erro
    if not resposta.ok:
        detalhe = ""
        try:
            detalhe = str((resposta.json().get("error") or {}).get("message") or "")
        except (ValueError, AttributeError):
            pass
        sufixo = f": {detalhe[:240]}" if detalhe else ""
        raise MetaErro(f"Graph API devolveu HTTP {resposta.status_code}{sufixo}")
    try:
        dados = resposta.json()
    except ValueError as erro:
        raise MetaErro("Graph API devolveu uma resposta invalida.") from erro
    if not isinstance(dados, dict) or not dados.get("id"):
        raise MetaErro("Graph API nao devolveu o lead solicitado.")
    return dados


def _slug(valor: Any) -> str:
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


def _valor_campo(item: dict[str, Any]) -> Any:
    valores = item.get("values")
    if not isinstance(valores, list):
        return valores
    limpos = [valor for valor in valores if valor is not None]
    if len(limpos) == 1:
        return limpos[0]
    return limpos


def _mapear_campos(field_data: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    originais: dict[str, Any] = {}
    normalizados: dict[str, Any] = {}
    for item in field_data or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        nome = str(item["name"])
        valor = _valor_campo(item)
        originais[nome] = valor
        normalizados[_slug(nome)] = valor
    return originais, normalizados


def _primeiro_campo(campos: dict[str, Any], nomes: tuple[str, ...]) -> str | None:
    for nome in nomes:
        valor = campos.get(nome)
        if isinstance(valor, list):
            valor = valor[0] if valor else None
        texto = str(valor or "").strip()
        if texto:
            return texto
    return None


def _interpretar_consentimento(valor: Any) -> bool | None:
    if isinstance(valor, list):
        valor = " ".join(str(item) for item in valor)
    texto = _slug(valor)
    if not texto:
        return None
    negativos = ("nao", "no", "false", "recuso", "nao_autorizo", "nao_concordo")
    if texto in negativos or texto.startswith(("nao_", "no_")):
        return False
    positivos = ("sim", "yes", "true", "1", "aceito", "autorizo", "concordo")
    if texto in positivos or texto.startswith(("sim_", "yes_", "aceito_", "autorizo_", "concordo_")):
        return True
    return None


def _consentimento(campos: dict[str, Any]) -> tuple[bool | None, str | None]:
    configurados = {_slug(item) for item in _lista_env("META_WHATSAPP_OPT_IN_FIELDS")}
    candidatos = configurados or _CAMPOS_CONSENTIMENTO_PADRAO
    for nome in candidatos:
        if nome in campos:
            return _interpretar_consentimento(campos[nome]), nome
    return None, None


def _data_iso(valor: Any) -> str | None:
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor, tz=timezone.utc).isoformat()
    texto = str(valor or "").strip()
    return texto or None


def normalizar_lead(
    dados_graph: dict[str, Any], notificacao: dict[str, Any]
) -> dict[str, Any]:
    """Converte nomes variaveis dos formularios para o schema interno."""
    originais, campos = _mapear_campos(dados_graph.get("field_data"))
    nome = _primeiro_campo(campos, ("full_name", "nome_completo", "name", "nome"))
    if not nome:
        partes = [
            _primeiro_campo(campos, ("first_name", "primeiro_nome")),
            _primeiro_campo(campos, ("last_name", "sobrenome")),
        ]
        nome = " ".join(parte for parte in partes if parte) or None
    telefone = _primeiro_campo(
        campos, ("phone_number", "phone", "telefone", "numero_de_telefone", "whatsapp")
    )
    email = _primeiro_campo(campos, ("email", "email_address", "e_mail"))
    opt_in, fonte_opt_in = _consentimento(campos)
    criado_em = _data_iso(dados_graph.get("created_time") or notificacao.get("created_time"))

    linhas = ["Formulário da Meta recebido."]
    campos_contato = {
        "full_name", "nome_completo", "name", "nome", "first_name", "primeiro_nome",
        "last_name", "sobrenome", "phone_number", "phone", "telefone",
        "numero_de_telefone", "whatsapp", "email", "email_address", "e_mail",
    }
    campos_consentimento = _CAMPOS_CONSENTIMENTO_PADRAO | {
        _slug(item) for item in _lista_env("META_WHATSAPP_OPT_IN_FIELDS")
    }
    for chave, valor in campos.items():
        if chave in campos_contato or chave in campos_consentimento:
            continue
        if isinstance(valor, list):
            texto = ", ".join(str(item) for item in valor)
        else:
            texto = str(valor or "").strip()
        if texto:
            linhas.append(f"{chave.replace('_', ' ').title()}: {texto}")

    return {
        "nome": nome,
        "telefone": telefone,
        "email": email,
        "leadgen_id": str(dados_graph.get("id") or notificacao["leadgen_id"]),
        "meta_page_id": str(notificacao.get("page_id") or "") or None,
        "meta_form_id": str(dados_graph.get("form_id") or notificacao.get("form_id") or "") or None,
        "meta_campaign_id": str(dados_graph.get("campaign_id") or "") or None,
        "meta_campaign_name": str(dados_graph.get("campaign_name") or "") or None,
        "meta_adset_id": str(dados_graph.get("adset_id") or "") or None,
        "meta_adset_name": str(dados_graph.get("adset_name") or "") or None,
        "meta_ad_id": str(dados_graph.get("ad_id") or notificacao.get("ad_id") or "") or None,
        "meta_ad_name": str(dados_graph.get("ad_name") or "") or None,
        "meta_platform": str(dados_graph.get("platform") or "") or None,
        "meta_is_organic": dados_graph.get("is_organic"),
        "meta_created_time": criado_em,
        "campos_meta": originais,
        "whatsapp_opt_in": opt_in,
        "whatsapp_opt_in_em": criado_em if opt_in is True else None,
        "whatsapp_opt_in_fonte": f"meta_form:{fonte_opt_in}" if fonte_opt_in else None,
        "mensagem": "\n".join(linhas)[:2000],
    }


def _permitida(notificacao: dict[str, Any]) -> bool:
    paginas = _lista_env("META_ALLOWED_PAGE_IDS")
    formularios = _lista_env("META_ALLOWED_FORM_IDS")
    if paginas and str(notificacao.get("page_id") or "") not in paginas:
        return False
    if formularios and str(notificacao.get("form_id") or "") not in formularios:
        return False
    return True


def _resumo_notificacao(lead: dict[str, Any]) -> str:
    consentimento = lead.get("whatsapp_opt_in")
    texto_opt_in = "sim" if consentimento is True else "não" if consentimento is False else "não informado"
    linhas = [
        "📋 LEAD DE FORMULÁRIO META",
        f"Nome: {lead.get('nome') or 'não informado'}",
        f"Telefone: {lead.get('telefone') or 'não informado'}",
        f"E-mail: {lead.get('email') or 'não informado'}",
        f"Campanha: {lead.get('meta_campaign_name') or lead.get('meta_campaign_id') or 'não informada'}",
        f"Anúncio: {lead.get('meta_ad_name') or lead.get('meta_ad_id') or 'não informado'}",
        f"Consentimento WhatsApp: {texto_opt_in}",
        "Abrir o painel para fazer o primeiro atendimento.",
    ]
    return "\n".join(linhas)


def processar_notificacao(notificacao: dict[str, Any]) -> dict[str, Any]:
    """Processa uma notificacao com fila, retry e marcacao de falha."""
    leadgen_id = str(notificacao.get("leadgen_id") or "").strip()
    if not leadgen_id:
        raise MetaErro("Notificacao sem leadgen_id.")
    deve_processar = crm.preparar_evento_meta(notificacao)
    if not deve_processar:
        return {"status": "duplicado", "leadgen_id": leadgen_id}
    if not _permitida(notificacao):
        crm.marcar_evento_meta(leadgen_id, "ignorado")
        return {"status": "ignorado", "leadgen_id": leadgen_id}

    try:
        dados_graph = buscar_lead(notificacao)
        normalizado = normalizar_lead(dados_graph, notificacao)
        lead, criado = crm.registrar_lead_meta(normalizado)
        crm.marcar_evento_meta(leadgen_id, "processado", lead_id=lead["id"])
        if criado:
            agente = _texto_env("CRM_AGENTE") or "ah_imobiliaria"
            leads.enviar_lead(agente, _resumo_notificacao({**normalizado, **lead}))
        return {
            "status": "processado" if criado else "duplicado",
            "leadgen_id": leadgen_id,
            "lead_id": lead["id"],
        }
    except (MetaErro, crm.CRMErro) as erro:
        try:
            crm.marcar_evento_meta(leadgen_id, "erro", erro=str(erro))
        except crm.CRMErro:
            pass
        raise


def processar_payload(payload: dict[str, Any]) -> dict[str, int]:
    notificacoes = extrair_notificacoes(payload)
    contagens = {"recebidos": len(notificacoes), "processados": 0, "duplicados": 0, "ignorados": 0}
    falhas = 0
    for notificacao in notificacoes:
        try:
            resultado = processar_notificacao(notificacao)
        except (MetaErro, crm.CRMErro):
            falhas += 1
            continue
        chave = {
            "processado": "processados",
            "duplicado": "duplicados",
            "ignorado": "ignorados",
        }[resultado["status"]]
        contagens[chave] += 1
    if falhas:
        raise MetaErro(f"Falha ao processar {falhas} de {len(notificacoes)} notificacoes.")
    return contagens
