"""Plataforma de Agentes de IA — interface web (Streamlit).

Rodar com:  streamlit run app.py
"""

import html
import os
import re

import streamlit as st

from core import agent, config, tools

# --- modo demo (link pro cliente) vs modo admin -------------------------------
# ?agente=corretor_imoveis  -> abre direto no chat, sem sidebar de administração
# &corretor=Fulano          -> personaliza o nome do corretor sem editar o yaml

_params = st.query_params
MODO_DEMO = "agente" in _params
AGENTE_DEMO = _params.get("agente", "")
NOME_CORRETOR = (_params.get("corretor", "") or "").strip() or "Ricardo Almeida"

st.set_page_config(
    page_title="Assistente Imobiliário" if MODO_DEMO else "Plataforma de Agentes",
    page_icon="🏠" if MODO_DEMO else "✦",
    layout="centered" if MODO_DEMO else "wide",
    initial_sidebar_state="collapsed" if MODO_DEMO else "auto",
)


def obter_api_key_configurada() -> str:
    """Chave do deploy (st.secrets) ou do ambiente local (GROQ_API_KEY)."""
    try:
        chave = st.secrets.get("GROQ_API_KEY", "")
    except Exception:  # sem secrets.toml configurado
        chave = ""
    return chave or os.environ.get("GROQ_API_KEY", "")

MODELOS_DISPONIVEIS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b",
]

ICONES = ["🤖", "🏠", "📊", "🔎", "✍️", "🧠", "💼", "🛠️", "🌐", "📚"]

