/* =========================================================================
   ESTÚDIO E CONCEITO
   intro desenhada + fios de cabelo reativos + scroll scrubbing + parallax
   ========================================================================= */

gsap.registerPlugin(ScrollTrigger);

const suave = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------------------------------------------------------------- INTRO */

const fiosLogo = document.querySelectorAll('#logo-intro .fio');
fiosLogo.forEach(p => {
  const tam = p.getTotalLength();
  gsap.set(p, { strokeDasharray: tam, strokeDashoffset: tam });
});

const abertura = gsap.timeline();
abertura
  .to('#logo-intro .fio', {
    strokeDashoffset: 0,
    duration: 1.1,
    ease: 'power2.inOut',
    stagger: .13,
  })
  .to('#logo-intro .marca-nome', { opacity: 1, duration: .5 }, '-=.35')
  .to('#logo-intro .marca-sub', { opacity: 1, duration: .45 }, '-=.3')
  .to('.intro-marca', { scale: .94, duration: .5, ease: 'power2.inOut' }, '+=.4')
  .to('#intro', { yPercent: -100, duration: .8, ease: 'power4.inOut' }, '-=.2')
  .set('#intro', { display: 'none' })
  .to('#nav', { y: 0, duration: .6, ease: 'power3.out' }, '-=.35')
  .from('.hero-titulo .linha > span', {
    yPercent: 115,
    duration: 1,
    ease: 'power4.out',
    stagger: .1,
  }, '-=.45')
  .from('.etiqueta', { opacity: 0, y: 12, duration: .6 }, '-=.7')
  .from('.hero-texto, .hero-acoes, .hero-dados', {
    opacity: 0, y: 22, duration: .7, stagger: .1,
  }, '-=.55')
  .from('.hero-foto', { opacity: 0, scale: 1.06, duration: 1.1, ease: 'power3.out' }, '-=1');

/* --------------------------------------------------- CABELO (hero)
   Cada fio é uma cordinha de pontos com integração de Verlet: peso, vento e o
   empurrão do ponteiro se propagam nó a nó, então o fio DOBRA e volta sozinho
   em vez de balançar inteiro como uma linha rígida. A ponta se move mais que a
   raiz, que é o que dá a leitura de cabelo.

   Canvas em vez de SVG porque aqui são centenas de fios por quadro — com um
   <path> por fio o navegador reflui a árvore inteira e engasga no celular. */

const tela = document.getElementById('fios');
const ctx = tela && tela.getContext('2d');

