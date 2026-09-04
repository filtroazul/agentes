"""Adaptador seguro da WhatsApp Cloud API.

Nenhum envio acontece apenas porque as credenciais existem. Para enviar é
necessário ativar WHATSAPP_AUTOMATION_ENABLED e autorizar explicitamente o
destinatário em WHATSAPP_TEST_RECIPIENTS, ou ligar WHATSAPP_ALLOW_ALL somente
depois da homologação.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any

import requests


class WhatsAppErro(RuntimeError):
    """Falha segura na configuração, validação ou chamada da Cloud API."""


def _verdadeiro(nome: str) -> bool:
    return os.environ.get(nome, "").strip().lower() in {"1", "true", "sim", "yes", "on"}


def _lista(nome: str) -> set[str]:
    return {
        "".join(c for c in item if c.isdigit())
        for item in os.environ.get(nome, "").split(",")
        if "".join(c for c in item if c.isdigit())
    }


def configurado() -> bool:
    return bool(
        os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()
        and os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    )


def ativo() -> bool:
    return configurado() and _verdadeiro("WHATSAPP_AUTOMATION_ENABLED")


def remetente_permitido(wa_id: str) -> bool:
    numero = "".join(c for c in str(wa_id) if c.isdigit())
    return bool(numero) and (
        numero in _lista("WHATSAPP_TEST_RECIPIENTS")
        or _verdadeiro("WHATSAPP_ALLOW_ALL")
    )


def modo_teste(wa_id: str) -> bool:
    """Indica que o numero esta na allowlist e o atendimento geral segue fechado."""
    numero = "".join(c for c in str(wa_id) if c.isdigit())
    return bool(numero) and numero in _lista("WHATSAPP_TEST_RECIPIENTS") and not _verdadeiro(
        "WHATSAPP_ALLOW_ALL"
    )


def assinatura_valida(corpo: bytes, assinatura: str) -> bool:
    segredo = (
        os.environ.get("WHATSAPP_APP_SECRET", "").strip()
        or os.environ.get("META_APP_SECRET", "").strip()
    )
    if not segredo or not assinatura.startswith("sha256="):
        return False
    esperada = "sha256=" + hmac.new(segredo.encode(), corpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(assinatura, esperada)


def extrair_mensagens(payload: dict[str, Any]) -> list[dict[str, str]]:
    if payload.get("object") != "whatsapp_business_account":
        return []
    resultado = []
    for entrada in payload.get("entry", []):
        if not isinstance(entrada, dict):
            continue
        for mudanca in entrada.get("changes", []):
            if not isinstance(mudanca, dict) or mudanca.get("field") != "messages":
                continue
            valor = mudanca.get("value") or {}
            metadata = valor.get("metadata") or {}
            contatos = {
                str(item.get("wa_id")): str((item.get("profile") or {}).get("name") or "").strip()
                for item in valor.get("contacts", [])
                if isinstance(item, dict) and item.get("wa_id")
            }
            for mensagem in valor.get("messages", []):
                if not isinstance(mensagem, dict):
                    continue
                tipo = mensagem.get("type")
                texto = ""
                if tipo == "text":
                    texto = str((mensagem.get("text") or {}).get("body") or "").strip()
                elif tipo == "button":
                    texto = str((mensagem.get("button") or {}).get("text") or "").strip()
                elif tipo == "interactive":
                    interativo = mensagem.get("interactive") or {}
                    resposta = interativo.get("button_reply") or interativo.get("list_reply") or {}
                    texto = str(resposta.get("title") or resposta.get("id") or "").strip()
                remetente = "".join(c for c in str(mensagem.get("from") or "") if c.isdigit())
                identificador = str(mensagem.get("id") or "").strip()
                if remetente and identificador:
                    resultado.append(
                        {
                            "id": identificador,
                            "de": remetente,
                            "nome": contatos.get(remetente, ""),
                            "texto": texto,
                            "tipo": str(tipo or "unknown"),
                            "phone_number_id": str(metadata.get("phone_number_id") or ""),
                        }
                    )
    return resultado


def enviar_texto(destinatario: str, texto: str) -> str:
    numero = "".join(c for c in str(destinatario) if c.isdigit())
    if not ativo():
        raise WhatsAppErro("Automacao do WhatsApp esta desligada.")
    if not remetente_permitido(numero):
        raise WhatsAppErro("Destinatario fora da lista autorizada para teste.")
    token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    versao = os.environ.get(
        "WHATSAPP_GRAPH_API_VERSION",
        os.environ.get("META_GRAPH_API_VERSION", "v26.0"),
    ).strip()
    try:
        resposta = requests.post(
            f"https://graph.facebook.com/{versao}/{phone_id}/messages",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {"preview_url": False, "body": texto[:4096]},
            },
            timeout=20,
        )
    except requests.RequestException as erro:
        raise WhatsAppErro("A Cloud API nao respondeu a tempo.") from erro
    if not resposta.ok:
        raise WhatsAppErro(f"A Cloud API recusou o envio (HTTP {resposta.status_code}).")
    try:
        identificador = str((resposta.json().get("messages") or [{}])[0].get("id") or "")
    except (ValueError, AttributeError, IndexError):
        identificador = ""
    if not identificador:
        raise WhatsAppErro("A Cloud API nao confirmou o identificador da mensagem.")
    return identificador
