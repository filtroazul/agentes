"""Plataforma de Agentes de IA — interface web (Streamlit).

Rodar com:  streamlit run app.py
"""

import html
import os
import re
from urllib.parse import quote

import streamlit as st

from core import agent, config, tools

# --- modo demo (link pro cliente) vs modo admin -------------------------------
# ?agente=corretor_imoveis  -> abre direto no chat, sem sidebar de administração
# &nome=Fulano (ou corretor=) -> personaliza o nome do profissional sem editar o yaml

_params = st.query_params
MODO_DEMO = "agente" in _params
AGENTE_DEMO = _params.get("agente", "")
_NOME_PARAM = (_params.get("nome", "") or _params.get("corretor", "") or "").strip()
NOME_PROFISSIONAL = _NOME_PARAM or "Ricardo Almeida"

# --- ícones SVG (traço fino, sem emoji) ----------------------------------------

_SVG_ATTRS = (
    "xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    "stroke='{cor}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'"
)

def _svg(paths: str, cor: str, tamanho: int = 20) -> str:
    attrs = _SVG_ATTRS.format(cor=cor)
    return f"<svg {attrs} width='{tamanho}' height='{tamanho}'>{paths}</svg>"

def _svg_uri(paths: str, cor: str) -> str:
    return "data:image/svg+xml;utf8," + quote(_svg(paths, cor, 26))

_PATHS_ATENDENTE = (
    "<path d='M4 13a8 8 0 0 1 16 0'/>"
    "<rect x='2.5' y='13' width='4.5' height='6.5' rx='2'/>"
    "<rect x='17' y='13' width='4.5' height='6.5' rx='2'/>"
    "<path d='M20 19.5v1a2 2 0 0 1-2 2h-4'/>"
)
_PATHS_PESSOA = (
    "<circle cx='12' cy='8' r='4'/>"
    "<path d='M4 21c0-4.2 3.6-6.8 8-6.8s8 2.6 8 6.8'/>"
)
_PATHS_PRANCHETA = (
    "<rect x='8' y='2.5' width='8' height='4' rx='1'/>"
    "<path d='M16 4.5h2a2 2 0 0 1 2 2V19a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6.5a2 2 0 0 1 2-2h2'/>"
    "<path d='M9 12h6'/><path d='M9 16h4'/>"
)

AVATAR_ASSISTENTE = _svg_uri(_PATHS_ATENDENTE, "#E8985E")
AVATAR_PESSOA = _svg_uri(_PATHS_PESSOA, "#9BA3B2")

