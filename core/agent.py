"""Loop do agente: envia a conversa ao modelo (Groq), executa ferramentas
quando solicitado e repete até obter a resposta final."""

import json

from groq import Groq

from core import tools

MAX_ITERACOES = 8  # proteção contra loops infinitos de ferramentas


def responder(api_key: str, config_agente: dict, mensagens: list[dict]) -> str:
    """Roda uma rodada completa do agente e retorna o texto final.

    `mensagens` é o histórico no formato [{"role": "user"|"assistant", "content": str}, ...]
    `config_agente` vem do agents.yaml (modelo, prompt, temperatura, ferramentas).
    """
    client = Groq(api_key=api_key)

    schemas = tools.schemas_para(config_agente.get("ferramentas", []))
    conversa = [{"role": "system", "content": config_agente["prompt"]}] + list(mensagens)

    for _ in range(MAX_ITERACOES):
        resposta = client.chat.completions.create(
            model=config_agente.get("modelo", "llama-3.3-70b-versatile"),
            messages=conversa,
            temperature=float(config_agente.get("temperatura", 0.7)),
            tools=schemas or None,
            tool_choice="auto" if schemas else None,
            max_tokens=2048,
        )
        msg = resposta.choices[0].message

        # Sem chamadas de ferramenta -> resposta final
        if not msg.tool_calls:
            return msg.content or ""

        # Registra a intenção do assistente e executa cada ferramenta
        conversa.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            }
        )
        for tc in msg.tool_calls:
            try:
                argumentos = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                argumentos = {}
            resultado = tools.executar(tc.function.name, argumentos)
            conversa.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": resultado,
                }
            )

    return "O agente atingiu o limite de passos sem concluir. Tente reformular o pedido."
