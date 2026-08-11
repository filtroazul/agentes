"""Credenciais do painel da Ah Imobiliaria, fora do codigo.

Os gravadores de tutorial (`gravar-tutorial-*.py`) precisam logar DE VERDADE
pra gravar o video: e o login real que grava a sessao no localStorage, e sem
ela o botao "Painel" nao apareceria na gravacao. Ou seja, alguem tem que saber
a senha.

O que nao pode e ela morar dentro de um `.py`. Este repositorio e publico, e
senha em arquivo versionado nao sai mais do historico do git depois que sobe —
trocar o arquivo num commit seguinte nao apaga nada, o valor continua la em
`git show` de qualquer commit anterior. Por isso a senha vive em

    vendas/.credenciais-ah.json     ->  {"email": "...", "senha": "..."}

que o .gitignore barra. As variaveis de ambiente AH_PAINEL_EMAIL e
AH_PAINEL_SENHA tem prioridade, e sao o caminho pra rodar isto em outra
maquina sem criar arquivo nenhum.
"""

import json
import os
import pathlib

ARQUIVO = pathlib.Path(__file__).resolve().parent / ".credenciais-ah.json"


def credenciais():
    """Devolve (email, senha) do corretor, ou morre com instrucao no lugar."""
    email = os.environ.get("AH_PAINEL_EMAIL")
    senha = os.environ.get("AH_PAINEL_SENHA")
    if email and senha:
        return email, senha

    if not ARQUIVO.exists():
        raise SystemExit(
            "Faltam as credenciais do painel da Ah Imobiliaria.\n\n"
            f"Crie {ARQUIVO}\ncom o conteudo:\n\n"
            '    {"email": "...", "senha": "..."}\n\n'
            "ou defina AH_PAINEL_EMAIL e AH_PAINEL_SENHA no ambiente.\n"
            "O arquivo e barrado pelo .gitignore de proposito: NAO versione."
        )

    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    return dados["email"], dados["senha"]
