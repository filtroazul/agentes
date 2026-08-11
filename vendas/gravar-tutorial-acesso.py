#!/usr/bin/env python3
"""Grava o tutorial de COMO ENTRAR NO PAINEL, para o pai do usuario.

Irmao mais novo do `gravar-tutorial-painel.py`, e com a mesma regra de ouro:
quem vai assistir tem 60+ anos e vai ver no celular. Duas diferencas em
relacao aquele:

  1. VERTICAL (390x844). O outro e 1440x900, de PC. Este nasce no formato em
     que ele vai receber no WhatsApp e no aparelho em que vai usar o painel de
     verdade -- as fotos dos imoveis estao no celular dele.
  2. NAO CADASTRA NADA. O outro escreve no Supabase e precisa do
     `limpar-tutorial.py` depois. Este so navega e loga; nao deixa sujeira, e
     pode ser rodado quantas vezes quiser.

O que ele ensina, e por que nesta ordem:

  - A primeira vez e pelo endereco, digitado na mao. Nao tem jeito, e o
    unico passo chato.
  - Depois de logar UMA vez naquele aparelho, o botao "Painel" passa a
    aparecer no cabecalho do site (js/painel.js le a sessao no localStorage).
    Esse e o passo que motivou o video: dai em diante nao se digita mais
    endereco nem senha.

⚠️ O login e REAL, contra o Supabase de producao. Isso e proposital: e o login
de verdade que grava a sessao no localStorage, e sem ela o botao "Painel" nao
apareceria na gravacao. Nada e escrito no banco.

⚠️ Quando o dominio ahernandez.com.br for apontado pro projeto novo, este
video desatualiza. Trocar SITE/ADMIN e ENDERECO_VISIVEL abaixo e rodar de
novo -- leva uns 3 minutos.

Rodar:
    python vendas/gravar-tutorial-acesso.py
"""

import json
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from credenciais import credenciais  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = pathlib.Path.home() / "AppData/Local/Temp/tutorial-acesso"
DESTINO = RAIZ / "vendas" / "tutorial-acesso-painel.mp4"

BASE = "https://ah-imobiliaria.vercel.app"
ADMIN = f"{BASE}/admin.html"
SITE = f"{BASE}/index.html"
# O que aparece escrito na legenda. Separado da URL de navegacao de proposito:
# quando o dominio virar, o texto muda aqui sem mexer na navegacao.
ENDERECO_VISIVEL = "ah-imobiliaria.vercel.app/admin.html"

# Vem de vendas/.credenciais-ah.json (barrado pelo .gitignore) ou das variaveis
# AH_PAINEL_EMAIL / AH_PAINEL_SENHA. Nunca escreva a senha aqui: este
# repositorio e publico e o historico do git nao esquece.
EMAIL, SENHA = credenciais()

# Tela de celular. O device_scale_factor=2 e o que faz o video sair nitido:
# o quadro final tem 780x1688, nao 390x844.
W, H = 390, 844
ESCALA = 2
FPS = 25

CHROME = (pathlib.Path.home() /
          "AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe")

SAIDA.mkdir(parents=True, exist_ok=True)
for velho in SAIDA.glob("f*.jpg"):
    velho.unlink()

frames = []
_n = [0]

# Cursor sintetico: o screenshot do Playwright NAO desenha o ponteiro, e sem
# isso o video mostra campos se preenchendo sozinhos. Aqui ele e uma bolinha
# de toque, nao uma setinha: a tela e de celular, e dedo nao tem seta.
TOQUE = """
() => {
  const c = document.createElement('div');
  c.id = '__cur';
  c.style.cssText = 'position:fixed;left:-99px;top:-99px;z-index:2147483647;' +
    'width:34px;height:34px;margin:-17px 0 0 -17px;pointer-events:none;' +
    'border-radius:50%;background:rgba(110,24,27,.28);' +
    'border:2px solid rgba(110,24,27,.85)';
  c.innerHTML = '<i style="position:absolute;left:-12px;top:-12px;width:54px;' +
    'height:54px;border-radius:50%;border:3px solid rgba(110,24,27,.9);' +
    'opacity:0;transform:scale(.3)"></i>';
  document.body.appendChild(c);
  const anel = c.querySelector('i');
  window.__cur = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px'; };
  window.__pulso = () => {
    anel.style.transition = 'none';
    anel.style.opacity = '1';
    anel.style.transform = 'scale(.3)';
    requestAnimationFrame(() => {
      anel.style.transition = 'transform .55s ease-out, opacity .55s ease-out';
      anel.style.opacity = '0';
      anel.style.transform = 'scale(1)';
    });
  };
}
"""

