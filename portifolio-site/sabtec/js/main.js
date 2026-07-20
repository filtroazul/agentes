/* =========================================================
   SABTEC: intro desenhada + animações de traço
   ========================================================= */
gsap.registerPlugin(ScrollTrigger);

/* prepara um shape SVG pra ser "desenhado": esconde o traço todo */
function prepararTraco(el) {
  const len = el.getTotalLength();
  el.style.strokeDasharray = len;
  el.style.strokeDashoffset = len;
  return len;
}

/* ===== INTRO: a logo nasce traço por traço ===== */
const balao = document.getElementById("i-balao");
const esse = document.getElementById("i-esse");
const corte = document.getElementById("i-corte");

prepararTraco(balao);
prepararTraco(esse);
prepararTraco(corte);
gsap.set(balao, { fillOpacity: 0 });
gsap.set("#i-texto", { opacity: 0, y: 8 });
gsap.set("#i-cmyk rect", { scale: 0, transformOrigin: "center" });

const intro = gsap.timeline();
intro
  .to(balao, { strokeDashoffset: 0, duration: 1.15, ease: "power2.inOut" }, .3)
  .to(balao, { fillOpacity: 1, duration: .5, ease: "power2.out" }, "-=.15")
  .to(esse, { strokeDashoffset: 0, duration: .85, ease: "power2.inOut" }, "-=.35")
  .to(corte, { strokeDashoffset: 0, duration: .45, ease: "power2.out" }, "-=.2")
  .to("#i-texto", { opacity: 1, y: 0, duration: .45 }, "-=.1")
  .to("#i-cmyk rect", { scale: 1, stagger: .07, duration: .3, ease: "back.out(3)" }, "-=.3")
  .to(".intro-logo", { scale: .92, duration: .5, ease: "power2.inOut" }, "+=.45")
  .to("#intro", { yPercent: -100, duration: .75, ease: "power4.inOut" }, "-=.15")
  .set("#intro", { display: "none" });

/* ===== entrada do hero (emenda com o fim da intro) ===== */
gsap.timeline({ defaults: { ease: "power3.out" } })
  .from(".nav", { y: -70, opacity: 0, duration: .6 }, 3.35)
  .from(".selo", { opacity: 0, x: -24, duration: .45 }, 3.5)
  .from(".hero-titulo .palavra", { opacity: 0, y: 44, stagger: .08, duration: .55 }, 3.6)
  .from([".hero-sub", ".hero-cta", ".provas"], { opacity: 0, y: 26, stagger: .12, duration: .5 }, 4.05)
  .from(".hero-visual .impresso", { opacity: 0, scale: .6, y: 60, stagger: .16, duration: .65, ease: "back.out(1.7)", clearProps: "opacity" }, 3.8)
  .from(".ponto", { scale: 0, stagger: .1, duration: .35, ease: "back.out(3)" }, 4.4)
  .add(() => {
    const risco = document.querySelector(".risco path");
    prepararTraco(risco);
    gsap.to(risco, { strokeDashoffset: 0, duration: .7, ease: "power2.inOut" });
  }, 4.15);

/* pontos CMYK flutuam */
document.querySelectorAll(".ponto").forEach((p, i) => {
  gsap.to(p, { y: "+=16", duration: 2 + i * .5, ease: "sine.inOut", yoyo: true, repeat: -1 });
});

/* fotos "impressas" do hero balançam de leve */
document.querySelectorAll(".hero-visual .impresso").forEach((f, i) => {
  gsap.to(f, { y: "+=10", rotate: `+=${i % 2 ? 1.2 : -1.2}`, duration: 2.8 + i * .5, ease: "sine.inOut", yoyo: true, repeat: -1 });
});

/* ===== ícones que se desenham quando entram na tela ===== */
document.querySelectorAll(".serv-icone").forEach((icone) => {
  const shapes = icone.querySelectorAll("path, rect, circle");
  shapes.forEach(prepararTraco);
  ScrollTrigger.create({
    trigger: icone,
    start: "top 88%",
    once: true,
    onEnter: () => gsap.to(shapes, {
      strokeDashoffset: 0, duration: 1.1, stagger: .18, ease: "power2.inOut",
    }),
  });
});

/* ===== tesoura corta a página no scroll ===== */
const tesoura = document.querySelector(".tesoura");
if (tesoura) {
  gsap.to(tesoura, {
    left: "92%", rotate: 8,
    ease: "none",
    scrollTrigger: { trigger: ".tesoura-linha", start: "top 95%", end: "top 25%", scrub: 1 },
  });
}

/* ===== blocos entram ao rolar ===== */
gsap.utils.toArray(".titulo").forEach((t) => {
  gsap.from(t, {
    opacity: 0, y: 40, duration: .6, ease: "power3.out",
    scrollTrigger: { trigger: t, start: "top 86%" },
  });
});
ScrollTrigger.batch(".serv, .card-prod, .acess", {
  start: "top 90%", once: true,
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 40, stagger: .09, duration: .55, ease: "power2.out",
    clearProps: "opacity,transform",
  }),
});
gsap.from(".imp-3", {
  opacity: 0, x: -60, rotate: -8, duration: .8, ease: "power3.out",
  scrollTrigger: { trigger: ".producao", start: "top 72%" },
});
gsap.from(".prod-lista li", {
  opacity: 0, x: 40, stagger: .1, duration: .5,
  scrollTrigger: { trigger: ".prod-lista", start: "top 86%" },
});
gsap.from(".imp-loja", {
  opacity: 0, x: -60, rotate: 8, duration: .8, ease: "power3.out",
  scrollTrigger: { trigger: ".sobre", start: "top 72%" },
});
gsap.from(".sobre-lista li", {
  opacity: 0, x: 40, stagger: .1, duration: .5,
  scrollTrigger: { trigger: ".sobre-lista", start: "top 86%" },
});
gsap.from(".convite-caixa", {
  opacity: 0, scale: .9, duration: .7, ease: "back.out(1.6)",
  scrollTrigger: { trigger: ".convite", start: "top 78%" },
});