if (ctx) (function cabelo() {
  const TOQUE = window.matchMedia('(hover: none)').matches;

  // [r, g, b, opacidade na raiz] — a ponta sempre desaparece no fundo
  const PALETA = [
    [120, 88, 42, .26],   // castanho
    [168, 126, 62, .28],  // bronze
    [192, 149, 74, .32],  // dourado da marca
    [230, 198, 127, .30], // dourado claro
    [90, 66, 32, .18],    // sombra
  ];

  // tabela de seno: com centenas de fios o Math.sin por nó vira o gargalo do
  // quadro. A perda de precisão não aparece num movimento orgânico como este.
  const TAU = Math.PI * 2, TAM = 2048;
  const SENO = new Float32Array(TAM);
  for (let i = 0; i < TAM; i++) SENO[i] = Math.sin((i / TAM) * TAU);
  const sen = a => SENO[(((a % TAU) + TAU) % TAU) * (TAM / TAU) | 0];

  // espessuras em degraus (e não contínuas) pra permitir agrupar o traçado
  const LARGURAS = [.5, .85, 1.35];

  let L = 0, A = 0, fios = [], grupos = [], rodando = true, t = 0;
  const alvo = { x: -9999, y: -9999 };   // ponteiro
  const atual = { x: -9999, y: -9999 };  // ponteiro suavizado

  function medir() {
    const r = tela.getBoundingClientRect();
    L = Math.max(1, r.width);
    A = Math.max(1, r.height);
    // teto no dpr: retina "pura" dobra o custo de pintura sem ganho visível
    const dpr = Math.min(window.devicePixelRatio || 1, L < 760 ? 1.5 : 2);
    tela.width = Math.round(L * dpr);
    tela.height = Math.round(A * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round';
  }

  function semear() {
    // densidade constante por espaço, não por faixa de tela: um fio a cada ~8px
    // mantém a mesma leitura de tecido no celular e no monitor grande (antes o
    // celular recebia fio demais pra pouca largura e virava listra). Se o
    // aparelho não der conta, vigiar() reduz isso em tempo de execução.
    const qtd = Math.max(45, Math.min(220, Math.round(L / 8)));
    const nos = L < 760 ? 13 : 16;
    // telas estreitas precisam de onda proporcionalmente maior, senão o fio
    // não tem espaço lateral pra curvar e sai reto
    const escala = Math.max(.78, Math.min(1, L / 900));
    // no celular o hero é bem mais alto que largo; sem um teto de comprimento o
    // fio estica e fica vertical. Limitar deixa a mecha caindo em cortina.
    const refA = Math.min(A, 820);

    fios = [];
    for (let i = 0; i < qtd; i++) {
      // distribuição irregular: fios perfeitamente espaçados parecem pente
      const base = (L + 120) * (i / qtd) - 60 + (Math.random() - .5) * (L / qtd) * 1.6;
      // comprimentos diferentes: as pontas terminam em alturas variadas, como
      // cabelo em camadas, em vez de todas na mesma linha
      const alcance = .68 + Math.random() * .52;
      const seg = (refA * alcance + 150) / (nos - 1);

      const x = new Float32Array(nos);
      const y = new Float32Array(nos);
      const ax = new Float32Array(nos);
      const ay = new Float32Array(nos);

      // cada fio já nasce com uma curvatura própria (a mecha cai torta, não reta)
      const ondaAmp = (16 + Math.random() * 44) * escala;
      const ondaFreq = .28 + Math.random() * .5;
      const ondaFase = Math.random() * Math.PI * 2;

      const repouso = new Float32Array(nos);
      for (let j = 0; j < nos; j++) {
        const peso = j / (nos - 1);
        repouso[j] = base + Math.sin(j * ondaFreq + ondaFase) * ondaAmp * peso;
        x[j] = ax[j] = repouso[j];
        y[j] = ay[j] = -70 + seg * j;
      }

      // cor sólida de propósito: um CanvasGradient por fio derruba o quadro pela
      // metade. A ponta some sob a camada #inicio::after, no CSS.
      const iCor = (Math.random() * PALETA.length) | 0;
      const iLarg = (Math.random() * LARGURAS.length) | 0;

      fios.push({
        x, y, ax, ay, nos, seg, repouso,
        raiz: base,
        fase: Math.random() * Math.PI * 2,
        vel: .45 + Math.random() * .45,
        amp: .9 + Math.random() * 1.3,
        grupo: iCor * LARGURAS.length + iLarg,
      });
    }

    // Um stroke() por fio custa caro: no monitor grande são ~240 traçados por
    // quadro. Agrupando por cor+espessura, o mesmo desenho sai em ~15.
    grupos = [];
    for (let c = 0; c < PALETA.length; c++) {
      const [r, g, b, op] = PALETA[c];
      for (let w = 0; w < LARGURAS.length; w++) {
        grupos.push({ cor: `rgba(${r},${g},${b},${op})`, larg: LARGURAS[w], lista: [] });
      }
    }
    for (const fio of fios) grupos[fio.grupo].lista.push(fio);
    janelaIni = 0; cortes = 0;
  }

  function fisica() {
    t += PASSO;
    // ponteiro com inércia: o empurrão vira carícia, não teleporte
    atual.x += (alvo.x - atual.x) * .14;
    atual.y += (alvo.y - atual.y) * .14;

    const raio = L < 760 ? 90 : 130;
    const raio2 = raio * raio;

    for (let f = 0; f < fios.length; f++) {
      const fio = fios[f];
      const { x, y, ax, ay, nos, seg, repouso } = fio;

      // sopro lento e global + respiração própria de cada fio
      const brisa = sen(t * .35 + fio.raiz * .004) * .35;

      for (let j = 1; j < nos; j++) {
        const peso = j / (nos - 1);              // ponta pesa/balança mais
        const vx = (x[j] - ax[j]) * .955;        // atrito: maleável, sem elástico
        const vy = (y[j] - ay[j]) * .955;
        ax[j] = x[j];
        ay[j] = y[j];

        const vento = (sen(t * fio.vel + j * .38 + fio.fase) + brisa) * fio.amp * peso;
        x[j] += vx + vento;
        y[j] += vy + .12 * peso;                 // gravidade suave

        // memória de forma: o fio sempre tende de volta à própria curva de
        // repouso. Sem isso a costura endireita tudo e vira palha vertical.
        x[j] += (repouso[j] - x[j]) * .022;

        // empurrão do ponteiro
        const dx = x[j] - atual.x;
        const dy = y[j] - atual.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < raio2) {
          const d = Math.sqrt(d2) || .001;
          const forca = (1 - d / raio) * 1.9;
          x[j] += (dx / d) * forca;
          y[j] += (dy / d) * forca;
        }
      }

      // costura: cada nó volta pra distância certa do nó de cima (a raiz não sai
      // do lugar). Duas passadas bastam pro fio parecer inteiro sem endurecer.
      for (let it = 0; it < 2; it++) {
        x[0] = fio.raiz;
        y[0] = -70;
        for (let j = 1; j < nos; j++) {
          const dx = x[j] - x[j - 1];
          const dy = y[j] - y[j - 1];
          const d = Math.sqrt(dx * dx + dy * dy) || .001;
          const dif = (d - seg) / d;
          x[j] -= dx * dif;
          y[j] -= dy * dif;
        }
      }

    }
  }

  function pintar() {
    ctx.clearRect(0, 0, L, A);
    for (let g = 0; g < grupos.length; g++) {
      const grupo = grupos[g];
      if (!grupo.lista.length) continue;

      ctx.beginPath();
      for (let f = 0; f < grupo.lista.length; f++) {
        const { x, y, nos } = grupo.lista[f];
        // traço suave: curva pelos pontos médios, sem quinas nos nós
        ctx.moveTo(x[0], y[0]);
        for (let j = 1; j < nos - 1; j++) {
          ctx.quadraticCurveTo(x[j], y[j], (x[j] + x[j + 1]) / 2, (y[j] + y[j + 1]) / 2);
        }
        ctx.lineTo(x[nos - 1], y[nos - 1]);
      }
      ctx.strokeStyle = grupo.cor;
      ctx.lineWidth = grupo.larg;
      ctx.stroke();
    }
  }

  // Passo de tempo fixo com acumulador. Sem isso a física andaria junto com a
  // taxa de quadros: em tela de 120Hz o cabelo se mexe o dobro da velocidade e
  // em máquina fraca vira câmera lenta. Assim o movimento fica igual em todo
  // aparelho — e é o que dá a suavidade constante.
  const PASSO = 1 / 60;
  let ultimo = 0, acumulado = 0;

  function quadro(agora) {
    if (!rodando) return;
    // A 1ª chamada pode vir sem timestamp (quando disparada na mão, não pelo
    // rAF). Sem esta guarda, `agora - ultimo` vira NaN, contamina o acumulador
    // e a física nunca mais roda — o cabelo fica pintado, porém congelado.
    if (!Number.isFinite(agora)) { requestAnimationFrame(quadro); return; }
    if (!ultimo) ultimo = agora;
    // teto de 100ms: ao voltar de outra aba, não despejar um tranco de física
    acumulado += Math.min((agora - ultimo) / 1000, .1);
    ultimo = agora;

    let voltas = 0;
    while (acumulado >= PASSO && voltas < 2) {
      fisica();
      acumulado -= PASSO;
      voltas++;
    }
    pintar();
    vigiar(agora);
    requestAnimationFrame(quadro);
  }

  // Aparelho fraco não avisa: em vez de chutar uma densidade "segura" pra todo
  // mundo, começa cheio e vai tirando fio se o quadro não estiver fechando.
  // Some o excesso sem o visitante perceber, e quem tem máquina boa fica com a
  // malha inteira.
  let janelaIni = 0, janelaQtd = 0, cortes = 0, ruins = 0;
  function vigiar(agora) {
    if (cortes >= 3 || fios.length <= 50) return;
    if (!janelaIni) { janelaIni = agora; janelaQtd = 0; return; }
    janelaQtd++;
    const dur = agora - janelaIni;
    if (dur < 1500) return;

    const fps = janelaQtd / (dur / 1000);
    janelaIni = agora;
    janelaQtd = 0;

    // Limiar baixo de propósito: só corta quando está realmente ruim. Janela sem
    // foco, monitor em economia e afins seguram o quadro em 30fps sem que o site
    // esteja pesado — cortar aí seria estragar o visual à toa.
    if (fps < 26) {
      if (++ruins < 2) return;
      ruins = 0;
      fios = fios.filter((_, i) => i % 3 !== 0);   // tira ~1/3 dos fios
      for (const g of grupos) g.lista.length = 0;
      for (const fio of fios) grupos[fio.grupo].lista.push(fio);
      cortes++;
    } else {
      ruins = 0;
    }
  }

  function ligar() {
    if (rodando) return;
    rodando = true;
    requestAnimationFrame(quadro);
  }
  function desligar() { rodando = false; }

  medir();
  semear();

  // "Movimento reduzido" não é "tela congelada": quem liga isso (no Windows é o
  // padrão de quem desativou as animações do sistema) quer menos agitação, não
  // um fundo morto. Então o cabelo continua respirando, só que devagar e sem
  // reagir ao ponteiro — nada de movimento brusco ou que persiga o cursor.
  function acalmar() {
    for (const fio of fios) {
      fio.amp *= .38;
      fio.vel *= .55;
    }
  }

  if (suave) {
    acalmar();
    requestAnimationFrame(quadro);
  } else {
    requestAnimationFrame(quadro);

    if (!TOQUE) {
      window.addEventListener('pointermove', e => {
        const r = tela.getBoundingClientRect();
        alvo.x = e.clientX - r.left;
        alvo.y = e.clientY - r.top;
      }, { passive: true });
      window.addEventListener('pointerleave', () => { alvo.x = alvo.y = -9999; }, { passive: true });
    } else {
      // no celular o dedo passa rolando: reage ao toque e solta depois
      window.addEventListener('touchmove', e => {
        const p = e.touches[0];
        if (!p) return;
        const r = tela.getBoundingClientRect();
        alvo.x = p.clientX - r.left;
        alvo.y = p.clientY - r.top;
      }, { passive: true });
      window.addEventListener('touchend', () => { alvo.x = alvo.y = -9999; }, { passive: true });
    }

    // não gastar bateria com o hero fora da tela nem com a aba escondida
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([e]) => (e.isIntersecting ? ligar() : desligar()),
        { threshold: 0 }).observe(tela);
    }
    document.addEventListener('visibilitychange', () => {
      document.hidden ? desligar() : ligar();
    });
  }

  let atraso;
  window.addEventListener('resize', () => {
    clearTimeout(atraso);
    atraso = setTimeout(() => {
      const antes = L;
      medir();
      // no celular, rolar mostra/esconde a barra do navegador e dispara resize
      // à toa; refazer a malha só quando a largura muda de verdade
      if (Math.abs(L - antes) > 2) {
        semear();
        if (suave) acalmar();   // a malha nova nasce com o movimento cheio
      }
    }, 180);
  }, { passive: true });
})();

