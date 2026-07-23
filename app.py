"""Plataforma de Agentes de IA — interface web (Streamlit).

Rodar com:  streamlit run app.py
"""

import html
import os
import re
from urllib.parse import quote

import streamlit as st

from core import agent, config, leads, tools

# --- modo demo (link pro cliente) vs modo admin -------------------------------
# ?agente=corretor_imoveis  -> abre direto no chat, sem sidebar de administração
# &nome=Fulano (ou corretor=) -> personaliza o nome do profissional sem editar o yaml

_params = st.query_params
MODO_DEMO = "agente" in _params
AGENTE_DEMO = _params.get("agente", "")
_NOME_PARAM = (_params.get("nome", "") or _params.get("corretor", "") or "").strip()
NOME_PROFISSIONAL = _NOME_PARAM or "Ricardo Almeida"

# --- cor de destaque: adapta o chat à identidade do site onde ele é embutido ---
# O widget do site passa a cor detectada em ?cor=RRGGBB (com ou sem #). Se não
# vier, usa um padrão por agente; por último, um tom neutro.

_CORES_PADRAO_AGENTE = {
    "aioti": "#2d8a24",
    "corretor_imoveis": "#2563eb",
}
_COR_NEUTRA = "#3b6cb7"


def _hex_valido(valor: str) -> str:
    """Aceita 'RRGGBB' ou '#RRGGBB' (também 3 dígitos). Vazio se inválido."""
    v = (valor or "").strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) == 6 and all(c in "0123456789abcdefABCDEF" for c in v):
        return "#" + v.lower()
    return ""


def _rgb(cor_hex: str):
    h = cor_hex.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgba(cor_hex: str, alfa: float) -> str:
    r, g, b = _rgb(cor_hex)
    return f"rgba({r}, {g}, {b}, {alfa})"


def _luminancia(cor_hex: str) -> float:
    r, g, b = _rgb(cor_hex)
    return 0.299 * r + 0.587 * g + 0.114 * b


def _escurece(cor_hex: str, fator: float = 0.72) -> str:
    r, g, b = _rgb(cor_hex)
    return "#%02x%02x%02x" % (int(r * fator), int(g * fator), int(b * fator))


def _contraste(cor_hex: str) -> str:
    return "#0f172a" if _luminancia(cor_hex) > 165 else "#ffffff"


COR_ACCENT = (
    _hex_valido(_params.get("cor", ""))
    or _CORES_PADRAO_AGENTE.get(AGENTE_DEMO, "")
    or _COR_NEUTRA
)
# Se a cor for clara, escurece pro texto/ícone ter contraste no fundo branco.
COR_ACCENT_TXT = COR_ACCENT if _luminancia(COR_ACCENT) < 150 else _escurece(COR_ACCENT, 0.6)
COR_ON_ACCENT = _contraste(COR_ACCENT)

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

