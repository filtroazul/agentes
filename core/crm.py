"""Persistencia do funil de leads no Supabase.

O navegador usa a sessao normal do corretor e fica limitado pelo RLS. O
webhook usa SUPABASE_SERVICE_ROLE_KEY porque recebe mensagens sem uma sessao do
corretor. Essa chave nunca e devolvida ao navegador nem escrita em logs.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests


class CRMErro(RuntimeError):
    """Falha de comunicacao ou permissao no CRM."""


def _configuracao() -> tuple[str, str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    publica = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    servico = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return url, publica, servico


def disponivel() -> bool:
    """O webhook so persiste quando URL e chave de servico estao configuradas."""
    url, _, servico = _configuracao()
    return bool(url and servico)


def _cabecalhos(
    *, token: str | None = None, servico: bool = False, prefer: str | None = None
) -> dict[str, str]:
    _, publica, chave_servico = _configuracao()
    chave = chave_servico if servico else publica
    if not chave:
        raise CRMErro("A chave do Supabase para esta operacao nao foi configurada.")
    cabecalhos = {
        "apikey": chave,
        "Content-Type": "application/json",
    }
    # As chaves secretas atuais (sb_secret_*) autenticam pelo header apikey e
    # nao sao JWTs. Envia-las como Bearer faria o gateway tentar decodifica-las
    # e rejeitar uma credencial valida. As chaves legadas service_role seguem
    # sendo JWTs e precisam do Authorization abaixo.
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    elif not (servico and chave.startswith("sb_secret_")):
        cabecalhos["Authorization"] = f"Bearer {chave}"
    if prefer:
        cabecalhos["Prefer"] = prefer
    return cabecalhos


def _rest(
    metodo: str,
    recurso: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any = None,
    token: str | None = None,
    servico: bool = False,
    prefer: str | None = None,
) -> Any:
    url, _, _ = _configuracao()
    if not url:
        raise CRMErro("SUPABASE_URL nao foi configurada.")
    try:
        resposta = requests.request(
            metodo,
            f"{url}/rest/v1/{recurso}",
            params=params,
            json=json,
            headers=_cabecalhos(token=token, servico=servico, prefer=prefer),
            timeout=10,
        )
    except requests.RequestException as erro:
        raise CRMErro("O CRM nao respondeu a tempo.") from erro
    if not resposta.ok:
        detalhe = ""
        try:
            detalhe = resposta.json().get("message", "")
        except (ValueError, AttributeError):
            detalhe = resposta.text[:180]
        raise CRMErro(detalhe or f"O CRM respondeu HTTP {resposta.status_code}.")
    if not resposta.content:
        return None
    try:
        return resposta.json()
    except ValueError:
        return resposta.text


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _primeiro(dados: Any) -> dict[str, Any] | None:
    return dados[0] if isinstance(dados, list) and dados else None


def _origem(valor: str) -> str:
    permitidas = {"site", "whatsapp", "instagram", "telefone", "indicacao", "portal"}
    return valor if valor in permitidas else "whatsapp"


def registrar_entrada(
    *,
    canal_id: str,
    origem: str,
    texto: str,
    nome: str | None = None,
    telefone: str | None = None,
    email: str | None = None,
    external_id: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Encontra ou cria o lead e grava a mensagem recebida.

    Retorna (lead, mensagem_nova). Em retry do ManyChat, mensagem_nova=False.
    """
    if not disponivel():
        raise CRMErro("CRM do webhook nao configurado.")
    origem = _origem(origem)
    encontrados = _rest(
        "GET",
        "leads",
        params={
            "select": "*",
            "origem": f"eq.{origem}",
            "canal_id": f"eq.{canal_id}",
            "limit": "1",
        },
        servico=True,
    )
    lead = _primeiro(encontrados)

    if not lead:
        registro = {
            "nome": (nome or "").strip() or None,
            "telefone": "".join(c for c in (telefone or "") if c.isdigit()) or None,
            "email": (email or "").strip() or None,
            "origem": origem,
            "canal_id": canal_id,
            "mensagem": texto[:2000],
            "status": "novo",
            "proximo_contato": (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat(),
            "ultimo_contato": _agora(),
        }
        criados = _rest(
            "POST", "leads", json=registro, servico=True, prefer="return=representation"
        )
        lead = _primeiro(criados)
    else:
        mudancas: dict[str, Any] = {"ultimo_contato": _agora()}
        if nome and not lead.get("nome"):
            mudancas["nome"] = nome.strip()[:120]
        if telefone and not lead.get("telefone"):
            mudancas["telefone"] = "".join(c for c in telefone if c.isdigit())
        if email and not lead.get("email"):
            mudancas["email"] = email.strip()
        atualizados = _rest(
            "PATCH",
            "leads",
            params={"id": f"eq.{lead['id']}"},
            json=mudancas,
            servico=True,
            prefer="return=representation",
        )
        lead = _primeiro(atualizados) or {**lead, **mudancas}

    if not lead:
        raise CRMErro("Nao foi possivel criar o lead no CRM.")

    if external_id:
        existente = _rest(
            "GET",
            "lead_interacoes",
            params={
                "select": "id",
                "canal": f"eq.{origem}",
                "external_id": f"eq.{external_id}",
                "limit": "1",
            },
            servico=True,
        )
        if existente:
            return lead, False

    _rest(
        "POST",
        "lead_interacoes",
        json={
            "lead_id": lead["id"],
            "tipo": "mensagem",
            "direcao": "entrada",
            "autor": "lead",
            "canal": origem,
            "conteudo": texto[:4000],
            "automatico": False,
            "external_id": external_id,
        },
        servico=True,
        prefer="return=minimal",
    )
    return lead, True


def registrar_saida(
    lead_id: str,
    texto: str,
    *,
    canal: str,
    external_id: str | None = None,
    automatico: bool = True,
) -> None:
    agora = _agora()
    _rest(
        "POST",
        "lead_interacoes",
        json={
            "lead_id": lead_id,
            "tipo": "mensagem",
            "direcao": "saida",
            "autor": "ia" if automatico else "corretor",
            "canal": _origem(canal),
            "conteudo": texto[:4000],
            "automatico": automatico,
            "external_id": external_id,
        },
        servico=True,
        prefer="return=minimal",
    )
    _rest(
        "PATCH",
        "leads",
        params={"id": f"eq.{lead_id}"},
        json={"ultimo_contato": agora},
        servico=True,
        prefer="return=minimal",
    )
    _rest(
        "PATCH",
        "leads",
        params={"id": f"eq.{lead_id}", "primeira_resposta_em": "is.null"},
        json={"primeira_resposta_em": agora},
        servico=True,
        prefer="return=minimal",
    )


def resposta_por_external_id(canal: str, external_id: str) -> str | None:
    dados = _rest(
        "GET",
        "lead_interacoes",
        params={
            "select": "conteudo",
            "canal": f"eq.{_origem(canal)}",
            "external_id": f"eq.{external_id}",
            "limit": "1",
        },
        servico=True,
    )
    item = _primeiro(dados)
    return item.get("conteudo") if item else None


def registrar_erro(lead_id: str, texto: str, *, canal: str) -> None:
    _rest(
        "POST",
        "lead_interacoes",
        json={
            "lead_id": lead_id,
            "tipo": "erro",
            "direcao": "interna",
            "autor": "sistema",
            "canal": _origem(canal),
            "conteudo": texto[:1000],
            "automatico": True,
        },
        servico=True,
        prefer="return=minimal",
    )


def atualizar_resumo(lead_id: str, resumo: str) -> None:
    _rest(
        "PATCH",
        "leads",
        params={"id": f"eq.{lead_id}"},
        json={"resumo": resumo[:4000], "status": "qualificado", "qualificado_em": _agora()},
        servico=True,
        prefer="return=minimal",
    )
    _rest(
        "POST",
        "lead_interacoes",
        json={
            "lead_id": lead_id,
            "tipo": "ia_resumo",
            "direcao": "interna",
            "autor": "ia",
            "canal": "sistema",
            "conteudo": resumo[:4000],
            "automatico": True,
        },
        servico=True,
        prefer="return=minimal",
    )


def historico_do_lead(lead_id: str, *, limite: int = 20) -> list[dict[str, str]]:
    itens = _rest(
        "GET",
        "lead_interacoes",
        params={
            "select": "direcao,autor,conteudo,criado_em",
            "lead_id": f"eq.{lead_id}",
            "tipo": "eq.mensagem",
            "order": "criado_em.desc",
            "limit": str(limite),
        },
        servico=True,
    )
    historico = []
    for item in reversed(itens or []):
        role = "assistant" if item.get("direcao") == "saida" else "user"
        historico.append({"role": role, "content": item.get("conteudo", "")})
    return historico


def configuracao_ia() -> dict[str, Any]:
    if not disponivel():
        return {"modo": "automatico", "agente": "ah_imobiliaria", "canais": []}
    dados = _rest(
        "GET",
        "configuracoes_ia",
        params={"select": "*", "id": "eq.principal", "limit": "1"},
        servico=True,
    )
    return _primeiro(dados) or {
        "modo": "automatico",
        "agente": "ah_imobiliaria",
        "canais": ["whatsapp", "instagram"],
        "mensagem_pausa": "Recebi sua mensagem. O corretor vai continuar o atendimento por aqui.",
    }


def validar_corretor(token: str) -> dict[str, Any]:
    """Valida JWT no Auth e confirma que o usuario pertence a equipe ativa."""
    url, publica, _ = _configuracao()
    if not url or not publica or not token:
        raise CRMErro("Sessao ausente.")
    try:
        resposta = requests.get(
            f"{url}/auth/v1/user",
            headers={"apikey": publica, "Authorization": f"Bearer {token}"},
            timeout=8,
        )
    except requests.RequestException as erro:
        raise CRMErro("Nao consegui validar a sessao.") from erro
    if not resposta.ok:
        raise CRMErro("Sessao expirada ou invalida.")
    usuario = resposta.json()
    equipe = _rest(
        "GET",
        "corretores",
        params={"select": "id,nome,ativo", "id": f"eq.{usuario['id']}", "ativo": "eq.true"},
        token=token,
    )
    corretor = _primeiro(equipe)
    if not corretor:
        raise CRMErro("Este usuario nao faz parte da equipe ativa.")
    return corretor


def contexto_autenticado(token: str, lead_id: str, *, limite: int = 20) -> tuple[dict, list]:
    validar_corretor(token)
    leads = _rest(
        "GET", "leads", params={"select": "*", "id": f"eq.{lead_id}", "limit": "1"}, token=token
    )
    lead = _primeiro(leads)
    if not lead:
        raise CRMErro("Lead nao encontrado.")
    itens = _rest(
        "GET",
        "lead_interacoes",
        params={
            "select": "direcao,autor,conteudo,criado_em",
            "lead_id": f"eq.{lead_id}",
            "tipo": "eq.mensagem",
            "order": "criado_em.desc",
            "limit": str(limite),
        },
        token=token,
    )
    historico = [
        {
            "role": "assistant" if item.get("direcao") == "saida" else "user",
            "content": item.get("conteudo", ""),
        }
        for item in reversed(itens or [])
    ]
    if not historico and lead.get("mensagem"):
        historico.append({"role": "user", "content": lead["mensagem"]})
    return lead, historico
