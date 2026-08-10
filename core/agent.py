"""Loop do agente: envia a conversa ao modelo (Groq), executa ferramentas
quando solicitado e repete até obter a resposta final."""

import json
import re

from groq import BadRequestError, Groq, RateLimitError

from core import cota, tools

MAX_ITERACOES = 8  # proteção contra loops infinitos de ferramentas

# Ordem de queda quando o teto DIÁRIO de um modelo estoura. Os tetos do plano
# grátis são por modelo (100k/200k/200k/500k tokens por dia), então trocar de
# modelo é cota nova de verdade — e é o que os termos do Groq permitem, ao
# contrário de abrir uma segunda conta.
#
# ⚠️ A ordem saiu de MEDIÇÃO, não de tamanho de modelo. Eu tinha assumido
# "maior = melhor" e estava errado: numa bateria com o prompt do ah_imobiliaria
# (11/08/2026, catálogo vazio), o gpt-oss-120b foi o PIOR dos três — respondeu
# "Qual é seu nome?" a quem pediu apartamento de 2 quartos até 300 mil,
# ignorando a pergunta inteira. O llama-3.1-8b foi o único que respondeu as
# três perguntas empilhadas de "tem casa no Montese? aceita financiamento?
# qual o valor?", que é o teste mais duro do prompt.
#
# O 8b vem em segundo também por cota: 500 mil tokens/dia contra 200 mil dos
# gpt-oss, ou seja, é ele que aguenta o tranco por mais tempo.
#
# ⚠️ Ressalva honesta: foram 4 perguntas, uma rodada cada, e o llama-3.3-70b
# estava com a cota estourada e NÃO entrou na comparação. Se for mover agente
# de modelo pra valer, refazer a bateria com mais volume.
CADEIA_RESERVA = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]


def _cadeia(modelo_do_agente: str) -> list[str]:
    """O modelo do agente primeiro, depois as reservas que sobrarem."""
    return [modelo_do_agente] + [m for m in CADEIA_RESERVA if m != modelo_do_agente]

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


def _geracao_recusada(erro: BadRequestError) -> str | None:
    """Extrai o `failed_generation` de um 400 `tool_use_failed`, se for isso.

    ⚠️ Este é um erro do SERVIDOR do Groq, não nosso: eles validam os argumentos
    da ferramenta contra o schema antes de nos entregar qualquer coisa. Se o
    modelo mandar `"quartos_min": "3"` (string) num campo integer, o request
    INTEIRO volta 400 e o cliente lê "assistente temporariamente indisponível".
    Visto de verdade em 11/08/2026 no ah_imobiliaria, no meio de uma conversa
    que já estava funcionando — é intermitente, depende do humor do modelo.

    Os schemas já aceitam tipo-união pra evitar a causa comum. Isto aqui é a
    rede embaixo: o texto recusado ainda contém a chamada que o modelo queria
    fazer, então dá pra executá-la em vez de perder a conversa.
    """
    corpo = getattr(erro, "body", None)
    if not isinstance(corpo, dict):
        return None
    detalhe = corpo.get("error")
    if not isinstance(detalhe, dict) or detalhe.get("code") != "tool_use_failed":
        return None
    gerado = detalhe.get("failed_generation")
    return gerado if isinstance(gerado, str) else None


def _e_teto_diario(erro: RateLimitError) -> bool:
    """O 429 é do teto do DIA (TPD) ou só do balde do minuto (TPM)?

    Os dois viram fallback — numa conversa ao vivo ninguém espera um minuto —
    mas só o diário merece alarme: o do minuto se resolve sozinho.
    """
    return "per day" in str(erro).lower()