/* ------------------------------------------------------- ÍCONES (serviços)
   Cada traço do ícone se desenha quando o card entra na tela. */

document.querySelectorAll('[data-svc]').forEach((card, i) => {
  const tracos = card.querySelectorAll('.tr');
  tracos.forEach(p => {
    const tam = p.getTotalLength();
    gsap.set(p, { strokeDasharray: tam, strokeDashoffset: tam });
  });

  gsap.timeline({
    scrollTrigger: { trigger: card, start: 'top 84%' },
  })
    .from(card, { opacity: 0, y: 40, duration: .8, ease: 'power3.out', delay: i * .08 })
    .to(tracos, { strokeDashoffset: 0, duration: 1.1, ease: 'power2.inOut', stagger: .12 }, '-=.5');
});

/* ------------------------------------------- TRANSFORMAÇÕES (scrubbing)
   A faixa horizontal anda conforme o scroll vertical: a seção fica presa
   na tela e o trilho desliza junto com a rolagem. */

const trilho = document.querySelector('.trilho-interno');
if (trilho && window.innerWidth > 760) {
  const percurso = () => trilho.scrollWidth - window.innerWidth;

  gsap.to(trilho, {
    x: () => -percurso(),
    ease: 'none',
    scrollTrigger: {
      trigger: '#transformacoes',
      start: 'top top',
      end: () => '+=' + percurso(),
      pin: true,
      scrub: 1,
      invalidateOnRefresh: true,
    },
  });

  // cada foto entra com um leve deslize enquanto o trilho passa
  gsap.utils.toArray('.painel-foto').forEach(foto => {
    gsap.from(foto, {
      y: 60,
      opacity: 0,
      duration: .8,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: foto,
        containerAnimation: gsap.getTweensOf(trilho)[0],
        start: 'left 92%',
      },
    });
  });
}

