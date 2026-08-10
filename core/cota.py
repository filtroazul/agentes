"""Contabilidade da cota diária do Groq, por modelo, com alarme no Telegram.

POR QUE ISTO EXISTE
-------------------
O plano grátis do Groq tem teto de TOKENS POR DIA, e ele é **por modelo**, não
da conta inteira (conferido em 11/08/2026: o 429 nomeia o modelo, e o cabeçalho
`x-ratelimit-limit-requests` devolve 14.400 pro llama-3.1-8b contra 1.000 pro
llama-3.3-70b). Quando o teto estoura, o cliente lê "Tive um probleminha aqui"
— que é exatamente o que um lead pago do Meta Ads veria.

⚠️ Os cabeçalhos `x-ratelimit-*` que a API devolve são do balde por MINUTO, não
do diário. O diário só aparece na mensagem do 429, quando já é tarde. Por isso
aqui a contagem é nossa: somamos `usage.total_tokens` de cada resposta.

O arquivo de contagem é best-effort. Se sumir (redeploy do Streamlit Cloud
zera o disco), o pior que acontece é o alarme atrasar um dia — a cadeia de
reserva do agent.py continua protegendo o cliente de qualquer jeito.
"""

import json
import os
import threading
from datetime import date
from pathlib import Path

# Tetos de tokens/dia do plano grátis (console.groq.com/docs/rate-limits,
# conferido em 11/08/2026). Modelo fora desta tabela não é contabilizado.
TETO_DIARIO = {
    "llama-3.3-70b-versatile": 100_000,
    "openai/gpt-oss-120b": 200_000,
    "openai/gpt-oss-20b": 200_000,
    "llama-3.1-8b-instant": 500_000,
}

# A partir de quanto do teto avisar. 0.8 dá margem pra reagir antes de cair.
LIMIAR_ALARME = 0.8

ARQUIVO = Path(
    os.environ.get("COTA_ARQUIVO", Path(__file__).resolve().parent.parent / ".cota-groq.json")
)

_trava = threading.Lock()


def _ler() -> dict:
    try:
        dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except Exception:
        return {}
    # Vira o dia: o que é de ontem não interessa.
    return dados if dados.get("dia") == date.today().isoformat() else {}


def _gravar(dados: dict) -> None:
    try:
        ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass  # disco somente-leitura: seguimos sem contabilidade


def registrar(modelo: str, tokens: int) -> None:
    """Soma o consumo do modelo no dia e alerta ao cruzar o limiar.

    Alerta UMA vez por modelo por dia — alarme que repete vira ruído e
    para de ser lido.
    """
    teto = TETO_DIARIO.get(modelo)
    if not teto or tokens <= 0:
        return

    with _trava:
        dados = _ler()
        dados["dia"] = date.today().isoformat()
        usados = dados.setdefault("modelos", {})
        antes = int(usados.get(modelo, 0))
        depois = antes + int(tokens)
        usados[modelo] = depois
        avisados = dados.setdefault("avisados", [])
        cruzou = (
            antes < teto * LIMIAR_ALARME <= depois and modelo not in avisados
        )
        if cruzou:
            avisados.append(modelo)
        _gravar(dados)

    if cruzou:
        _avisar(
            f"⚠️ COTA DO GROQ\n\n"
            f"O modelo {modelo} passou de {int(LIMIAR_ALARME * 100)}% do teto de hoje.\n"
            f"Usados: {depois:,} de {teto:,} tokens.\n\n"
            f"Quando acabar, os agentes caem automaticamente pro próximo modelo "
            f"da cadeia — o atendimento não para, mas a qualidade muda."
            .replace(",", ".")
        )


def avisar_queda(modelo_caiu: str, modelo_novo: str, agente: str) -> None:
    """Chamado quando um modelo estoura e a cadeia de reserva assume."""
    _avisar(
        f"🔻 COTA ESTOURADA\n\n"
        f"O modelo {modelo_caiu} bateu o teto do dia.\n"
        f"O agente '{agente}' está respondendo com {modelo_novo}.\n\n"
        f"Ninguém ficou sem resposta, mas vale conferir se as respostas "
        f"continuam boas."
    )


def _avisar(texto: str) -> None:
    """Manda o aviso pro mesmo Telegram dos leads. Nunca levanta exceção:
    alarme quebrado não pode derrubar o atendimento."""
    try:
        import requests

        from core.leads import _secret

        token = _secret("TELEGRAM_BOT_TOKEN")
        chat = _secret("TELEGRAM_CHAT_ID_ALERTAS") or _secret("TELEGRAM_CHAT_ID")
        if not token or not chat:
            print(f"[cota] {texto}")
            return
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": texto},
            timeout=8,
        )
    except Exception as e:
        print(f"[cota] falhou o aviso ({e}): {texto}")


def situacao() -> dict:
    """Quanto foi usado hoje, por modelo. Para inspeção manual."""
    dados = _ler()
    usados = dados.get("modelos", {})
    return {
        modelo: {
            "usados": int(usados.get(modelo, 0)),
            "teto": teto,
            "porcento": round(100 * int(usados.get(modelo, 0)) / teto, 1),
        }
        for modelo, teto in TETO_DIARIO.items()
    }
