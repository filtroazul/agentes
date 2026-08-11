#!/usr/bin/env python3
"""Grava o tutorial do PAINEL DO CORRETOR para o pai do usuario.

Nao e video de venda: e video de ensinar. Por isso duas diferencas em relacao
aos `gravar-video-*.py`:

  1. LEGENDA GRANDE em cima da tela, dizendo o que esta acontecendo. Quem vai
     assistir tem 60+ anos e vai ver no celular.
  2. RITMO LENTO de proposito. Pausa depois de cada passo, pra dar tempo de ler.

O passo que motivou o video inteiro e o da SITUACAO: o imovel nasce como
rascunho e nao aparece no site. Foi assim que o primeiro cadastro real se
perdeu (10/08/2026). Esse passo tem a legenda mais forte e a maior pausa.

⚠️ O cadastro e REAL: escreve no Supabase de verdade. O imovel de exemplo e
apagado no fim pelo `limpar-tutorial.py`; se a gravacao morrer no meio, apagar
na mao pelo painel (procure o titulo em TITULO).

Rodar:
    cd C:\\Users\\Iagho\\OneDrive\\projeto\\ah-imobiliaria && python -m http.server 8730
    python vendas/gravar-tutorial-painel.py
"""

import json
import pathlib
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from credenciais import credenciais  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = pathlib.Path.home() / "AppData/Local/Temp/tutorial-painel"
DESTINO = RAIZ / "vendas" / "tutorial-painel-ah.mp4"
# Foto ILUSTRADA de propósito. Já tentei com foto real de outro cliente e ficou
# pior: eram fachadas de salão, com pessoa, e num tutorial de imobiliária isso
# confunde mais do que ajuda. Gerada por vendas/gerar-foto-exemplo (ver git).
FOTO = RAIZ / "vendas" / "foto-exemplo-imovel.jpg"

URL = "http://localhost:8730/admin.html"
SITE = "http://localhost:8730/index.html#catalogo"
ENDERECO_REAL = "filtroazul.github.io/ah-imobiliaria/admin.html"

# Vem de vendas/.credenciais-ah.json (barrado pelo .gitignore) ou das variaveis
# AH_PAINEL_EMAIL / AH_PAINEL_SENHA. Nunca escreva a senha aqui: este
# repositorio e publico e o historico do git nao esquece.
EMAIL, SENHA = credenciais()

TITULO = "Casa com quintal no Montese"

W, H = 1440, 900
FPS = 25

SAIDA.mkdir(parents=True, exist_ok=True)
for velho in SAIDA.glob("f*.jpg"):
    velho.unlink()

frames = []
_n = [0]

# Cursor sintetico: o screenshot do Playwright NAO desenha o mouse, e sem isso
# o video mostra campos se preenchendo sozinhos.
CURSOR = """
() => {
  const c = document.createElement('div');
  c.id = '__cur';
  c.style.cssText = 'position:fixed;left:-99px;top:-99px;z-index:2147483647;' +
    'width:28px;height:28px;pointer-events:none;will-change:transform';
  c.innerHTML =
    '<svg viewBox="0 0 24 24" width="28" height="28">' +
    '<path d="M5 2 L5 20 L10 15.4 L13 22 L16.4 20.4 L13.4 14 L20 14 Z" ' +
    'fill="#fff" stroke="rgba(9,24,48,.8)" stroke-width="1.2" stroke-linejoin="round"/></svg>' +
    '<i style="position:absolute;left:-10px;top:-10px;width:48px;height:48px;border-radius:50%;' +
    'border:3px solid rgba(110,24,27,.9);opacity:0;transform:scale(.3)"></i>';
  document.body.appendChild(c);
  const anel = c.querySelector('i');
  window.__cur = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px'; };
  window.__pulso = () => {
    anel.style.transition = 'none';
    anel.style.opacity = '1';
    anel.style.transform = 'scale(.3)';
    requestAnimationFrame(() => {
      anel.style.transition = 'transform .5s ease-out, opacity .5s ease-out';
      anel.style.opacity = '0';
      anel.style.transform = 'scale(1)';
    });
  };
}
"""