st.set_page_config(
    page_title=(f"Atendimento — {_NOME_PARAM}" if _NOME_PARAM else "Atendimento")
    if MODO_DEMO
    else "Plataforma de Agentes",
    page_icon=AVATAR_ASSISTENTE if MODO_DEMO else "✦",
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
    .agent-card.demo { display: flex; align-items: center; gap: 16px; }
    .icone-tile {
        flex: 0 0 48px;
        width: 48px; height: 48px;
        border-radius: 13px;
        background: linear-gradient(160deg, #2B2015 0%, #241C14 100%);
        border: 1px solid #7A5636;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        display: flex; align-items: center; justify-content: center;
    }

    /* modo demo: moldura dupla (card dentro de card) + entrada suave */
    .demo-shell {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 22px;
        padding: 6px;
        margin-bottom: 1.1rem;
        box-shadow: 0 18px 48px rgba(8, 10, 14, 0.45);
        animation: demo-entrada 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .demo-shell .agent-card.demo {
        margin-bottom: 0;
        border-radius: 16px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    @keyframes demo-entrada {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .status-pill {
        display: inline-flex; align-items: center; gap: 7px;
        margin-top: 9px; padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.72rem; font-weight: 500;
        color: #7ED9A7;
        background: rgba(62, 156, 107, 0.12);
        border: 1px solid rgba(62, 156, 107, 0.35);
    }
    .status-pill .dot {
        width: 7px; height: 7px; border-radius: 999px;
        background: #57C98A;
        animation: pulso 2.2s cubic-bezier(0.45, 0, 0.55, 1) infinite;
    }
    @keyframes pulso {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%      { opacity: 0.45; transform: scale(0.8); }
    }

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
        transition: border-color 0.3s cubic-bezier(0.32, 0.72, 0, 1),
                    box-shadow 0.3s cubic-bezier(0.32, 0.72, 0, 1);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #E8985E;
        box-shadow: 0 0 0 1px rgba(232, 152, 94, 0.3);
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
        display: flex;
        align-items: center;
        gap: 8px;
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
    r"-{3,}\s*\n\s*((?:📋\s*)?RESUMO[^\n]*.*?)(?:\n\s*-{3,}|\Z)", re.DOTALL
)


def renderizar_mensagem(texto: str) -> None:
    """Markdown normal, mas o bloco RESUMO vira um card destacado."""
    m = RE_RESUMO.search(texto)
    if not m:
        st.markdown(texto)
        return

    antes = texto[: m.start()].strip()
    if antes:
        st.markdown(antes)

    linhas = [l.strip() for l in m.group(1).strip().splitlines() if l.strip()]
    titulo_txt = re.sub(r"^📋\s*", "", linhas[0]) if linhas else "RESUMO DO LEAD"
    icone_titulo = _svg(_PATHS_PRANCHETA, "#6FD79E", 18)
    corpo = "<br>".join(html.escape(l) for l in linhas[1:])
    st.markdown(
        f'<div class="resumo-card">'
        f'<span class="titulo">{icone_titulo}{html.escape(titulo_txt)}</span>{corpo}</div>',
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


def personalizar(texto: str) -> str:
    """Substitui os placeholders de nome sem alterar o agents.yaml."""
    return texto.replace("[NOME DO CORRETOR]", NOME_PROFISSIONAL).replace(
        "[NOME]", NOME_PROFISSIONAL
    )


if MODO_DEMO:
    # Cabeçalho limpo pro cliente: sem modelo, temperatura ou jargão técnico.
    # Título/subtítulo vêm do yaml do agente (qualquer ramo), com fallback genérico.
    titulo_demo = personalizar(cfg.get("titulo_demo") or "Assistente de [NOME]")
    subtitulo_demo = personalizar(
        cfg.get("subtitulo_demo")
        or "Atendimento imediato, a qualquer hora. Conte o que você procura."
    )
    st.markdown(
        f"""
        <div class="demo-shell">
            <div class="agent-card demo">
                <div class="icone-tile">{_svg(_PATHS_ATENDENTE, "#E8985E", 24)}</div>
                <div>
                    <div class="nome">{html.escape(titulo_demo)}</div>
                    <div class="desc">{html.escape(subtitulo_demo)}</div>
                    <div class="status-pill"><span class="dot"></span>Online agora · resposta em segundos</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    ferramentas_html = "".join(
        f'<span class="chip">{f}</span>' for f in cfg.get("ferramentas", [])
    )
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="nome">{icone} {selecionado.replace('_', ' ').title()}</div>
            <div class="desc">{cfg.get('descricao', '')}</div>
            <div>
                <span class="chip accent">{cfg.get('modelo', '')}</span>
                <span class="chip">temp {cfg.get('temperatura', 0.7)}</span>
                {ferramentas_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

historico = st.session_state.historicos.setdefault(selecionado, [])

avatar_assistente = AVATAR_ASSISTENTE if MODO_DEMO else icone

for msg in historico:
    avatar = avatar_assistente if msg["role"] == "assistant" else AVATAR_PESSOA
    with st.chat_message(msg["role"], avatar=avatar):
        renderizar_mensagem(msg["content"])

pergunta = st.chat_input("Digite sua mensagem...")

if pergunta:
    if not api_key:
        if MODO_DEMO:
            st.error("O assistente está temporariamente indisponível. Tente de novo em instantes.")
        else:
            st.error("Informe sua chave da API Groq na barra lateral (é gratuita).")
        st.stop()

    historico.append({"role": "user", "content": pergunta})
    with st.chat_message("user", avatar=AVATAR_PESSOA):
        st.markdown(pergunta)

    # personaliza o nome do profissional no prompt sem alterar o agents.yaml
    cfg_exec = dict(cfg)
    cfg_exec["prompt"] = personalizar(cfg.get("prompt", ""))

    with st.chat_message("assistant", avatar=avatar_assistente):
        with st.spinner("Pensando..."):
            try:
                resposta = agent.responder(api_key, cfg_exec, historico)
            except Exception as e:
                if MODO_DEMO:
                    resposta = (
                        "O assistente está temporariamente indisponível. "
                        "Tente de novo em instantes."
                    )
                else:
                    resposta = f"Erro ao chamar o modelo: {e}"
        renderizar_mensagem(resposta)

    historico.append({"role": "assistant", "content": resposta})