# Legenda. Por padrao no TOPO, porque o teclado e os botoes de acao vivem
# embaixo e legenda no rodape taparia o que se quer mostrar.
#
# ⚠️ Mas ela PRECISA poder descer, e isso nao e capricho: `.cabecalho` do site
# e `position:fixed; top:0` (css/site.css:152), e o botao "Painel" mora dentro
# dele. Com a legenda no topo ela cobre o botao — some da tela justo no momento
# em que o video manda o espectador olhar pra ele, e ainda come o clique. Por
# isso os trechos que falam do cabecalho usam `onde='rodape'`.
#
# `pointer-events:none` pelo mesmo motivo: legenda e decoracao, nunca deve
# interceptar toque.
LEGENDA = """
() => {
  const b = document.createElement('div');
  b.id = '__leg';
  b.style.cssText = 'position:fixed;left:0;right:0;top:0;z-index:2147483646;' +
    'background:linear-gradient(#6e181b,#571316);color:#fff;padding:13px 16px;' +
    "font:600 18px/1.34 'Segoe UI',system-ui,sans-serif;pointer-events:none;" +
    'box-shadow:0 5px 20px rgba(0,0,0,.3);display:none;text-align:center';
  b.innerHTML = '<span id="__legp" style="opacity:.62;font-size:13px;font-weight:700;' +
    'letter-spacing:1.6px;display:block;margin-bottom:4px"></span>' +
    '<span id="__legt"></span>';
  document.body.appendChild(b);
  window.__legenda = (passo, texto, onde) => {
    document.getElementById('__legp').textContent = passo || '';
    document.getElementById('__legt').innerHTML = texto;
    const rodape = onde === 'rodape';
    b.style.top = rodape ? 'auto' : '0';
    b.style.bottom = rodape ? '0' : 'auto';
    b.style.boxShadow = rodape ? '0 -5px 20px rgba(0,0,0,.3)'
                               : '0 5px 20px rgba(0,0,0,.3)';
    b.style.display = texto ? 'block' : 'none';
  };
}
"""

# Halo pra destacar UM elemento. E o recurso central deste video: o botao
# "Painel" e pequeno e fica no meio de um cabecalho cheio; sem isso o
# espectador de 60 anos nao acha o que a legenda esta mandando ele achar.
HALO = """
(sel) => {
  document.getElementById('__halo')?.remove();
  if (!sel) return;
  const e = document.querySelector(sel);
  if (!e) return;
  const r = e.getBoundingClientRect();
  const h = document.createElement('div');
  h.id = '__halo';
  h.style.cssText = 'position:fixed;z-index:2147483645;pointer-events:none;' +
    'border:3px solid #c3a35c;border-radius:999px;' +
    'box-shadow:0 0 0 9999px rgba(12,8,4,.55), 0 0 18px 4px rgba(195,163,92,.9);' +
    `left:${r.left - 7}px;top:${r.top - 7}px;` +
    `width:${r.width + 14}px;height:${r.height + 14}px;`;
  document.body.appendChild(h);
}
"""


def salvar(pag, dur):
    _n[0] += 1
    p = SAIDA / f"f{_n[0]:05d}.jpg"
    pag.screenshot(path=str(p), type="jpeg", quality=88)
    frames.append((p.name, dur))


def pausa(pag, segundos):
    """Segura a imagem parada. E aqui que o espectador le a legenda."""
    for _ in range(max(1, int(segundos * FPS))):
        salvar(pag, 1.0 / FPS)


def legenda(pag, passo, texto, segurar=0.0, onde="topo"):
    pag.evaluate("([p, t, o]) => window.__legenda(p, t, o)", [passo, texto, onde])
    print(f"  [{passo}] {texto[:52]}", flush=True)
    if segurar:
        pausa(pag, segurar)


def halo(pag, seletor, segurar=0.0):
    pag.evaluate(HALO, seletor)
    if segurar:
        pausa(pag, segurar)


_pos = [W / 2, H / 2]


def mover(pag, x, y):
    pag.mouse.move(x, y)
    pag.evaluate("([x, y]) => window.__cur(x, y)", [x, y])
    _pos[0], _pos[1] = x, y


def mover_ate(pag, x, y, segundos=0.75):
    x0, y0 = _pos
    n = max(1, int(segundos * FPS))
    for i in range(n):
        t = (i + 1) / n
        s = t * t * (3 - 2 * t)          # suaviza a saida e a chegada
        mover(pag, x0 + (x - x0) * s, y0 + (y - y0) * s)
        salvar(pag, 1.0 / FPS)


