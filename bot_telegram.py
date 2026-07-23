"""Bot de Telegram que atende leads com o mesmo agente da plataforma.

O lead conversa direto no Telegram; usa o mesmo cérebro do chat web
(core.agent + agents.yaml). Quando o agente fecha o RESUMO, ele é encaminhado
para a equipe (core.leads). Funciona por long polling — não precisa de servidor
com URL pública, roda em qualquer PC ou host gratuito.

Configuração por variáveis de ambiente:
  TELEGRAM_BOT_TOKEN  (obrigatória)  token do bot criado no @BotFather
  GROQ_API_KEY        (obrigatória)  chave da Groq (console.groq.com/keys)
  TELEGRAM_AGENTE     (opcional)     agente do agents.yaml (padrão: atendimento)
  TELEGRAM_CHAT_ID    (opcional)     chat da equipe que recebe os resumos
  TELEGRAM_NOME       (opcional)     nome do profissional (placeholders do prompt)

Rodar:  python bot_telegram.py
"""

import os
import sys
import time
from pathlib import Path

import requests

from core import agent, config, leads

API = "https://api.telegram.org/bot{token}/{metodo}"

SECRETS_TOML = Path(__file__).parent / ".streamlit" / "secrets.toml"


def _carregar_secrets_toml() -> None:
    """Copia as chaves do .streamlit/secrets.toml para o ambiente (mesma fonte
    de configuração do site). Só define o que ainda não veio como variável de
    ambiente, então variáveis explícitas continuam tendo prioridade."""
    if not SECRETS_TOML.exists():
        return
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # backport para Python <= 3.10
        except ModuleNotFoundError:
            print("Aviso: sem tomllib/tomli; use variáveis de ambiente.")
            return
    try:
        with open(SECRETS_TOML, "rb") as f:
            dados = tomllib.load(f)
    except Exception as e:
        print("Aviso: não consegui ler secrets.toml:", e)
        return
    for chave, valor in dados.items():
        if isinstance(valor, str):
            os.environ.setdefault(chave, valor)

BOAS_VINDAS = (
    "Olá! Sou o atendimento virtual por aqui. Me conta o que você procura "
    "que eu já te ajudo."
)


def _obrigatoria(nome: str) -> str:
    valor = os.environ.get(nome, "").strip()
    if not valor:
        sys.exit(f"Defina a variável de ambiente {nome} antes de rodar o bot.")
    return valor


def _personalizar(texto: str, nome: str) -> str:
    return texto.replace("[NOME DO CORRETOR]", nome).replace("[NOME]", nome)


def _chamar(token: str, metodo: str, **params):
    r = requests.post(API.format(token=token, metodo=metodo), json=params, timeout=40)
    return r.json()


def _enviar(token: str, chat_id, texto: str) -> None:
    try:
        _chamar(token, "sendMessage", chat_id=chat_id, text=texto)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)


def main() -> None:
    _carregar_secrets_toml()
    token = _obrigatoria("TELEGRAM_BOT_TOKEN")
    api_key = _obrigatoria("GROQ_API_KEY")

    nome_agente = os.environ.get("TELEGRAM_AGENTE", "atendimento").strip()
    nome_prof = os.environ.get("TELEGRAM_NOME", "").strip()

    agentes = config.carregar_agentes()
    if nome_agente not in agentes:
        sys.exit(
            f"Agente '{nome_agente}' não existe em agents.yaml. "
            f"Opções: {', '.join(agentes) or 'nenhuma'}"
        )

    cfg = dict(agentes[nome_agente])
    if nome_prof:
        cfg["prompt"] = _personalizar(cfg.get("prompt", ""), nome_prof)

    historicos: dict[int, list] = {}   # chat_id -> histórico de mensagens
    resumos_enviados: set = set()      # (chat_id, hash) já encaminhados à equipe

    print(f"Bot no ar como agente '{nome_agente}'. Ctrl+C para parar.")
    offset = None
    while True:
        try:
            resp = _chamar(token, "getUpdates", offset=offset, timeout=30)
        except Exception as e:
            print("Erro no getUpdates:", e)
            time.sleep(3)
            continue

        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message") or {}
            chat_id = (msg.get("chat") or {}).get("id")
            texto = (msg.get("text") or "").strip()
            if not chat_id or not texto:
                continue

            if texto.lower() in ("/start", "/reset"):
                historicos[chat_id] = []
                _enviar(token, chat_id, BOAS_VINDAS)
                continue

            historico = historicos.setdefault(chat_id, [])
            historico.append({"role": "user", "content": texto})

            try:
                resposta = agent.responder(api_key, cfg, historico)
            except Exception as e:
                print("Erro no agente:", e)
                historico.pop()  # não trava o histórico com a pergunta sem resposta
                _enviar(
                    token,
                    chat_id,
                    "Tive um probleminha aqui. Pode mandar de novo, por favor?",
                )
                continue

            historico.append({"role": "assistant", "content": resposta})
            _enviar(token, chat_id, resposta)

            resumo = leads.extrair_resumo(resposta)
            if resumo:
                chave = (chat_id, hash(resumo))
                if chave not in resumos_enviados and leads.enviar_lead(nome_agente, resumo):
                    resumos_enviados.add(chave)


if __name__ == "__main__":
    main()
