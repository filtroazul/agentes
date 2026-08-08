"""Ferramentas que os agentes podem usar.

Para adicionar uma ferramenta nova:
1. Escreva a função Python.
2. Registre-a em FERRAMENTAS com nome, descrição e schema dos parâmetros.
3. Adicione o nome dela na lista `ferramentas` do agente em agents.yaml.
"""

import ast
import operator
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# --- implementações -----------------------------------------------------

_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _avaliar(no):
    """Avalia com segurança uma expressão matemática (sem eval)."""
    if isinstance(no, ast.Expression):
        return _avaliar(no.body)
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, ast.BinOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.left), _avaliar(no.right))
    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.operand))
    raise ValueError("Expressão não permitida")


def calculadora(expressao: str) -> str:
    """Calcula uma expressão matemática, ex: '2 * (3 + 4)'."""
    try:
        resultado = _avaliar(ast.parse(expressao, mode="eval"))
        return str(resultado)
    except Exception as e:
        return f"Erro ao calcular '{expressao}': {e}"


def data_hora() -> str:
    """Retorna a data e hora atual no fuso de Brasília."""
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    return agora.strftime("%d/%m/%Y %H:%M:%S (horário de Brasília)")


_SEGREDOS = None


def _segredo(nome: str) -> str:
    """Lê uma chave do ambiente e, se não achar, do .streamlit/secrets.toml.

    O import de tomllib fica aqui dentro de propósito: a VM da Oracle roda
    Python 3.10, que não tem esse módulo. Lá as chaves vêm por variável de
    ambiente e o fallback nunca é acionado.
    """
    valor = os.environ.get(nome)
    if valor:
        return valor

    global _SEGREDOS
    if _SEGREDOS is None:
        _SEGREDOS = {}
        try:
            import tomllib

            caminho = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
            if caminho.exists():
                with open(caminho, "rb") as f:
                    _SEGREDOS = tomllib.load(f)
        except Exception:
            _SEGREDOS = {}

    return str(_SEGREDOS.get(nome, ""))


def buscar_imoveis(
    finalidade: str = "",
    tipo: str = "",
    bairro: str = "",
    preco_max: float = 0,
    quartos_min: int = 0,
) -> str:
    """Consulta a carteira real da imobiliária no Supabase.

    Chama a RPC buscar_imoveis, que roda com as permissões do visitante
    anônimo: só devolve o que está publicado. Rascunho, vendido e alugado
    não vazam para o agente nem por acidente.
    """
    url = _segredo("SUPABASE_URL").rstrip("/")
    chave = _segredo("SUPABASE_ANON_KEY")
    if not url or not chave:
        return (
            "Catálogo indisponível: faltam SUPABASE_URL e SUPABASE_ANON_KEY. "
            "Não invente imóveis; diga que o corretor confirma a disponibilidade."
        )

    corpo = {"p_limite": 5}
    if finalidade in ("venda", "aluguel"):
        corpo["p_finalidade"] = finalidade
    if tipo:
        corpo["p_tipo"] = tipo
    if bairro:
        corpo["p_bairro"] = bairro
    if preco_max and float(preco_max) > 0:
        corpo["p_preco_max"] = float(preco_max)
    if quartos_min and int(quartos_min) > 0:
        corpo["p_quartos_min"] = int(quartos_min)

    try:
        resposta = requests.post(
            f"{url}/rest/v1/rpc/buscar_imoveis",
            headers={
                "apikey": chave,
                "Authorization": f"Bearer {chave}",
                "Content-Type": "application/json",
            },
            json=corpo,
            timeout=10,
        )
        resposta.raise_for_status()
        achados = resposta.json()
    except Exception as e:
        return (
            f"Não consegui consultar o catálogo agora ({e}). "
            "Não invente imóveis; diga que o corretor confirma as opções."
        )

    if not achados:
        return (
            "Nenhum imóvel publicado bate com esse perfil no momento. "
            "Ofereça avisar quando entrar algo parecido."
        )

    linhas = []
    for im in achados:
        preco = f"R$ {im['preco']:,.0f}".replace(",", ".")
        if im.get("preco") and finalidade == "aluguel":
            preco += "/mês"

        detalhes = []
        if im.get("quartos"):
            detalhes.append(f"{im['quartos']} quartos")
        if im.get("banheiros"):
            detalhes.append(f"{im['banheiros']} banheiros")
        if im.get("vagas"):
            detalhes.append(f"{im['vagas']} vagas")
        if im.get("area_util"):
            detalhes.append(f"{float(im['area_util']):.0f} m²")

        linhas.append(
            f"- Cód {im['codigo']} | {im['titulo']} | {im['bairro']}, {im['cidade']} "
            f"| {preco}" + (f" | {', '.join(detalhes)}" if detalhes else "")
        )

    return f"{len(achados)} imóvel(is) na carteira:\n" + "\n".join(linhas)


# --- registro -----------------------------------------------------------

FERRAMENTAS = {
    "calculadora": {
        "funcao": lambda args: calculadora(args.get("expressao", "")),
        "schema": {
            "type": "function",
            "function": {
                "name": "calculadora",
                "description": "Calcula uma expressão matemática. Ex: '2 * (3 + 4)'",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expressao": {
                            "type": "string",
                            "description": "Expressão matemática a calcular",
                        }
                    },
                    "required": ["expressao"],
                },
            },
        },
    },
    "data_hora": {
        "funcao": lambda args: data_hora(),
        "schema": {
            "type": "function",
            "function": {
                "name": "data_hora",
                "description": "Retorna a data e hora atual no horário de Brasília",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "buscar_imoveis": {
        "funcao": lambda args: buscar_imoveis(
            finalidade=args.get("finalidade", ""),
            tipo=args.get("tipo", ""),
            bairro=args.get("bairro", ""),
            preco_max=args.get("preco_max", 0),
            quartos_min=args.get("quartos_min", 0),
        ),
        "schema": {
            "type": "function",
            "function": {
                "name": "buscar_imoveis",
                "description": (
                    "Consulta os imóveis publicados da imobiliária. Use sempre que o "
                    "cliente perguntar o que tem disponível, em vez de responder de "
                    "cabeça. Passe só os filtros que o cliente já informou."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "finalidade": {
                            "type": "string",
                            "enum": ["venda", "aluguel"],
                            "description": "venda para compra, aluguel para locação",
                        },
                        "tipo": {
                            "type": "string",
                            "enum": ["casa", "apartamento", "terreno", "comercial", "rural"],
                            "description": "Tipo de imóvel procurado",
                        },
                        "bairro": {
                            "type": "string",
                            "description": "Bairro ou região de interesse",
                        },
                        "preco_max": {
                            "type": "number",
                            "description": "Teto de valor em reais. Para aluguel, valor mensal",
                        },
                        "quartos_min": {
                            "type": "integer",
                            "description": "Número mínimo de quartos",
                        },
                    },
                },
            },
        },
    },
}


def schemas_para(nomes: list[str]) -> list[dict]:
    """Retorna os schemas das ferramentas pedidas (ignora nomes desconhecidos)."""
    return [FERRAMENTAS[n]["schema"] for n in nomes if n in FERRAMENTAS]


def executar(nome: str, argumentos: dict) -> str:
    """Executa uma ferramenta pelo nome e retorna o resultado como texto."""
    if nome not in FERRAMENTAS:
        return f"Ferramenta desconhecida: {nome}"
    try:
        return FERRAMENTAS[nome]["funcao"](argumentos)
    except Exception as e:
        return f"Erro na ferramenta {nome}: {e}"