AVATAR_ASSISTENTE = _svg_uri(_PATHS_ATENDENTE, COR_ACCENT_TXT)
AVATAR_PESSOA = _svg_uri(_PATHS_PESSOA, "#94a3b8")

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
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500&display=swap');

    :root {{
        --accent: {COR_ACCENT};
        --accent-txt: {COR_ACCENT_TXT};
        --on-accent: {COR_ON_ACCENT};
        --accent-08: {_rgba(COR_ACCENT, 0.08)};
        --accent-14: {_rgba(COR_ACCENT, 0.14)};
        --accent-22: {_rgba(COR_ACCENT, 0.22)};
        --accent-32: {_rgba(COR_ACCENT, 0.32)};
    }}

    html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Sora', sans-serif !important; letter-spacing: -0.5px; }}

    /* fundo geral: branco leitoso com um véu suave da cor do site */
    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(1200px 500px at 100% -10%, var(--accent-08), transparent 60%),
            radial-gradient(900px 500px at -10% 110%, var(--accent-08), transparent 55%),
            linear-gradient(180deg, #ffffff 0%, #f4f7fb 100%);
    }}

    /* barra lateral (só no modo admin) */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #ffffff 0%, #f2f5fa 100%);
        border-right: 1px solid #e6ebf2;
    }}
    [data-testid="stSidebar"] h1 {{
        font-size: 1.35rem;
        color: var(--accent-txt);
    }}

    /* cartão do agente — vidro branco */
    .agent-card {{
        background: rgba(255, 255, 255, 0.72);
        -webkit-backdrop-filter: blur(16px) saturate(1.4);
        backdrop-filter: blur(16px) saturate(1.4);
        border: 1px solid rgba(255, 255, 255, 0.85);
        border-radius: 18px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(20, 33, 61, 0.08);
    }}
    .agent-card .nome {{
        font-family: 'Sora', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #16202e;
        letter-spacing: -0.02em;
    }}
    .agent-card .desc {{ color: #5a6b7e; margin-top: 3px; font-size: 0.92rem; }}
    .agent-card.demo {{ display: flex; align-items: center; gap: 15px; }}
    .icone-tile {{
        flex: 0 0 48px;
        width: 48px; height: 48px;
        border-radius: 14px;
        background: linear-gradient(160deg, var(--accent), {_escurece(COR_ACCENT, 0.82)});
        border: 1px solid var(--accent-32);
        box-shadow: 0 6px 16px var(--accent-32);
        display: flex; align-items: center; justify-content: center;
    }}

    /* modo demo: moldura de vidro + entrada suave */
    .demo-shell {{
        background: rgba(255, 255, 255, 0.55);
        -webkit-backdrop-filter: blur(20px) saturate(1.5);
        backdrop-filter: blur(20px) saturate(1.5);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 22px;
        padding: 6px;
        margin-bottom: 1.1rem;
        box-shadow: 0 16px 44px rgba(20, 33, 61, 0.12);
        animation: demo-entrada 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .demo-shell .agent-card.demo {{
        margin-bottom: 0;
        border-radius: 17px;
        box-shadow: none;
        background: rgba(255, 255, 255, 0.6);
    }}
    @keyframes demo-entrada {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .status-pill {{
        display: inline-flex; align-items: center; gap: 7px;
        margin-top: 10px; padding: 4px 13px;
        border-radius: 999px;
        font-size: 0.72rem; font-weight: 600;
        color: #12805a;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }}
    .status-pill .dot {{
        width: 7px; height: 7px; border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.18);
        animation: pulso 2.2s cubic-bezier(0.45, 0, 0.55, 1) infinite;
    }}
    @keyframes pulso {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.45; transform: scale(0.8); }}
    }}

    /* chips de metadados */
    .chip {{
        display: inline-block;
        padding: 3px 12px;
        margin: 8px 6px 0 0;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid #dfe5ee;
        color: #45566a;
        background: #eef2f8;
    }}
    .chip.accent {{ border-color: var(--accent-32); color: var(--accent-txt); background: var(--accent-08); }}

    /* mensagens do chat — bolhas de vidro */
    [data-testid="stChatMessage"] {{
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.9);
        background: rgba(255, 255, 255, 0.72);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.45rem;
        box-shadow: 0 4px 16px rgba(20, 33, 61, 0.06);
    }}
    /* mensagem do usuário puxa a cor do site */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        background: var(--accent-08);
        border-color: var(--accent-22);
    }}

    /* input do chat */
    [data-testid="stChatInput"] textarea {{ font-family: 'IBM Plex Sans', sans-serif; }}
    [data-testid="stChatInput"] {{
        border-radius: 16px;
        border: 1px solid #dbe2ec;
        background: rgba(255, 255, 255, 0.8);
        -webkit-backdrop-filter: blur(8px);
        backdrop-filter: blur(8px);
        transition: border-color 0.3s cubic-bezier(0.32, 0.72, 0, 1),
                    box-shadow 0.3s cubic-bezier(0.32, 0.72, 0, 1);
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-22);
    }}
    [data-testid="stChatInput"] button {{ color: var(--accent-txt) !important; }}

    /* botões */
    .stButton > button {{
        border-radius: 12px;
        border: 1px solid #dbe2ec;
        transition: all .15s ease;
    }}
    .stButton > button:hover {{
        border-color: var(--accent);
        color: var(--accent-txt);
    }}

    /* card do resumo pro corretor (print de venda) */
    .resumo-card {{
        background: linear-gradient(135deg, #ffffff 0%, var(--accent-08) 100%);
        border: 1px solid var(--accent-22);
        border-radius: 16px;
        padding: 1rem 1.3rem;
        margin: 0.6rem 0;
        line-height: 1.9;
        color: #223142;
        box-shadow: 0 8px 26px var(--accent-14);
    }}
    .resumo-card .titulo {{
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--accent-txt);
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid var(--accent-22);
        padding-bottom: 0.4rem;
    }}

    #MainMenu, footer, [data-testid="stStatusWidget"] {{ visibility: hidden; }}
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
    icone_titulo = _svg(_PATHS_PRANCHETA, COR_ACCENT_TXT, 18)
    corpo = "<br>".join(html.escape(l) for l in linhas[1:])
    st.markdown(
        f'<div class="resumo-card">'
        f'<span class="titulo">{icone_titulo}{html.escape(titulo_txt)}</span>{corpo}</div>',
        unsafe_allow_html=True,
    )

    depois = texto[m.end() :].strip().lstrip("-").strip()
    if depois:
        st.markdown(depois)

# --- envio do lead pra equipe ---------------------------------------------------
# A lógica de envio (Telegram/webhook) vive em core/leads.py, compartilhada com
# o bot do Telegram. Configuração via secrets/variáveis de ambiente:
#   TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID  -> mensagem no Telegram da equipe
#   LEADS_WEBHOOK_URL                      -> POST JSON (Google Sheets, Make, CRM...)
# Sufixo _<AGENTE> (ex.: TELEGRAM_CHAT_ID_AIOTI) direciona por agente/cliente.

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
                <div class="icone-tile">{_svg(_PATHS_ATENDENTE, COR_ON_ACCENT, 24)}</div>
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

        m_lead = RE_RESUMO.search(resposta)
        if m_lead:
            resumo_lead = m_lead.group(1).strip()
            enviados = st.session_state.setdefault("leads_enviados", set())
            chave = (selecionado, hash(resumo_lead))
            if chave not in enviados and leads.enviar_lead(selecionado, resumo_lead):
                enviados.add(chave)
                st.caption("Resumo enviado para a equipe ✓")

    historico.append({"role": "assistant", "content": resposta})
