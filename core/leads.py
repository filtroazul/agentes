"""Envio do resumo do lead para os destinos configurados (Telegram / webhook).

Compartilhado pela interface web (app.py) e pelo bot do Telegram (bot_telegram.py),
por isso não depende de Streamlit: lê a configuração de variáveis de ambiente e,
quando disponível, também de st.secrets.

Destinos (nenhum configurado = não envia, sem erro):
  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID  -> mensagem no Telegram da equipe
  LEADS_WEBHOOK_URL                      -> POST JSON (Google Sheets, Make, CRM...)
Sufixo _<AGENTE> (ex.: TELEGRAM_CHAT_ID_AIOTI) direciona por agente/cliente.
"""

import os
import re
from datetime import datetime

import requests

# Bloco de resumo que o agente emite no fim da qualificação (ver agents.yaml).
RE_RESUMO = re.compile(
    r"-{3,}\s*\n\s*((?:📋\s*)?RESUMO[^\n]*.*?)(?:\n\s*-{3,}|\Z)", re.DOTALL
)


def extrair_resumo(texto: str) -> str | None:
    """Retorna o bloco RESUMO da resposta do agente, ou None se não houver."""
    m = RE_RESUMO.search(texto)
    return m.group(1).strip() if m else None


def _secret(nome: str) -> str:
    """Valor de st.secrets (se houver app Streamlit) ou da variável de ambiente."""
    valor = ""
    try:
        import streamlit as st

        valor = st.secrets.get(nome, "")
    except Exception:  # sem Streamlit rodando / sem secrets.toml
        valor = ""
    return (valor or os.environ.get(nome, "")).strip()


def _secret_do_agente(base: str, agente: str) -> str:
    return _secret(f"{base}_{agente.upper()}") or _secret(base)


def _momento() -> str:
    try:
        from zoneinfo import ZoneInfo

        agora = datetime.now(ZoneInfo("America/Fortaleza"))
    except Exception:
        agora = datetime.now()
    return agora.strftime("%d/%m/%Y %H:%M")


def enviar_lead(agente: str, resumo: str) -> bool:
    """Envia o resumo do lead pros destinos configurados. True se algum recebeu."""
    momento = _momento()
    enviado = False

    token = _secret("TELEGRAM_BOT_TOKEN")
    chat_id = _secret_do_agente("TELEGRAM_CHAT_ID", agente)
    if token and chat_id:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": f"🔔 NOVO LEAD · {momento}\n\n{resumo}"},
                timeout=8,
            )
            enviado = enviado or r.ok
        except Exception:
            pass

    webhook = _secret_do_agente("LEADS_WEBHOOK_URL", agente)
    if webhook:
        try:
            r = requests.post(
                webhook,
                json={"agente": agente, "momento": momento, "resumo": resumo},
                timeout=8,
            )
            enviado = enviado or r.ok
        except Exception:
            pass

    return enviado