/* ------------------------------------------------------------- PARALLAX */

if (!suave) {
  gsap.utils.toArray('[data-parallax]').forEach(el => {
    const forca = parseFloat(el.dataset.parallax) || .12;
    const img = el.querySelector('img') || el;
    gsap.fromTo(img,
      { yPercent: -forca * 100 },
      {
        yPercent: forca * 100,
        ease: 'none',
        scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true },
      });
  });
}

/* ------------------------------------------------- REVELAÇÕES DE SEÇÃO */

gsap.utils.toArray('.titulo-secao').forEach(tit => {
  gsap.from(tit, {
    opacity: 0,
    y: 46,
    duration: 1,
    ease: 'power3.out',
    scrollTrigger: { trigger: tit, start: 'top 86%' },
  });
});

gsap.utils.toArray('[data-item]').forEach((item, i) => {
  gsap.from(item, {
    opacity: 0,
    x: -26,
    duration: .8,
    ease: 'power3.out',
    delay: i * .12,
    scrollTrigger: { trigger: item, start: 'top 88%' },
  });
});

gsap.utils.toArray('.casa-foto, .casa-info').forEach((el, i) => {
  gsap.from(el, {
    opacity: 0,
    y: 50,
    duration: .9,
    ease: 'power3.out',
    delay: i * .1,
    scrollTrigger: { trigger: el, start: 'top 88%' },
  });
});

