/* =========================================================
   PORTFÓLIO: lógica e animações
   (os dados editáveis ficam em js/data.js)
   ========================================================= */

gsap.registerPlugin(ScrollTrigger);

const $ = (s, el = document) => el.querySelector(s);
const iconUrl = (icon) => `https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/${icon}.svg`;

/* ===== preenche textos do perfil ===== */
/* chips do hero usam o símbolo puro da linguagem (sem moldura), via Simple Icons */
const CHIP_ICON = { JavaScript: "javascript", TypeScript: "typescript", React: "react", "Node.js": "nodedotjs", Python: "python", HTML: "html5" };
$("#hero-tags").innerHTML = SKILLS.slice(0, 6).map((s) =>
  `<span><img src="https://cdn.simpleicons.org/${CHIP_ICON[s.nome] || s.nome.toLowerCase()}/${s.cor.slice(1)}" alt="" loading="lazy" decoding="async" />${s.nome}</span>`).join("");
$("#link-cv").href = PERFIL.cv;

$("#cracha-nome").textContent = PERFIL.nome;
$("#cracha-titulo").textContent = PERFIL.titulo;
$("#cracha-local").textContent = PERFIL.local;

$("#link-email").href = `mailto:${PERFIL.email}`;
$("#link-whats").href = `https://wa.me/${PERFIL.whatsapp}`;
$("#sociais").innerHTML = [
  ["GitHub", PERFIL.github, "https://cdn.simpleicons.org/github/e8ecf8"],
  ["LinkedIn", PERFIL.linkedin, iconUrl("linkedin/linkedin-original")],
  ["Instagram", PERFIL.instagram, "https://cdn.simpleicons.org/instagram/e4405f"],
  ["E-mail", `mailto:${PERFIL.email}`, "https://cdn.simpleicons.org/gmail/ea4335"],
].map(([nome, url, icone]) =>
  `<a href="${url}" target="_blank" rel="noopener"><img src="${icone}" alt="" loading="lazy" decoding="async" />${nome} ↗</a>`).join("");
$("#ano").textContent = new Date().getFullYear();

/* ===== efeito de digitação no hero (escreve, apaga, próxima frase) ===== */
const typeEl = $("#type-text");
let fraseAtual = 0, charAtual = 0, apagando = false;

function digita() {
  const frase = PERFIL.frases[fraseAtual];
  charAtual += apagando ? -1 : 1;
  typeEl.textContent = frase.slice(0, charAtual);

  let espera = apagando ? 38 : 72;                 // apagar é mais rápido que escrever
  if (!apagando && charAtual === frase.length) {
    espera = 2100;                                  // pausa com a frase completa
    apagando = true;
  } else if (apagando && charAtual === 0) {
    apagando = false;
    fraseAtual = (fraseAtual + 1) % PERFIL.frases.length;
    espera = 420;                                   // respiro antes da próxima
  }
  setTimeout(digita, espera);
}
digita();

/* =========================================================
   TECLADO 3D DE SKILLS
   ========================================================= */
const keyboard = $("#keyboard");

SKILLS.forEach((skill, i) => {
  const key = document.createElement("div");
  key.className = "key";
  key.style.setProperty("--c", skill.cor);
  key.dataset.index = i;
  const conteudo = skill.icon
    ? `<img src="${iconUrl(skill.icon)}" alt="${skill.nome}" loading="lazy" decoding="async" />`
    : `<span class="key-txt">${skill.text}</span>`;
  key.innerHTML = `
    <div class="key-cap">
      <div class="key-top">${conteudo}</div>
      <div class="key-face f-front"></div>
      <div class="key-face f-right"></div>
      <div class="key-face f-left"></div>
    </div>`;
  key.addEventListener("pointerenter", () => pressKey(i, false));
  key.addEventListener("click", () => pressKey(i, true));
  keyboard.appendChild(key);
});

const callout = $("#skill-callout");
const calloutNome = $("#skill-callout-nome");
const calloutTag = $("#skill-callout-tag");
let calloutTimer;

function pressKey(i, mostrarCallout = true) {
  const skill = SKILLS[i];
  const cap = keyboard.children[i].querySelector(".key-cap");

  cap.classList.add("pressed");
  setTimeout(() => cap.classList.remove("pressed"), 140);

  if (!mostrarCallout) return;
  calloutNome.textContent = skill.nome;
  calloutTag.textContent = skill.tag;

  gsap.killTweensOf(callout);
  gsap.fromTo(
    callout,
    { opacity: 0, x: -70, scale: 0.85, rotate: -12 },
    { opacity: 1, x: 0, scale: 1, rotate: -8, duration: 0.35, ease: "back.out(2)" }
  );
  clearTimeout(calloutTimer);
  calloutTimer = setTimeout(() => {
    gsap.to(callout, { opacity: 0, x: 40, duration: 0.3, ease: "power2.in" });
  }, 1800);
}

