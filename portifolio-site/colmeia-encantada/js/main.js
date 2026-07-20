/* =========================================================
   COLMEIA ENCANTADA: produtos + animações
   ========================================================= */
gsap.registerPlugin(ScrollTrigger);

const IG = "https://www.instagram.com/colmeiaencantadaa/";

/* ===== produtos (fotos reais do feed da loja) ===== */
const PRODUTOS = [
  { nome: "Macaquinho Abelhinhas",        cat: "Vestidos",  preco: "89,90", de: "",      foto: "assets/p10.jpg", tag: "a queridinha 🐝", mel: true },
  { nome: "Vestido Corações Arco-íris",   cat: "Vestidos",  preco: "72,90", de: "",      foto: "assets/p6.jpg",  tag: "novo" },
  { nome: "Conjunto Perfect Day",         cat: "Conjuntos", preco: "69,90", de: "79,90", foto: "assets/p1.jpg",  tag: "promo" },
  { nome: "Vestido Morangos",             cat: "Vestidos",  preco: "76,90", de: "",      foto: "assets/p7.jpg",  tag: "" },
  { nome: "Conjunto Summer Abacaxi",      cat: "Conjuntos", preco: "64,90", de: "",      foto: "assets/p2.jpg",  tag: "novo" },
  { nome: "Vestido Floral Rosê",          cat: "Vestidos",  preco: "79,90", de: "",      foto: "assets/p3.jpg",  tag: "delicado ✨", mel: true },
  { nome: "Conjunto Lacinhos Cereja",     cat: "Conjuntos", preco: "74,90", de: "",      foto: "assets/p4.jpg",  tag: "" },
  { nome: "Conjunto Saia Listrinhas",     cat: "Conjuntos", preco: "84,90", de: "",      foto: "assets/p5.jpg",  tag: "" },
  { nome: "Conjunto Player Pro",          cat: "Meninos",   preco: "66,90", de: "",      foto: "assets/p8.jpg",  tag: "p/ eles" },
  { nome: "Vestido Azul Céu",             cat: "Vestidos",  preco: "69,90", de: "",      foto: "assets/p9.jpg",  tag: "" },
  { nome: "Vestido Flores Pink",          cat: "Vestidos",  preco: "78,90", de: "88,90", foto: "assets/p11.jpg", tag: "promo" },
];

const grid = document.getElementById("prod-grid");
const filtros = document.getElementById("filtros");
const cats = ["Tudo", "Vestidos", "Conjuntos", "Meninos"];

function renderProdutos(cat) {
  const lista = cat === "Tudo" ? PRODUTOS : PRODUTOS.filter((p) => p.cat === cat);
  grid.innerHTML = lista.map((p) => `
    <a class="prod" href="${IG}" target="_blank" rel="noopener">
      <div class="prod-foto">
        <img src="${p.foto}" alt="${p.nome}" loading="lazy" decoding="async" />
        ${p.tag ? `<span class="prod-tag${p.mel ? " tag-mel" : ""}">${p.tag}</span>` : ""}
        <span class="prod-quero">eu quero! 🍯</span>
      </div>
      <div class="prod-corpo">
        <h3 class="prod-nome">${p.nome}</h3>
        <div class="prod-preco">
          <strong>R$ ${p.preco}</strong>
          ${p.de ? `<s>R$ ${p.de}</s>` : ""}
        </div>
      </div>
    </a>`).join("");
  gsap.from(grid.children, {
    opacity: 0, y: 34, scale: .94, stagger: .06, duration: .5,
    ease: "back.out(1.6)", clearProps: "all",
  });
}

filtros.innerHTML = cats.map((c) =>
  `<button class="filtro${c === "Tudo" ? " ativo" : ""}" data-cat="${c}">${c}</button>`).join("");
filtros.addEventListener("click", (e) => {
  const btn = e.target.closest(".filtro");
  if (!btn) return;
  filtros.querySelectorAll(".filtro").forEach((b) => b.classList.toggle("ativo", b === btn));
  renderProdutos(btn.dataset.cat);
});
renderProdutos("Tudo");

/* ===== nav ganha sombra ao rolar ===== */
const nav = document.getElementById("nav");
addEventListener("scroll", () => nav.classList.toggle("rolou", scrollY > 30), { passive: true });

