"""Carrega e salva as configurações dos agentes (agents.yaml)."""

from pathlib import Path

import yaml

ARQUIVO_CONFIG = Path(__file__).parent.parent / "agents.yaml"

CONFIG_PADRAO = {
    "icone": "🤖",
    "descricao": "Novo agente",
    "modelo": "llama-3.3-70b-versatile",
    "temperatura": 0.7,
    "ferramentas": [],
    "prompt": "Você é um assistente útil. Responda em português do Brasil.",
}


def carregar_agentes() -> dict:
    """Retorna o dicionário de agentes definidos em agents.yaml."""
    if not ARQUIVO_CONFIG.exists():
        return {}
    with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
        dados = yaml.safe_load(f) or {}
    return dados.get("agentes", {})


def salvar_agentes(agentes: dict) -> None:
    """Grava o dicionário de agentes de volta em agents.yaml."""
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
        yaml.dump(
            {"agentes": agentes},
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
