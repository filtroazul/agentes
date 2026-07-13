# 🤖 Plataforma de Agentes de IA

Plataforma para criar e configurar agentes de IA usando modelos **gratuitos** (Groq / Llama 3.3), com interface web em Streamlit.

## Recursos

- ✅ Vários agentes, cada um com nome, prompt, modelo, temperatura e ferramentas próprias
- ✅ Configuração pela interface web ou editando `agents.yaml`
- ✅ Ferramentas (tool calling): calculadora, data/hora — fácil de adicionar novas
- ✅ 100% gratuito (free tier da Groq)

## Como rodar

### 1. Pegue sua chave gratuita da Groq

1. Acesse https://console.groq.com/keys
2. Crie uma conta (grátis) e gere uma API Key

### 2. Instale as dependências

```
pip install -r requirements.txt
```

### 3. Inicie a plataforma

```
streamlit run app.py
```

O navegador abre em `http://localhost:8501`. Cole sua chave da Groq na barra lateral e comece a conversar.

> Dica: para não digitar a chave toda vez, defina a variável de ambiente `GROQ_API_KEY`.

## Modo demo (link pro cliente)

Abrindo o app com parâmetros na URL, ele vira uma página de atendimento limpa — sem sidebar, sem configuração, direto no chat:

```
http://localhost:8501/?agente=corretor_imoveis&corretor=Ricardo%20Almeida
```

- `agente=` — qual agente abrir (obrigatório pra ativar o modo demo)
- `corretor=` — substitui `[NOME DO CORRETOR]` no prompt, sem editar o `agents.yaml`

Nesse modo a chave da API **não** é pedida ao visitante: ela vem de `st.secrets` (deploy) ou da variável de ambiente `GROQ_API_KEY` (local). O bloco "📋 RESUMO PARA O CORRETOR" é renderizado como um card destacado, fácil de printar.

## Deploy no Streamlit Community Cloud (grátis)

1. Suba o projeto num repositório do GitHub (o `.gitignore` já protege o `secrets.toml`).
2. Acesse https://share.streamlit.io → "New app" → escolha o repo, branch `main`, arquivo `app.py`.
3. Em **Advanced settings → Secrets**, cole:
   ```toml
   GROQ_API_KEY = "gsk_sua_chave"
   ```
4. Deploy. O link do cliente fica: `https://SEU-APP.streamlit.app/?agente=corretor_imoveis&corretor=Nome%20Do%20Corretor`

Para rodar local com secrets: copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha a chave.

## Como criar/configurar agentes

**Pela interface:** barra lateral → "➕ Novo agente" → depois "⚙️ Configurar agente" (prompt, modelo, temperatura, ferramentas) → Salvar.

**Pelo arquivo:** edite `agents.yaml` diretamente. Exemplo:

```yaml
agentes:
  meu_agente:
    descricao: O que esse agente faz
    modelo: llama-3.3-70b-versatile
    temperatura: 0.7
    ferramentas: [calculadora, data_hora]
    prompt: |
      Instruções e personalidade do agente aqui.
```

## Como adicionar uma ferramenta nova

Edite `core/tools.py`:

1. Escreva a função Python (ex: consultar uma API, ler um arquivo).
2. Registre no dicionário `FERRAMENTAS` com nome, descrição e schema dos parâmetros.
3. Habilite a ferramenta no agente (interface ou `agents.yaml`).

## Estrutura do projeto

```
projeto/
├── app.py             # interface web (Streamlit)
├── agents.yaml        # configuração dos agentes
├── requirements.txt
└── core/
    ├── config.py      # carrega/salva agents.yaml
    ├── agent.py       # loop do agente (modelo + ferramentas)
    └── tools.py       # ferramentas disponíveis
```
