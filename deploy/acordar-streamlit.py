#!/usr/bin/env python3
"""Acorda (e mantem acordado) o app do Streamlit Community Cloud.

POR QUE ISTO EXISTE, e nao um curl:
o `curl` no `/_stcore/health` devolve 303 — e um redirect pra tela de auth do
Streamlit, o ping nunca chega no container. E o GET da pagina devolve 200 mesmo
com o app dormindo: sao ~9 KB de esqueleto HTML, e a tela "Zzzz" e desenhada
depois, pelo JS. Ou seja: 200 nao significa acordado.

O Streamlit conta atividade por **sessao de websocket** (`/_stcore/stream`), e
quem abre esse websocket e o JS da pagina. Entao a unica forma honesta de
manter o app de pe e abrir a pagina num navegador de verdade, clicar em
"Yes, get this app back up!" se ela aparecer, e ficar la alguns segundos.

Roda no GitHub Actions (.github/workflows/keep-alive.yml) e tambem na mao, aqui
no PC, antes de uma demo ao vivo:

    python deploy/acordar-streamlit.py

Sai com codigo 0 se o app respondeu, 1 se nao.
"""

import os
import sys
import time

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

APP = os.environ.get(
    "STREAMLIT_APP_URL",
    "https://agentes-s68ksrzb97z5q4qqp7f8nq.streamlit.app/?agente=atendimento&embed=true",
)

# Acordar do zero leva ~2 min. O teto e generoso de proposito: se o app ja
# estiver de pe, o script sai em segundos e nao usa esse tempo todo.
TETO_ACORDAR_MS = 240_000

# Depois que a UI aparece, ficar parado com o websocket aberto. E isso que
# conta como "sessao" pro Streamlit.
SEGUNDOS_DE_PERMANENCIA = 20

TEXTO_BOTAO = "get this app back up"


def log(msg):
    print(msg, flush=True)


def frame_do_app(page):
    """Acha o frame onde a UI do Streamlit realmente mora.

    ARMADILHA JA PAGA: a UI fica num frame ANINHADO cuja URL contem `/~/+/`.
    Ler a pagina de cima devolve so "Built with Streamlit".
    """
    for f in page.frames:
        if "/~/+/" in f.url:
            return f
    return None


def app_desenhou(frame):
    """A UI existe de verdade? (nao so o esqueleto HTML)"""
    try:
        return frame.locator('[data-testid="stAppViewContainer"], .stApp').count() > 0
    except Exception:
        return False


def acordar(page):
    """Retorna o frame do app, ou None se nao subiu dentro do teto."""
    limite = time.monotonic() + TETO_ACORDAR_MS / 1000
    ja_clicou = False

    while time.monotonic() < limite:
        # 1) a tela "Zzzz" mora na pagina de cima, nao no frame aninhado
        if not ja_clicou:
            botao = page.get_by_text(TEXTO_BOTAO, exact=False)
            try:
                if botao.count() > 0:
                    log("-> app estava DORMINDO; clicando em 'Yes, get this app back up!'")
                    botao.first.click(timeout=10_000)
                    ja_clicou = True
            except Exception:
                pass  # sumiu entre o count e o click: o app acordou sozinho

        # 2) o frame da UI ja existe e ja desenhou?
        frame = frame_do_app(page)
        if frame is not None and app_desenhou(frame):
            return frame

        page.wait_for_timeout(3_000)

    return None


def main():
    log(f"app: {APP}")
    inicio = time.monotonic()

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=["--no-sandbox"])
        contexto = navegador.new_context(viewport={"width": 1280, "height": 900})
        page = contexto.new_page()

        try:
            page.goto(APP, wait_until="domcontentloaded", timeout=60_000)
        except PWTimeout:
            log("!! a pagina nem carregou o HTML dentro de 60s")
            navegador.close()
            return 1

        frame = acordar(page)
        if frame is None:
            log(f"!! a UI nao subiu em {TETO_ACORDAR_MS // 1000}s")
            log(f"   frames vistos: {[f.url for f in page.frames]}")
            navegador.close()
            return 1

        log(f"-> UI de pe em {time.monotonic() - inicio:.0f}s")

        # Ficar parado com o websocket aberto: e isto que o Streamlit conta.
        page.wait_for_timeout(SEGUNDOS_DE_PERMANENCIA * 1_000)

        # Prova de vida: o cabecalho do agente e escrito pelo servidor Python,
        # entao se ele apareceu, o container rodou codigo — nao e so o HTML.
        try:
            texto = frame.inner_text("body", timeout=10_000).strip()
            log(f"-> {len(texto)} caracteres renderizados pelo app")
            if len(texto) < 40:
                log("!! renderizou quase nada; o container pode nao ter subido")
                navegador.close()
                return 1
        except Exception as e:
            log(f"!! nao consegui ler o corpo do frame: {e}")
            navegador.close()
            return 1

        navegador.close()

    log(f"OK: app acordado e com sessao aberta ({time.monotonic() - inicio:.0f}s no total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
