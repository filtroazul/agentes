"""Loop do agente: envia a conversa ao modelo (Groq), executa ferramentas
quando solicitado e repete até obter a resposta final."""

import json
import re

from groq import Groq

from core import tools

MAX_ITERACOES = 8  # proteção contra loops infinitos de ferramentas

# ⚠️ O llama-3.3 às vezes "chama" a ferramenta ESCREVENDO a chamada no texto da
# resposta, em vez de devolvê-la no campo `tool_calls` da API. Quando isso
# acontece, o campo vem vazio, o laço trata como resposta final e o cliente lê
# no chat uma coisa assim:
#     Anotado! <function=buscar_imoveis>{"bairro": "Meireles"}</function>
# Visto de verdade em 10/08/2026 com o agente ah_imobiliaria. O padrão abaixo
# reconhece essa forma pra que ela seja EXECUTADA como ferramenta; e o que
# sobrar dela é limpo antes de qualquer texto chegar na tela.
_FUNCAO_EM_TEXTO = re.compile(
    r"<function\s*=\s*([A-Za-z_]\w*)\s*>\s*(\{.*?\})\s*</function\s*>",
    re.DOTALL,
)


def _limpar(texto: str) -> str:
    """Tira qualquer sintaxe de chamada de ferramenta que tenha sobrado."""
    return _FUNCAO_EM_TEXTO.sub("", texto or "").strip()


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

        # Sem chamadas de ferramenta -> resposta final...
        if not msg.tool_calls:
            texto = msg.content or ""
            escritas = _FUNCAO_EM_TEXTO.findall(texto)

            # ...a menos que o modelo tenha escrito a chamada no texto. Aí ela
            # é executada de verdade e o laço continua, senão a pessoa fica sem
            # a resposta que pediu.
            if escritas and schemas:
                conversa.append({"role": "assistant", "content": _limpar(texto)})
                for nome, argumentos_json in escritas:
                    try:
                        argumentos = json.loads(argumentos_json)
                    except json.JSONDecodeError:
                        argumentos = {}
                    resultado = tools.executar(nome, argumentos)
                    # Sem `tool_calls` não existe tool_call_id, e a API recusa
                    # uma mensagem de papel "tool" sem ele. Devolvemos o
                    # resultado como contexto do usuário, que ela aceita.
                    conversa.append(
                        {
                            "role": "user",
                            "content": f"[resultado de {nome}]\n{resultado}",
                        }
                    )
                continue

            return _limpar(texto)

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
