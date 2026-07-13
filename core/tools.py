"""Ferramentas que os agentes podem usar.

Para adicionar uma ferramenta nova:
1. Escreva a função Python.
2. Registre-a em FERRAMENTAS com nome, descrição e schema dos parâmetros.
3. Adicione o nome dela na lista `ferramentas` do agente em agents.yaml.
"""

import ast
import operator
from datetime import datetime
from zoneinfo import ZoneInfo

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