# Faixa de legenda. Fica no TOPO porque o botao de salvar e os campos vivem
# embaixo, e legenda no rodape taparia justamente o que se quer mostrar.
LEGENDA = """
() => {
  const b = document.createElement('div');
  b.id = '__leg';
  b.style.cssText = 'position:fixed;left:0;right:0;top:0;z-index:2147483646;' +
    'background:linear-gradient(#6e181b,#571316);color:#fff;padding:18px 28px;' +
    "font:600 27px/1.32 'Segoe UI',system-ui,sans-serif;letter-spacing:.2px;" +
    'box-shadow:0 6px 24px rgba(0,0,0,.28);display:none;text-align:center';
  b.innerHTML = '<span id="__legp" style="opacity:.62;font-size:19px;font-weight:700;' +
    'letter-spacing:2px;display:block;margin-bottom:5px"></span>' +
    '<span id="__legt"></span>';
  document.body.appendChild(b);
  window.__legenda = (passo, texto) => {
    document.getElementById('__legp').textContent = passo || '';
    document.getElementById('__legt').innerHTML = texto;
    b.style.display = texto ? 'block' : 'none';
  };
}
"""


def salvar(page, dur):
    _n[0] += 1
    p = SAIDA / f"f{_n[0]:05d}.jpg"
    page.screenshot(path=str(p), type="jpeg", quality=88)
    frames.append((p.name, dur))


def pausa(page, segundos):
    """Segura a imagem parada. E aqui que o espectador le a legenda."""
    n = max(1, int(segundos * FPS))
    for _ in range(n):
        salvar(page, 1.0 / FPS)


def legenda(page, passo, texto, segurar=0.0):
    page.evaluate("([p, t]) => window.__legenda(p, t)", [passo, texto])
    if segurar:
        pausa(page, segurar)


_pos = [W / 2, H / 2]


def mover(page, x, y):
    page.mouse.move(x, y)
    page.evaluate("([x, y]) => window.__cur(x, y)", [x, y])
    _pos[0], _pos[1] = x, y


def mover_ate(page, x, y, segundos=0.7, curva=0.0):
    x0, y0 = _pos
    n = max(1, int(segundos * FPS))
    for i in range(n):
        t = (i + 1) / n
        s = t * t * (3 - 2 * t)
        mover(page, x0 + (x - x0) * s,
              y0 + (y - y0) * s + curva * (4 * t * (1 - t)))
        salvar(page, 1.0 / FPS)


def centro(page, seletor):
    cx = page.evaluate(
        """s => { const e = document.querySelector(s);
                  e.scrollIntoView({block:'center'});
                  const r = e.getBoundingClientRect();
                  return [r.left + r.width/2, r.top + r.height/2]; }""", seletor)
    return cx


def ir_e_clicar(page, seletor, ler=0.5, segundos=0.7, curva=0.0):
    x, y = centro(page, seletor)
    mover_ate(page, x, y, segundos, curva)
    page.evaluate("() => window.__pulso()")
    page.mouse.click(x, y)
    pausa(page, ler)


def escrever(page, seletor, texto, por_char=0.055):
    x, y = centro(page, seletor)
    mover_ate(page, x, y, 0.55)
    page.evaluate("() => window.__pulso()")
    page.mouse.click(x, y)
    page.fill(seletor, "")
    for ch in texto:
        page.type(seletor, ch, delay=0)
        salvar(page, por_char)
    pausa(page, 0.35)


def rolar_ate(page, alvo, segundos=0.9):
    de = page.evaluate("() => window.scrollY")
    n = max(1, int(segundos * FPS))
    for i in range(n):
        t = (i + 1) / n
        s = t * t * (3 - 2 * t)
        page.evaluate("y => window.scrollTo(0, y)", de + (alvo - de) * s)
        salvar(page, 1.0 / FPS)