/* =========================================================
   ANIMAÇÕES
   ========================================================= */

/* entrada do hero */
gsap.timeline({ defaults: { ease: "power3.out" } })
  .from(".nav", { y: -70, opacity: 0, duration: .6 })
  .from(".hero-selo", { scale: 0, rotate: -8, duration: .45, ease: "back.out(2.5)" }, .25)
  .from(".hero-titulo .palavra", { opacity: 0, y: 46, rotate: 4, stagger: .09, duration: .6 }, .35)
  .from([".hero-sub", ".hero-cta", ".hero-provas"], { opacity: 0, y: 26, stagger: .12, duration: .5 }, .8)
  .from(".hero-fotos .polaroid", { opacity: 0, scale: .5, y: 60, stagger: .14, duration: .7, ease: "back.out(1.8)", clearProps: "opacity" }, .55)
  .from(".brilho", { opacity: 0, scale: 0, stagger: .1, duration: .4, ease: "back.out(3)" }, 1.1);

/* brilhos piscando pra sempre */
gsap.to(".brilho", {
  opacity: .25, scale: .7, duration: 1.1, ease: "sine.inOut",
  yoyo: true, repeat: -1, stagger: .35,
});

/* polaroids balançam suave, como penduradas */
document.querySelectorAll(".hero-fotos .polaroid").forEach((p, i) => {
  gsap.to(p, {
    y: "+=12", rotate: `+=${i % 2 ? 1.6 : -1.6}`,
    duration: 2.6 + i * .4, ease: "sine.inOut", yoyo: true, repeat: -1,
  });
});

/* favos do fundo passeiam com o scroll */
document.querySelectorAll(".fundo .favo").forEach((f, i) => {
  gsap.to(f, {
    y: (i % 2 ? -1 : 1) * (120 + i * 40), rotate: i % 2 ? 40 : -40,
    ease: "none",
    scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1.4 },
  });
});

/* abelhinha voa em zigue-zague conforme a página rola */
const abelha = document.getElementById("abelha");
gsap.set(abelha, { x: -80, y: 0 });
gsap.to(abelha, { y: "+=10", duration: .9, ease: "sine.inOut", yoyo: true, repeat: -1 }); // voo tremido

gsap.timeline({
  scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1.8, invalidateOnRefresh: true },
  defaults: { ease: "none" },
})
  .to(abelha, { x: () => innerWidth * .78, rotate: 10 })
  .to(abelha, { scaleX: -1, duration: .01 })
  .to(abelha, { x: () => innerWidth * .12, rotate: -8 })
  .to(abelha, { scaleX: 1, duration: .01 })
  .to(abelha, { x: () => innerWidth * .85, rotate: 8 })
  .to(abelha, { x: () => innerWidth * 1.15, rotate: 0 });

/* títulos e blocos entram ao rolar */
gsap.utils.toArray(".titulo").forEach((t) => {
  gsap.from(t, {
    opacity: 0, y: 40, duration: .65, ease: "power3.out",
    scrollTrigger: { trigger: t, start: "top 86%" },
  });
});
gsap.from(".filtros", {
  opacity: 0, y: 24, duration: .5,
  scrollTrigger: { trigger: ".filtros", start: "top 88%" },
});
ScrollTrigger.batch(".dep", {
  start: "top 88%", once: true,
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 44, rotate: 2, stagger: .12, duration: .6,
    ease: "back.out(1.6)", clearProps: "opacity,transform",
  }),
});
gsap.from(".pol-sobre", {
  opacity: 0, x: -60, rotate: -10, duration: .8, ease: "power3.out",
  scrollTrigger: { trigger: ".sobre", start: "top 75%" },
});
gsap.from(".sobre-lista li", {
  opacity: 0, x: 40, stagger: .1, duration: .5, ease: "power2.out",
  scrollTrigger: { trigger: ".sobre-lista", start: "top 85%" },
});
gsap.from(".convite-caixa", {
  opacity: 0, scale: .88, duration: .7, ease: "back.out(1.7)",
  scrollTrigger: { trigger: ".convite", start: "top 78%" },
});