def centro(pag, seletor):
    return pag.evaluate(
        """s => { const e = document.querySelector(s);
                  e.scrollIntoView({block:'center'});
                  const r = e.getBoundingClientRect();
                  return [r.left + r.width/2, r.top + r.height/2]; }""", seletor)


def tocar(pag, seletor, ler=0.6, segundos=0.75):
    x, y = centro(pag, seletor)
    mover_ate(pag, x, y, segundos)
    pag.evaluate("() => window.__pulso()")
    pausa(pag, 0.28)
    pag.mouse.click(x, y)
    pausa(pag, ler)


def escrever(pag, seletor, texto, por_char=0.06):
    x, y = centro(pag, seletor)
    mover_ate(pag, x, y, 0.6)
    pag.evaluate("() => window.__pulso()")
    pag.mouse.click(x, y)
    pag.fill(seletor, "")
    for ch in texto:
        pag.type(seletor, ch, delay=0)
        salvar(pag, por_char)
    pausa(pag, 0.4)


def preparar(pag):
    pag.evaluate(TOQUE)
    pag.evaluate(LEGENDA)
    mover(pag, W / 2, H / 2)


with sync_playwright() as pw:
    nav = pw.chromium.launch(executable_path=str(CHROME))
    ctx = nav.new_context(viewport={"width": W, "height": H},
                          device_scale_factor=ESCALA,
                          is_mobile=True, has_touch=True,
                          reduced_motion="no-preference")
    pag = ctx.new_page()

    # ---------------------------------------------------------- passo 1 --
    pag.goto(ADMIN, wait_until="networkidle", timeout=60000)
    pag.wait_for_selector("#login:not([hidden])", timeout=30000)
    preparar(pag)
    pausa(pag, 0.8)

    legenda(pag, "PASSO 1",
            f"Só na primeira vez, digite:<br><b>{ENDERECO_VISIVEL}</b>", 4.2)

    # ---------------------------------------------------------- passo 2 --
    legenda(pag, "PASSO 2", "Seu e-mail", 1.2)
    escrever(pag, "#login-email", EMAIL)

    legenda(pag, "PASSO 3", "Sua senha", 1.2)
    escrever(pag, "#login-senha", SENHA, por_char=0.05)

    legenda(pag, "PASSO 4", "Toque em <b>Entrar</b>", 1.4)
    tocar(pag, "#login-botao", ler=0.4)

    pag.wait_for_selector("#painel:not([hidden])", timeout=40000)
    pag.wait_for_timeout(1200)
    legenda(pag, "PRONTO", "Você está dentro do painel", 3.2)

    # ---------------------------------------------------------- passo 5 --
    # A parte que motivou o video: voltar pro site e achar o atalho novo.
    legenda(pag, "AGORA O ATALHO", "Vamos voltar para o site", 2.4)
    pag.goto(SITE, wait_until="networkidle", timeout=60000)
    preparar(pag)
    pag.wait_for_selector("#painel-link:not([hidden])", timeout=20000)
    pag.wait_for_timeout(2600)          # deixa a abertura do hero terminar

    # Daqui ate o clique, a legenda vai pro RODAPE: o cabecalho e fixo no topo
    # e ela cobriria o botao que o video esta mandando olhar.
    legenda(pag, "OLHA AQUI", "Apareceu o botão <b>Painel</b>", 1.0, onde="rodape")
    halo(pag, "#painel-link", 3.4)
    halo(pag, None)

    legenda(pag, "IMPORTANTE",
            "Ele só aparece <b>pra você</b>.<br>Quem visita o site não vê.",
            4.0, onde="rodape")

    legenda(pag, "DE AGORA EM DIANTE", "Toque nele e pronto", 1.6, onde="rodape")
    tocar(pag, "#painel-link", ler=0.5)

    pag.wait_for_selector("#painel:not([hidden])", timeout=40000)
    preparar(pag)
    pag.wait_for_timeout(1000)
    legenda(pag, "VIU?", "Entrou <b>sem digitar senha</b> de novo", 4.0)

    legenda(pag, "RESUMINDO",
            "1ª vez: endereço + senha<br>Depois: só o botão <b>Painel</b>", 4.6)

    nav.close()

(SAIDA / "lista.txt").write_text(
    "".join(f"file '{n}'\nduration {d:.4f}\n" for n, d in frames)
    + f"file '{frames[-1][0]}'\n",
    encoding="utf-8",
)

ffmpeg = None
for cand in pathlib.Path.home().glob(
        "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"):
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