/* teclas físicas acionam as keycaps (como no vídeo) */
document.addEventListener("keydown", (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key.toLowerCase();
  let i = SKILLS.findIndex((s) => s.key === k);
  if (i === -1 && /^[a-z0-9]$/.test(k)) i = Math.floor(Math.random() * SKILLS.length);
  if (i !== -1) pressKey(i, true);
});

/* =========================================================
   CRACHÁ: física elástica realista
   O cartão é um corpo com massa pendurado numa fita-mola:
   dá pra puxar em QUALQUER direção, a fita estica e ele
   volta quicando, com balanço angular próprio.
   ========================================================= */
const lanyard = $("#lanyard");
const strapArm = $("#strap-arm");
const crachaArm = $("#cracha-arm");

let px = 0, py = 0, vx = 0, vy = 0;      // posição/velocidade do cartão
let ang = 0, angV = 0;                    // rotação própria do cartão
let arrasto = null;                       // {x0, y0, px0, py0} durante o drag
let t0 = performance.now();

lanyard.addEventListener("pointerdown", (e) => {
  lanyard.setPointerCapture(e.pointerId);
  arrasto = { x0: e.clientX, y0: e.clientY, px0: px, py0: py };
});
lanyard.addEventListener("pointermove", (e) => {
  if (arrasto) { arrasto.x = e.clientX; arrasto.y = e.clientY; }
});
["pointerup", "pointercancel"].forEach((ev) =>
  lanyard.addEventListener(ev, () => { arrasto = null; })
);

/* pausa a física quando o crachá sai da tela (economia de bateria) */
let crachaVisivel = true;
new IntersectionObserver(([e]) => (crachaVisivel = e.isIntersecting)).observe(lanyard);

/* rolar a página faz o crachá quicar na vertical */
let ultimoScroll = window.scrollY;
window.addEventListener("scroll", () => {
  vy += (window.scrollY - ultimoScroll) * 0.35;
  ultimoScroll = window.scrollY;
}, { passive: true });

function fisica(now) {
  const dt = Math.min((now - t0) / 1000, 0.04);
  t0 = now;

  if (!crachaVisivel && !arrasto) { requestAnimationFrame(fisica); return; }

  if (arrasto && arrasto.x !== undefined) {
    // o cartão persegue o dedo com uma mola firme (sensação de peso)
    const txAlvo = arrasto.px0 + (arrasto.x - arrasto.x0);
    const tyAlvo = arrasto.py0 + (arrasto.y - arrasto.y0);
    vx += ((txAlvo - px) * 320 - vx * 26) * dt;
    vy += ((tyAlvo - py) * 320 - vy * 26) * dt;
  } else {
    // solto: mola elástica puxa de volta pro repouso, com pouco atrito
    vx += (-px * 70 - vx * 4.5) * dt;
    vy += (-py * 90 - vy * 5.5) * dt;
    vx += Math.sin(now / 1300) * 2.2 * dt; // brisa constante
  }
  px += vx * dt;
  py += vy * dt;

  // a fita estica: aponta e escala do topo até o furo do cartão
  const L = strapArm.offsetHeight || 200;
  const dx = px, dy = L + py;
  const rot = Math.atan2(-dx, Math.max(dy, 40)) * (180 / Math.PI);
  const estica = Math.max(Math.hypot(dx, dy) / L, 0.25);
  gsap.set(strapArm, { rotation: rot, scaleY: estica });

  // o cartão tenta se alinhar com a fita, mas com atraso (rebolado)
  angV += ((rot - ang) * 55 - angV * 5) * dt;
  ang += angV * dt;
  gsap.set(crachaArm, { x: px, y: py, rotation: ang });

  requestAnimationFrame(fisica);
}
requestAnimationFrame(fisica);

/* brilho passando no crachá de tempos em tempos */
gsap.to(".cracha-brilho", { xPercent: 240, duration: 1.4, ease: "power2.inOut", repeat: -1, repeatDelay: 4 });

/* =========================================================
   PROJETOS: cards + filtros por categoria
   ========================================================= */
const grid = $("#projetos-grid");
const filtros = $("#filtros");
const categorias = ["Todos", ...new Set(PROJETOS.map((p) => p.categoria))];

function renderProjetos(cat) {
  const lista = cat === "Todos" ? PROJETOS : PROJETOS.filter((p) => p.categoria === cat);
  grid.innerHTML = lista.map((p) => `
    <article class="card" style="--c:${p.cor}">
      <div class="card-capa">
        ${p.capa ? `<img src="${p.capa}" alt="${p.titulo}"${p.capaContain ? ' class="contain"' : ""} loading="lazy" decoding="async" />` : ""}
        <span class="card-cat">${p.categoria}</span>
      </div>
      <div class="card-corpo">
        <h3>${p.titulo}</h3>
        <p>${p.desc}</p>
        <div class="card-stack">${p.stack.map((s) => `<span>${s}</span>`).join("")}</div>
        <div class="card-links">
          ${p.link ? `<a href="${p.link}" target="_blank" rel="noopener">ver online ↗</a>` : ""}
          ${p.repo ? `<a href="${p.repo}" target="_blank" rel="noopener">código ↗</a>` : ""}
          ${!p.link && !p.repo ? `<span class="sem-link">em breve_</span>` : ""}
        </div>
      </div>
    </article>`).join("");
  gsap.from(grid.children, { opacity: 0, y: 32, stagger: 0.07, duration: 0.5, ease: "power2.out", clearProps: "all" });
}

