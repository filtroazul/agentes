/* =========================================================
   PORTFÓLIO — lógica e animações
   (os dados editáveis ficam em js/data.js)
   ========================================================= */

gsap.registerPlugin(ScrollTrigger);

const $ = (s, el = document) => el.querySelector(s);
const iconUrl = (icon) => `https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/${icon}.svg`;

/* ===== preenche textos do perfil ===== */
$("#hero-disponivel").append(PERFIL.disponivel);
$("#hero-usuario").textContent = `// @${PERFIL.usuario} — ${PERFIL.titulo}_`;
$("#hero-bio").textContent = PERFIL.bio;
$("#hero-tags").innerHTML = SKILLS.slice(0, 6).map((s) => `<span>${s.nome}</span>`).join("");

$("#cracha-nome").textContent = PERFIL.nome;
$("#cracha-titulo").textContent = PERFIL.titulo;
$("#cracha-local").textContent = PERFIL.local;

$("#link-email").href = `mailto:${PERFIL.email}`;
$("#link-whats").href = `https://wa.me/${PERFIL.whatsapp}`;
$("#sociais").innerHTML = [
  ["GitHub", PERFIL.github],
  ["LinkedIn", PERFIL.linkedin],
  ["Instagram", PERFIL.instagram],
  ["E-mail", `mailto:${PERFIL.email}`],
].map(([nome, url]) => `<a href="${url}" target="_blank" rel="noopener">${nome} ↗</a>`).join("");
$("#ano").textContent = new Date().getFullYear();

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
    ? `<img src="${iconUrl(skill.icon)}" alt="${skill.nome}" />`
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
   CRACHÁ — física de pêndulo + arrastar
   ========================================================= */
const lanyard = $("#lanyard");
let angulo = 0, vel = 0, alvo = null, t0 = performance.now();

function pivot() {
  const r = lanyard.getBoundingClientRect();
  // com rotação aplicada o rect muda; usa o centro-x e o topo aproximado
  return { x: r.left + r.width / 2, y: r.top };
}

lanyard.addEventListener("pointerdown", (e) => {
  lanyard.setPointerCapture(e.pointerId);
  alvo = e;
});
lanyard.addEventListener("pointermove", (e) => { if (alvo) alvo = e; });
["pointerup", "pointercancel"].forEach((ev) =>
  lanyard.addEventListener(ev, () => { alvo = null; })
);

function fisica(now) {
  const dt = Math.min((now - t0) / 1000, 0.05);
  t0 = now;

  if (alvo) {
    const p = pivot();
    const desejado = Math.atan2(alvo.clientX - p.x, Math.max(alvo.clientY - p.y, 40)) * (180 / Math.PI);
    vel = (desejado - angulo) * 14;
    angulo += vel * dt * 4;
  } else {
    const mola = -14 * angulo;         // volta pro centro
    const atrito = -1.6 * vel;
    vel += (mola + atrito) * dt * 4;
    angulo += vel * dt;
    angulo += Math.sin(now / 1400) * 0.006; // balanço sutil constante
  }
  angulo = Math.max(-60, Math.min(60, angulo));
  gsap.set(lanyard, { rotation: angulo });
  requestAnimationFrame(fisica);
}
requestAnimationFrame(fisica);

/* brilho passando no crachá de tempos em tempos */
gsap.to(".cracha-brilho", { xPercent: 240, duration: 1.4, ease: "power2.inOut", repeat: -1, repeatDelay: 4 });

/* =========================================================
   PROJETOS — cards + filtros por categoria
   ========================================================= */
const grid = $("#projetos-grid");
const filtros = $("#filtros");
const categorias = ["Todos", ...new Set(PROJETOS.map((p) => p.categoria))];

function renderProjetos(cat) {
  const lista = cat === "Todos" ? PROJETOS : PROJETOS.filter((p) => p.categoria === cat);
  grid.innerHTML = lista.map((p) => `
    <article class="card" style="--c:${p.cor}">
      <div class="card-capa"><span class="card-cat">${p.categoria}</span></div>
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
    <div class="cert-logo"><img src="${c.logo || iconUrl(c.icon)}" alt="${c.emissor}" /></div>
    <div class="cert-corpo">
      <h3>${c.titulo}</h3>
      <span class="cert-meta">${c.emissor} • ${c.ano}</span>
      <p>${c.desc}</p>
    </div>
  </article>`).join("");

/* =========================================================
   ANIMAÇÕES DE SCROLL (o "passeio" pelo fundo)
   ========================================================= */

/* intro do hero */
gsap.timeline({ defaults: { ease: "power3.out" } })
  .from(".hero-badge", { opacity: 0, y: 20, duration: 0.5 }, 0.1)
  .from(".hero-titulo .linha", { opacity: 0, y: 60, stagger: 0.12, duration: 0.7 }, 0.2)
  .from([".hero-sub", ".hero-bio", ".hero-tags", ".hero-cta"], { opacity: 0, y: 24, stagger: 0.08, duration: 0.5 }, 0.5)
  .from(".lanyard", { y: -560, duration: 1.1, ease: "bounce.out", onComplete: () => (vel += 24) }, 0.35);

/* fundo desloca conforme rola a página — sensação de passear pelo cenário */
gsap.to(".bg", {
  xPercent: -6, yPercent: -9,
  ease: "none",
  scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1.2 },
});
gsap.to(".bg-grid", {
  backgroundPosition: "0px 640px",
  ease: "none",
  scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1.2 },
});

/* SKILLS: seção fica presa e o teclado entra com scrub */
const keys = gsap.utils.toArray(".key");
gsap.set(".keyboard", { rotateX: 58, rotateZ: -40 });

gsap.timeline({
  scrollTrigger: {
    trigger: ".skills",
    start: "top top",
    end: "+=130%",
    pin: ".skills-pin",
    scrub: 0.8,
  },
})
  .fromTo(".skills .titulo-gigante", { scale: 2.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35 })
  .fromTo(".keyboard", { rotateX: 78, rotateZ: -8, y: 260 }, { rotateX: 58, rotateZ: -40, y: 0, duration: 0.6 }, 0.1)
  .fromTo(keys, { z: 420, opacity: 0 }, { z: 0, opacity: 1, stagger: { each: 0.02, from: "random" }, duration: 0.45 }, 0.25)
  .fromTo(".skills-hint", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 0.8);

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