def preparar(page):
    page.evaluate(CURSOR)
    page.evaluate(LEGENDA)
    mover(page, W / 2, H / 2)


with sync_playwright() as pw:
    nav = pw.chromium.launch()
    ctx = nav.new_context(viewport={"width": W, "height": H},
                          reduced_motion="no-preference")
    pag = ctx.new_page()
    pag.goto(URL, wait_until="networkidle", timeout=60000)
    preparar(pag)

    # ---------------------------------------------------------------- abertura
    legenda(pag, "PAINEL DA AH IMOBILIÁRIA",
            "Como cadastrar um imóvel, do começo ao fim", 3.2)
    legenda(pag, "PASSO 1 — ENTRAR",
            f"Abra <b>{ENDERECO_REAL}</b> no celular ou no computador", 3.0)

    # ------------------------------------------------------------------- login
    escrever(pag, "#login-email", EMAIL, por_char=0.035)
    legenda(pag, "PASSO 1 — ENTRAR", "Agora a sua senha", 0.8)
    escrever(pag, "#login-senha", SENHA, por_char=0.05)
    ir_e_clicar(pag, "#login-botao", ler=0.6)
    pag.wait_for_timeout(2500)
    pausa(pag, 1.2)

    legenda(pag, "PRONTO, VOCÊ ENTROU",
            "Esta é a sua lista. Todo imóvel cadastrado aparece aqui", 3.0)

    # ---------------------------------------------------------------- cadastrar
    legenda(pag, "PASSO 2 — COMEÇAR", "Clique em <b>Cadastrar imóvel</b>", 1.6)
    ir_e_clicar(pag, "#novo", ler=1.2, curva=-60)

    legenda(pag, "PASSO 3 — O BÁSICO",
            "Um título que descreva o imóvel em poucas palavras", 1.8)
    escrever(pag, "#i-titulo", TITULO)

    legenda(pag, "PASSO 3 — O BÁSICO", "É para vender ou para alugar?", 1.4)
    ir_e_clicar(pag, "#i-finalidade", ler=0.3)
    pag.select_option("#i-finalidade", "venda")
    pausa(pag, 1.0)

    ir_e_clicar(pag, "#i-tipo", ler=0.3)
    pag.select_option("#i-tipo", "casa")
    pausa(pag, 1.0)

    legenda(pag, "PASSO 3 — O BÁSICO",
            "O valor. Só números, sem ponto e sem vírgula", 1.6)
    escrever(pag, "#i-preco", "320000", por_char=0.09)

    # ---------------------------------------------------------------- medidas
    legenda(pag, "PASSO 4 — AS MEDIDAS",
            "Quartos, banheiros, vagas. O que não tiver, deixe zero", 1.8)
    for campo, valor in (("#i-quartos", "3"), ("#i-banheiros", "2"),
                         ("#i-vagas", "2"), ("#i-area-util", "110")):
        escrever(pag, campo, valor, por_char=0.1)

    # -------------------------------------------------------------- descrição
    legenda(pag, "PASSO 5 — A DESCRIÇÃO",
            "Escreva como você contaria para o cliente pessoalmente", 1.8)
    escrever(pag, "#i-descricao",
             "Casa em rua tranquila, com quintal grande nos fundos.",
             por_char=0.032)

    # ---------------------------------------------------------------- endereço
    legenda(pag, "PASSO 6 — ONDE FICA",
            "O bairro é o que o cliente mais procura", 1.6)
    escrever(pag, "#i-bairro", "Montese", por_char=0.07)
    pausa(pag, 0.8)

    # ------------------------------------------------------------------- fotos
    legenda(pag, "PASSO 7 — AS FOTOS",
            "Clique na área das fotos e escolha do celular", 2.0)
    x, y = centro(pag, "#arquivos")
    pag.evaluate("""() => { const z = document.querySelector('#arquivos')
        .closest('.solta, .zona, section, div'); if (z) z.scrollIntoView({block:'center'}); }""")
    pausa(pag, 0.4)
    pag.set_input_files("#arquivos", str(FOTO))
    pag.wait_for_timeout(2500)
    pausa(pag, 2.0)
    legenda(pag, "PASSO 7 — AS FOTOS",
            "A primeira foto vira a capa do anúncio", 2.2)

    # ------------------------------------------------- o passo que mais importa
    ir_e_clicar(pag, "#i-status", ler=0.4)
    legenda(pag, "PASSO 8 — O MAIS IMPORTANTE",
            "Aqui está escrito <b>Rascunho</b>. Rascunho <b>NÃO aparece no site</b>", 3.4)
    pag.select_option("#i-status", "disponivel")
    pausa(pag, 0.6)
    legenda(pag, "PASSO 8 — O MAIS IMPORTANTE",
            "Troque para <b>Disponível</b>. É isto que publica o imóvel", 3.4)

    # ----------------------------------------------------------------- salvar
    legenda(pag, "PASSO 9 — SALVAR", "Agora sim: <b>Salvar imóvel</b>", 1.8)
    ir_e_clicar(pag, "#forma button[type=submit], #forma .btn--principal", ler=0.4)
    pag.wait_for_timeout(4000)
    pausa(pag, 1.0)
    legenda(pag, "PASSO 9 — SALVAR",
            "O painel confirma que está <b>publicado</b>", 3.2)

    # -------------------------------------------------------------- no ar
    # Vai direto na PÁGINA DO IMÓVEL recém-criado, e não na home. Na home o
    # trecho "Três que valem a visita" mostra os destaques da carteira real, e
    # o tutorial acabaria exibindo outro imóvel qualquer — na 1ª gravação saiu
    # um cadastro de teste com print de painel no lugar da foto.
    # O botão "Ver" da lista é target=_blank e abriria outra aba, então leio o
    # código no próprio item e navego na mesma página.
    codigo = pag.evaluate(
        """() => { const t = document.querySelector('#lista').innerText;
                   const m = t.match(/C[óo]d\\.\\s*(\\d+)/); return m ? m[1] : null; }""")
    legenda(pag, "PRONTO", "Vamos ver o imóvel no site", 1.8)
    pag.goto(f"http://localhost:8730/imovel.html?cod={codigo}",
             wait_until="networkidle", timeout=60000)
    preparar(pag)
    pag.wait_for_timeout(3000)
    legenda(pag, "PRONTO", "É assim que o cliente vê o seu imóvel", 3.0)
    rolar_ate(pag, 620, 1.8)
    pausa(pag, 3.0)

    legenda(pag, "RESUMINDO",
            "Cadastrar &rarr; preencher &rarr; <b>Situação: Disponível</b> &rarr; Salvar", 4.0)

    nav.close()

(SAIDA / "lista.txt").write_text(
    "".join(f"file '{n}'\nduration {d:.4f}\n" for n, d in frames)
    + f"file '{frames[-1][0]}'\n",
    encoding="utf-8",
)

ffmpeg = None
for cand in list(pathlib.Path.home().glob(
        "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe")):
    ffmpeg = str(cand)
    break
if not ffmpeg:
    ffmpeg = "ffmpeg"

subprocess.run(
    [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(SAIDA / "lista.txt"),
     "-fps_mode", "vfr", "-vf", f"fps={FPS},format=yuv420p",
     "-c:v", "libx264", "-preset", "medium", "-crf", "23",
     "-movflags", "+faststart", str(DESTINO)],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(json.dumps({
    "frames": len(frames),
    "duracao_s": round(sum(d for _, d in frames), 1),
    "arquivo": str(DESTINO),
    "mb": round(DESTINO.stat().st_size / 1048576, 1),
}, ensure_ascii=False))