# --- estilo ---------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Sora', sans-serif !important; letter-spacing: -0.5px; }

    /* barra lateral */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #14181F 0%, #0F1115 100%);
        border-right: 1px solid #262B35;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.35rem;
        background: linear-gradient(90deg, #E8985E, #E5C07B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* cartão do agente */
    .agent-card {
        background: linear-gradient(135deg, #1B202A 0%, #171B22 100%);
        border: 1px solid #2A3040;
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .agent-card .nome {
        font-family: 'Sora', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #F3EFE6;
    }
    .agent-card .desc { color: #9BA3B2; margin-top: 2px; }

    /* chips de metadados */
    .chip {
        display: inline-block;
        padding: 3px 12px;
        margin: 8px 6px 0 0;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid #3A4152;
        color: #C9CFDB;
        background: #202634;
    }
    .chip.accent { border-color: #7A5636; color: #E8985E; background: #241C14; }

    /* mensagens do chat */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        border: 1px solid #232935;
        background: #151922;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.4rem;
    }

    /* input do chat */
    [data-testid="stChatInput"] textarea { font-family: 'IBM Plex Sans', sans-serif; }
    [data-testid="stChatInput"] {
        border-radius: 14px;
        border: 1px solid #2A3040;
    }

    /* botões */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #3A4152;
        transition: all .15s ease;
    }
    .stButton > button:hover {
        border-color: #E8985E;
        color: #E8985E;
    }

    /* card do resumo pro corretor (print de venda) */
    .resumo-card {
        background: linear-gradient(135deg, #14261C 0%, #101D16 100%);
        border: 1px solid #3E9C6B;
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin: 0.6rem 0;
        line-height: 1.9;
        color: #DFF5E8;
        box-shadow: 0 4px 20px rgba(62, 156, 107, 0.18);
    }
    .resumo-card .titulo {
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: #6FD79E;
        display: block;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid #2A4A38;
        padding-bottom: 0.4rem;
    }

    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

if MODO_DEMO:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- renderização de mensagens -------------------------------------------------

RE_RESUMO = re.compile(
    r"-{3,}\s*\n\s*(📋\s*RESUMO PARA O CORRETOR.*?)(?:\n\s*-{3,}|\Z)", re.DOTALL
)


def renderizar_mensagem(texto: str) -> None:
    """Markdown normal, mas o bloco 📋 RESUMO vira um card destacado."""
    m = RE_RESUMO.search(texto)
    if not m:
        st.markdown(texto)
        return

    antes = texto[: m.start()].strip()
    if antes:
        st.markdown(antes)

    linhas = [l.strip() for l in m.group(1).strip().splitlines() if l.strip()]
    titulo = html.escape(linhas[0]) if linhas else "📋 RESUMO PARA O CORRETOR"
    corpo = "<br>".join(html.escape(l) for l in linhas[1:])
    st.markdown(
        f'<div class="resumo-card"><span class="titulo">{titulo}</span>{corpo}</div>',
        unsafe_allow_html=True,
    )

    depois = texto[m.end() :].strip().lstrip("-").strip()
    if depois:
        st.markdown(depois)

# --- estado -----------------------------------------------------------------

if "agentes" not in st.session_state:
    st.session_state.agentes = config.carregar_agentes()
if "historicos" not in st.session_state:
    st.session_state.historicos = {}  # nome do agente -> lista de mensagens

agentes = st.session_state.agentes

# --- modo demo: direto no chat, sem administração ------------------------------

if MODO_DEMO:
    if AGENTE_DEMO not in agentes:
        st.error("Assistente não encontrado. Confira o link recebido.")
        st.stop()
    selecionado = AGENTE_DEMO
    api_key = obter_api_key_configurada()

# --- barra lateral (modo admin): chave, seleção e configuração -----------------

if not MODO_DEMO:
  with st.sidebar:
    st.title("✦ Plataforma de Agentes")

    api_key = st.text_input(
        "Chave da API Groq",
        value=obter_api_key_configurada(),
        type="password",
        help="Crie uma chave gratuita em https://console.groq.com/keys",
    )

    st.divider()

    nomes = list(agentes.keys())
    if not nomes:
        st.warning("Nenhum agente configurado. Crie um abaixo.")
        selecionado = None
    else:
        selecionado = st.selectbox(
            "Agente ativo",
            nomes,
            format_func=lambda n: f"{agentes[n].get('icone', '🤖')}  {n}",
        )

    # Criar novo agente
    with st.expander("➕ Novo agente"):
        novo_nome = st.text_input("Nome (sem espaços)", key="novo_nome")
        if st.button("Criar agente", use_container_width=True):
            nome_limpo = novo_nome.strip().replace(" ", "_").lower()
            if not nome_limpo:
                st.error("Informe um nome.")
            elif nome_limpo in agentes:
                st.error("Já existe um agente com esse nome.")
            else:
                agentes[nome_limpo] = dict(config.CONFIG_PADRAO)
                config.salvar_agentes(agentes)
                st.rerun()

    # Configurar agente selecionado
    if selecionado:
        cfg = agentes[selecionado]
        with st.expander("⚙️ Configurar agente"):
            icone_atual = cfg.get("icone", "🤖")
            if icone_atual not in ICONES:
                ICONES.insert(0, icone_atual)
            cfg["icone"] = st.selectbox("Ícone", ICONES, index=ICONES.index(icone_atual))
            cfg["descricao"] = st.text_input("Descrição", value=cfg.get("descricao", ""))
            modelo_atual = cfg.get("modelo", MODELOS_DISPONIVEIS[0])
            if modelo_atual not in MODELOS_DISPONIVEIS:
                MODELOS_DISPONIVEIS.insert(0, modelo_atual)
            cfg["modelo"] = st.selectbox(
                "Modelo", MODELOS_DISPONIVEIS, index=MODELOS_DISPONIVEIS.index(modelo_atual)
            )
            cfg["temperatura"] = st.slider(
                "Temperatura (criatividade)", 0.0, 1.5, float(cfg.get("temperatura", 0.7)), 0.1
            )
            cfg["ferramentas"] = st.multiselect(
                "Ferramentas",
                options=list(tools.FERRAMENTAS.keys()),
                default=[f for f in cfg.get("ferramentas", []) if f in tools.FERRAMENTAS],
            )
            cfg["prompt"] = st.text_area(
                "Prompt de sistema (personalidade/instruções)",
                value=cfg.get("prompt", ""),
                height=200,
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Salvar", use_container_width=True):
                    config.salvar_agentes(agentes)
                    st.success("Salvo!")
            with col2:
                if st.button("🗑️ Excluir", use_container_width=True):
                    del agentes[selecionado]
                    st.session_state.historicos.pop(selecionado, None)
                    config.salvar_agentes(agentes)
                    st.rerun()

        if st.button("🧹 Limpar conversa", use_container_width=True):
            st.session_state.historicos[selecionado] = []
            st.rerun()

# --- área principal: chat -----------------------------------------------------

if not selecionado:
    st.info("Crie um agente na barra lateral para começar.")
    st.stop()

cfg = agentes[selecionado]
icone = cfg.get("icone", "🤖")

if MODO_DEMO:
    # Cabeçalho limpo pro cliente: sem modelo, temperatura ou jargão técnico
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="nome">🏠 Assistente do corretor {html.escape(NOME_CORRETOR)}</div>
            <div class="desc">Atendimento imediato, a qualquer hora — me conta o que você procura 😊</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    ferramentas_html = "".join(
        f'<span class="chip">🔧 {f}</span>' for f in cfg.get("ferramentas", [])
    )
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="nome">{icone} {selecionado.replace('_', ' ').title()}</div>
            <div class="desc">{cfg.get('descricao', '')}</div>
            <div>
                <span class="chip accent">⚡ {cfg.get('modelo', '')}</span>
                <span class="chip">🌡️ {cfg.get('temperatura', 0.7)}</span>
                {ferramentas_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

historico = st.session_state.historicos.setdefault(selecionado, [])

for msg in historico:
    avatar = icone if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        renderizar_mensagem(msg["content"])

pergunta = st.chat_input("Digite sua mensagem...")

if pergunta:
    if not api_key:
        if MODO_DEMO:
            st.error("⚠️ O assistente está temporariamente indisponível. Tente de novo em instantes.")
        else:
            st.error("Informe sua chave da API Groq na barra lateral (é gratuita).")
        st.stop()

    historico.append({"role": "user", "content": pergunta})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(pergunta)

    # personaliza o nome do corretor no prompt sem alterar o agents.yaml
    cfg_exec = dict(cfg)
    cfg_exec["prompt"] = cfg.get("prompt", "").replace("[NOME DO CORRETOR]", NOME_CORRETOR)

    with st.chat_message("assistant", avatar=icone):
        with st.spinner("Pensando..."):
            try:
                resposta = agent.responder(api_key, cfg_exec, historico)
            except Exception as e:
                if MODO_DEMO:
                    resposta = (
                        "⚠️ O assistente está temporariamente indisponível. "
                        "Tente de novo em instantes."
                    )
                else:
                    resposta = f"⚠️ Erro ao chamar o modelo: {e}"
        renderizar_mensagem(resposta)

    historico.append({"role": "assistant", "content": resposta})