gsap.from('.contato-caixa', {
  opacity: 0,
  scale: .96,
  duration: 1,
  ease: 'power3.out',
  scrollTrigger: { trigger: '.contato-caixa', start: 'top 86%' },
});

/* nav ganha sombra ao sair do topo */
ScrollTrigger.create({
  start: 'top -80',
  onUpdate: self => {
    gsap.to('#nav', {
      boxShadow: self.progress > 0 ? '0 10px 30px rgba(90,64,22,.10)' : 'none',
      duration: .3,
    });
  },
});

window.addEventListener('load', () => ScrollTrigger.refresh());

/* ---------------------------------------------------- PROVADOR DE COR
   Uma mecha de fios desenhada em canvas. Ao escolher um tom na paleta, a cor
   de cada fio migra suavemente do valor atual para o novo, num degradê
   raiz→ponta. Mesmo motivo de "fio de cabelo" do hero, aqui a serviço de deixar
   a pessoa provar a cor antes de sentar na cadeira. */

(function provador() {
  const tela = document.getElementById('mecha');
  if (!tela) return;
  const ctx = tela.getContext('2d');
  const paleta = document.querySelector('.paleta');
  const rotulo = document.querySelector('.tom-nome');
  const botaoAgendar = document.getElementById('tom-agendar');

  // hex "#rrggbb" -> [r,g,b]
  const rgb = h => {
    const n = parseInt(h.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  };
  const misturar = (a, b, t) => [
    a[0] + (b[0] - a[0]) * t,
    a[1] + (b[1] - a[1]) * t,
    a[2] + (b[2] - a[2]) * t,
  ];

  // tom atual e tom-alvo (a transição acontece entre os dois)
  const inicial = document.querySelector('.tom.selecionado') || document.querySelector('.tom');
  let raizAtual = rgb(inicial.dataset.raiz);
  let pontaAtual = rgb(inicial.dataset.ponta);
  let raizAlvo = raizAtual.slice();
  let pontaAlvo = pontaAtual.slice();

  let L = 0, A = 0, fios = [], t = 0, rodando = true;

  function medir() {
    const r = tela.getBoundingClientRect();
    L = Math.max(1, r.width);
    A = Math.max(1, r.height);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    tela.width = Math.round(L * dpr);
    tela.height = Math.round(A * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round';
  }

  function semear() {
    const qtd = Math.max(26, Math.min(64, Math.round(L / 9)));
    fios = [];
    for (let i = 0; i < qtd; i++) {
      // fios saem de um topo estreito (como preso no alto) e abrem descendo
      const espalha = (i / (qtd - 1) - .5);
      const topo = L * (.5 + espalha * .18) + (Math.random() - .5) * 6;
      fios.push({
        topo,
        // quanto o fio abre até a ponta — as bordas caem mais pra fora
        abre: espalha * L * .62 + (Math.random() - .5) * 22,
        comp: .82 + Math.random() * .18,          // fração da altura
        amp: 6 + Math.random() * 16,              // onda do fio
        freq: 1.1 + Math.random() * 1.6,
        fase: Math.random() * Math.PI * 2,
        vel: .5 + Math.random() * .5,
        larg: .6 + Math.random() * 1.5,
        // cada fio pega o degradê num ponto ligeiramente diferente: dá volume
        matiz: .82 + Math.random() * .32,
      });
    }
  }

  function pintar() {
    ctx.clearRect(0, 0, L, A);
    for (const f of fios) {
      const nos = 14;
      const baseY = -8;
      const fim = A * f.comp;

      ctx.beginPath();
      let px = f.topo, py = baseY;
      ctx.moveTo(px, py);
      for (let j = 1; j <= nos; j++) {
        const p = j / nos;                          // 0 raiz -> 1 ponta
        const solto = p * p;                        // abre mais perto da ponta
        const balanco = sen(t * f.vel + p * f.freq * 3 + f.fase) * f.amp * p;
        const x = f.topo + f.abre * solto + balanco;
        const y = baseY + fim * p;
        const mx = (px + x) / 2, my = (py + y) / 2;
        ctx.quadraticCurveTo(px, py, mx, my);
        px = x; py = y;
      }
      // cor do fio: degradê raiz->ponta com leve variação por fio
      const grad = ctx.createLinearGradient(0, baseY, 0, fim);
      const cr = raizAtual, cp = pontaAtual;
      grad.addColorStop(0, `rgb(${cr[0]|0},${cr[1]|0},${cr[2]|0})`);
      const meio = misturar(cr, cp, .55 * f.matiz);
      grad.addColorStop(.5, `rgb(${meio[0]|0},${meio[1]|0},${meio[2]|0})`);
      grad.addColorStop(1, `rgba(${cp[0]|0},${cp[1]|0},${cp[2]|0},.85)`);
      ctx.strokeStyle = grad;
      ctx.lineWidth = f.larg;
      ctx.stroke();
    }
  }

  // tabela de seno própria (o hero tem a dele em outro escopo)
  const TAU = Math.PI * 2, TAM = 1024;
  const SENO = new Float32Array(TAM);
  for (let i = 0; i < TAM; i++) SENO[i] = Math.sin((i / TAM) * TAU);
  const sen = a => SENO[(((a % TAU) + TAU) % TAU) * (TAM / TAU) | 0];

  function quadro() {
    if (!rodando) return;
    t += suave ? .006 : .016;
    // a cor caminha até o alvo (transição macia ao trocar o tom)
    raizAtual = misturar(raizAtual, raizAlvo, .09);
    pontaAtual = misturar(pontaAtual, pontaAlvo, .09);
    pintar();
    requestAnimationFrame(quadro);
  }

  function escolher(botao) {
    document.querySelectorAll('.tom').forEach(b => {
      b.classList.toggle('selecionado', b === botao);
      b.setAttribute('aria-checked', b === botao ? 'true' : 'false');
    });
    raizAlvo = rgb(botao.dataset.raiz);
    pontaAlvo = rgb(botao.dataset.ponta);

    const nome = botao.dataset.nome;
    if (rotulo) {
      rotulo.style.opacity = '0';
      setTimeout(() => { rotulo.textContent = nome; rotulo.style.opacity = '1'; }, 160);
    }
    if (botaoAgendar) {
      const msg = `Oi! Me apaixonei pelo tom ${nome} no site e queria avaliar se fica bem em mim`;
      botaoAgendar.href = 'https://wa.me/5585991899554?text=' + encodeURIComponent(msg);
    }
  }

  if (paleta) {
    paleta.addEventListener('click', e => {
      const botao = e.target.closest('.tom');
      if (botao) escolher(botao);
    });
    // acessível por teclado: setas andam pela paleta
    paleta.addEventListener('keydown', e => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const tons = [...document.querySelectorAll('.tom')];
      const i = tons.indexOf(document.querySelector('.tom.selecionado'));
      const prox = tons[(i + (e.key === 'ArrowRight' ? 1 : tons.length - 1)) % tons.length];
      prox.focus(); escolher(prox); e.preventDefault();
    });
  }

  medir();
  semear();
  requestAnimationFrame(quadro);

  // só anima quando está à vista
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => {
      if (e.isIntersecting && !rodando) { rodando = true; requestAnimationFrame(quadro); }
      else if (!e.isIntersecting) { rodando = false; }
    }, { threshold: 0 }).observe(tela);
  }

  let atraso;
  window.addEventListener('resize', () => {
    clearTimeout(atraso);
    atraso = setTimeout(() => { medir(); semear(); }, 180);
  }, { passive: true });
})();