def _chamar(client, cadeia, atual, conversa, schemas, config_agente, nome_agente):
    """Chama o modelo, caindo pro próximo da cadeia quando a cota estoura.

    Devolve (resposta, índice do modelo que respondeu) — o índice volta pro
    chamador pra que as próximas iterações já comecem do modelo que funciona.
    """
    ultimo_erro = None
    while atual < len(cadeia):
        modelo = cadeia[atual]
        try:
            resposta = client.chat.completions.create(
                model=modelo,
                messages=conversa,
                temperature=float(config_agente.get("temperatura", 0.7)),
                tools=schemas or None,
                tool_choice="auto" if schemas else None,
                max_tokens=2048,
            )
        except RateLimitError as erro:
            ultimo_erro = erro
            diario = _e_teto_diario(erro)
            proximo = cadeia[atual + 1] if atual + 1 < len(cadeia) else None
            if proximo and diario:
                cota.avisar_queda(modelo, proximo, nome_agente)
            atual += 1
            continue

        uso = getattr(resposta, "usage", None)
        if uso is not None:
            cota.registrar(modelo, getattr(uso, "total_tokens", 0) or 0)
        return resposta, atual

    # Acabou a cadeia: todos os modelos estourados. Deixa o erro subir — quem
    # chama já sabe mostrar uma mensagem decente pro cliente.
    raise ultimo_erro


def responder(api_key: str, config_agente: dict, mensagens: list[dict]) -> str:
    """Roda uma rodada completa do agente e retorna o texto final.

    `mensagens` é o histórico no formato [{"role": "user"|"assistant", "content": str}, ...]
    `config_agente` vem do agents.yaml (modelo, prompt, temperatura, ferramentas).
    """
    client = Groq(api_key=api_key)

    nome_agente = config_agente.get("titulo_demo") or config_agente.get("descricao", "?")
    cadeia = _cadeia(config_agente.get("modelo", "llama-3.3-70b-versatile"))
    # Índice na cadeia. Fica FORA do laço de propósito: uma vez que o modelo
    # caiu por cota, ele segue caído pelo resto desta resposta — voltar a
    # tentá-lo a cada iteração só gastaria 429 e tempo.
    atual = 0

    schemas = tools.schemas_para(config_agente.get("ferramentas", []))
    conversa = [{"role": "system", "content": config_agente["prompt"]}] + list(mensagens)

    def executar_do_texto(texto: str, escritas: list[tuple[str, str]]) -> None:
        """Roda as chamadas que o modelo escreveu no texto e alimenta a conversa."""
        conversa.append({"role": "assistant", "content": _limpar(texto)})
        for nome, argumentos_json in escritas:
            try:
                argumentos = json.loads(argumentos_json)
            except json.JSONDecodeError:
                argumentos = {}
            resultado = tools.executar(nome, argumentos)
            # Sem `tool_calls` não existe tool_call_id, e a API recusa uma
            # mensagem de papel "tool" sem ele. Devolvemos o resultado como
            # contexto do usuário, que ela aceita.
            conversa.append(
                {"role": "user", "content": f"[resultado de {nome}]\n{resultado}"}
            )

    for _ in range(MAX_ITERACOES):
        try:
            resposta, atual = _chamar(
                client, cadeia, atual, conversa, schemas, config_agente, nome_agente
            )
        except BadRequestError as erro:
            recusado = _geracao_recusada(erro)
            escritas = _FUNCAO_EM_TEXTO.findall(recusado or "")
            if not escritas:
                raise
            # O Groq rejeitou o formato, mas a intenção do modelo está legível.
            executar_do_texto(recusado, escritas)
            continue

        msg = resposta.choices[0].message

        # Sem chamadas de ferramenta -> resposta final...
        if not msg.tool_calls:
            texto = msg.content or ""
            escritas = _FUNCAO_EM_TEXTO.findall(texto)

            # ...a menos que o modelo tenha escrito a chamada no texto. Aí ela
            # é executada de verdade e o laço continua, senão a pessoa fica sem
            # a resposta que pediu.
            if escritas and schemas:
                executar_do_texto(texto, escritas)
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