filtros.innerHTML = categorias.map((c) =>
  `<button class="filtro${c === "Todos" ? " ativo" : ""}" data-cat="${c}">${c}</button>`).join("");
filtros.addEventListener("click", (e) => {
  const btn = e.target.closest(".filtro");
  if (!btn) return;
  filtros.querySelectorAll(".filtro").forEach((b) => b.classList.toggle("ativo", b === btn));
  renderProjetos(btn.dataset.cat);
});
renderProjetos("Todos");

/* =========================================================
   CERTIFICADOS
   ========================================================= */
$("#certs-grid").innerHTML = CERTIFICADOS.map((c) => `
  <article class="cert" style="--c:${c.cor}">
    <div class="cert-logo"><img src="${c.logo || iconUrl(c.icon)}" alt="${c.emissor}" loading="lazy" decoding="async" /></div>
    <div class="cert-corpo">
      <h3>${c.titulo}</h3>
      <span class="cert-meta">${c.emissor} • ${c.ano}</span>
      <p>${c.desc}</p>
      ${c.arquivo ? `<a class="cert-link" href="${c.arquivo}" target="_blank" rel="noopener">ver certificado ↗</a>` : ""}
    </div>
  </article>`).join("");

/* =========================================================
   ANIMAÇÕES DE SCROLL (o "passeio" pelo fundo)
   ========================================================= */

/* intro do hero */
gsap.timeline({ defaults: { ease: "power3.out" } })
  .from(".hero-titulo .linha", { opacity: 0, y: 60, stagger: 0.12, duration: 0.7 }, 0.15)
  .from([".hero-type", ".hero-tags", ".hero-cta"], { opacity: 0, y: 24, stagger: 0.08, duration: 0.5 }, 0.45)
  .from(".lanyard", { y: -560, duration: 1.1, ease: "bounce.out", onComplete: () => { vy += 380; vx += 60; } }, 0.3);

/* fundo desloca conforme rola a página, sensação de passear pelo cenário */
gsap.to(".bg", {
  xPercent: -6, yPercent: -9,
  ease: "none",
  scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1.2 },
});
gsap.to(".bg-tinta-mov", {
  y: 640,
  ease: "none",
  scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1.2 },
});

/* SKILLS: seção fica presa e o teclado entra com scrub */
const keys = gsap.utils.toArray(".key");
gsap.set(".keyboard", { rotateX: 48, rotateZ: -38 });

const skillsTl = gsap.timeline({
  scrollTrigger: {
    trigger: ".skills",
    start: "top top",
    end: "+=130%",
    pin: ".skills-pin",
    scrub: 0.8,
  },
})
  .fromTo(".skills .titulo-gigante", { scale: 2.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35 })
  .fromTo(".keyboard", { rotateX: 72, rotateZ: -8, y: 260 }, { rotateX: 48, rotateZ: -38, y: 0, duration: 0.6 }, 0.1)
  .fromTo(keys, { z: 420, opacity: 0 }, { z: 0, opacity: 1, stagger: { each: 0.02, from: "random" }, duration: 0.45 }, 0.25)
  .fromTo(".skills-hint", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 0.8);

/* clicar em "Skills" no menu leva ao fim do pin, com o teclado já montado */
document.querySelectorAll('a[href="#skills"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({ top: skillsTl.scrollTrigger.end, behavior: "smooth" });
  });
});

/* títulos gigantes das outras seções passeiam mais rápido que o resto */
gsap.utils.toArray(".secao .titulo-gigante[data-parallax]").forEach((el) => {
  gsap.fromTo(el, { yPercent: 45, opacity: 0.15 }, {
    yPercent: -12, opacity: 1,
    ease: "none",
    scrollTrigger: { trigger: el, start: "top bottom", end: "bottom 30%", scrub: 1 },
  });
});

/* cards sobem ao entrar na tela */
ScrollTrigger.batch(".card, .cert", {
  start: "top 88%",
  once: true,
  onEnter: (els) => gsap.from(els, { opacity: 0, y: 44, stagger: 0.08, duration: 0.6, ease: "power2.out", clearProps: "opacity,transform" }),
});

/* contato */
gsap.from(".contato-acoes, .sociais", {
  opacity: 0, y: 30, stagger: 0.15, duration: 0.6,
  scrollTrigger: { trigger: ".contato", start: "top 70%" },
});
