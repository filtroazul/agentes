/* =========================================================
   DADOS DO PORTFÓLIO: edite aqui, sem mexer no resto!
   ========================================================= */

const PERFIL = {
  nome: "Maxwell Gomes",
  usuario: "maxyzao",
  titulo: "Desenvolvedor Full Stack",
  local: "Fortaleza, CE, Brasil",
  bio: "Criando websites modernos com visual limpo, responsivo e elegante. Transformo ideias e design em experiências digitais que funcionam.",
  cv: "assets/cv-maxwell.pdf",       // ← coloque seu CV em PDF nessa pasta
  frases: [                          // ← frases do efeito de digitação do hero
    "Full Stack Developer",
    "Backend e Frontend",
    "Criando softwares desde 2023",
    "Websites modernos e responsivos",
  ],
  email: "maxgomeix@gmail.com",
  whatsapp: "5585991225077",             // só números, com DDI+DDD
  github: "https://github.com/Gyshro",
  linkedin: "https://www.linkedin.com/in/maxwell-gomes-45a780269/",
  instagram: "https://www.instagram.com/maxyzao/",
};

/* ---------------------------------------------------------
   SKILLS: cada uma vira uma keycap do teclado 3D.
   icon: nome do ícone no Devicon (https://devicon.dev)
         ou use  text: "API"  para tecla só com texto.
   key:  tecla física do teclado que aciona essa keycap.
   --------------------------------------------------------- */
const SKILLS = [
  { nome: "JavaScript", tag: "jogando código no DOM desde sempre", icon: "javascript/javascript-plain", cor: "#e8a33d", key: "j" },
  { nome: "TypeScript", tag: "JavaScript com cinto de segurança",  icon: "typescript/typescript-plain", cor: "#3178c6", key: "t" },
  { nome: "React",      tag: "aqui tudo é componente",             icon: "react/react-original",        cor: "#2fb6d9", key: "r" },
  { nome: "Node.js",    tag: "JavaScript no servidor, sim senhor", icon: "nodejs/nodejs-plain",         cor: "#3c873a", key: "n" },
  { nome: "Python",     tag: "indentação é vida",                  icon: "python/python-plain",         cor: "#366fa3", key: "p" },
  { nome: "HTML",       tag: "o esqueleto de toda a web",          icon: "html5/html5-plain",           cor: "#e34c26", key: "h" },
  { nome: "CSS",        tag: "centralizo div até no escuro",       icon: "css3/css3-plain",             cor: "#2965f1", key: "c" },
  { nome: "SQL",        tag: "SELECT * FROM oportunidades",        icon: "mysql/mysql-original",        cor: "#0d7799", key: "s" },
  { nome: "AWS",        tag: "hospedando sonhos na nuvem",         icon: "amazonwebservices/amazonwebservices-plain-wordmark", cor: "#e88b1a", key: "a" },
  { nome: "MongoDB",    tag: "NoSQL com muito estilo",             icon: "mongodb/mongodb-plain",       cor: "#419941", key: "m" },
  { nome: "Git",        tag: "commita e reza",                     icon: "git/git-plain",               cor: "#f05033", key: "g" },
  { nome: "GitHub",     tag: "meu diário público de código",       icon: "github/github-original",      cor: "#23262e", key: "b" },
  { nome: "APIs REST",  tag: "conectando mundos via request",      text: "API",                          cor: "#6d54c4", key: "i" },
  { nome: "JSON",       tag: '{ "dados": "sempre organizados" }',  text: "{ }",                          cor: "#23262e", key: "o" },
  { nome: "Tailwind",   tag: "classe em cima de classe, e ficou lindo", icon: "tailwindcss/tailwindcss-original", cor: "#38bdf8", key: "w" },
];

/* ---------------------------------------------------------
   PROJETOS: cards com filtro por categoria.
   categoria: aparece como filtro (use a mesma string para agrupar)
   cor: cor de destaque do card
   link / repo: pode deixar "" se não tiver
   --------------------------------------------------------- */
const PROJETOS = [
  {
    titulo: "Monitoramento AIOTI Soluções",
    desc: "Plataforma de monitoramento da AIOTI Soluções Industriais, empresa onde atuo: dashboard para os clientes acompanharem seus equipamentos, feita com Python na AWS e login com segurança JWT.",
    categoria: "AWS + PostgreSQL",
    stack: ["Python", "AWS", "PostgreSQL", "JWT"],
    cor: "#35c24a",
    capa: "assets/projetos/aioti.jpg",
    link: "https://www.instagram.com/p/DZiFYkshQmZ/",
    repo: "",
  },
  {
    titulo: "Agente de Atendimento com IA",
    desc: "Chatbot que qualifica leads automaticamente, faz perguntas objetivas e envia o resultado por Telegram e planilha Google.",
    categoria: "Python",
    stack: ["Python", "Streamlit", "IA"],
    cor: "#366fa3",
    capa: "assets/projetos/agente-ia.svg",
    capaContain: true,
    link: "https://agentes-s68ksrzb97z5q4qqp7f8nq.streamlit.app/?agente=atendimento",
    repo: "",
  },
  {
    titulo: "Site Portfólio Elegante",
    desc: "Site de portfólio com tema escuro elegante, navegação flutuante, efeito de digitação e cartão de destaque com foto.",
    categoria: "UI/UX",
    stack: ["HTML", "CSS", "JavaScript"],
    cor: "#c98a5e",
    capa: "assets/foto3.png",
    link: "",
    repo: "",
  },
  {
    titulo: "Loja Colmeia Encantada",
    desc: "Loja online feita para a cliente Colmeia Encantada, moda infantil: vitrine com fotos reais, filtros por categoria, animações com GSAP e código de efetuação de pagamento em JavaScript e Node.js para finalizar as compras.",
    categoria: "Front-end",
    stack: ["JavaScript", "Node.js", "GSAP", "Pagamentos"],
    cor: "#f2a51d",
    capa: "assets/projetos/colmeia-abelha.svg",
    capaContain: true,
    link: "colmeia-encantada/index.html",
    repo: "",
  },
  {
    titulo: "Site AIOTI Soluções",
    desc: "Site oficial da AIOTI Soluções Industriais: apresenta a empresa, os serviços de engenharia, automação e IoT, os produtos e os projetos realizados.",
    categoria: "JavaScript",
    stack: ["HTML", "CSS", "JavaScript"],
    cor: "#79d649",
    capa: "assets/projetos/logo-aioti.png",
    capaContain: true,
    link: "https://aiotisolucoes.com.br/",
    repo: "",
  },
  {
    titulo: "Widget de Chat para Sites",
    desc: "Widget leve de atendimento que se integra a qualquer site com uma linha de código.",
    categoria: "JavaScript",
    stack: ["JavaScript", "HTML", "CSS"],
    cor: "#e8a33d",
    link: "",
    repo: "",
  },
  {
    titulo: "Este Portfólio",
    desc: "Site pessoal com teclado 3D interativo, crachá com física e animações de scroll, feito do zero, sem frameworks.",
    categoria: "JavaScript",
    stack: ["HTML", "CSS", "JavaScript", "GSAP"],
    cor: "#6d54c4",
    link: "",
    repo: "https://github.com/Gyshro",
  },
  // 👉 adicione seus projetos aqui, seguindo o mesmo formato
];

/* ---------------------------------------------------------
   CERTIFICADOS: logo: caminho de imagem OU icon do Devicon.
   arquivo: caminho do PDF (gera o link "ver certificado").
   --------------------------------------------------------- */
const CERTIFICADOS = [
  {
    titulo: "DevQuest Extensão Universitária",
    emissor: "FEX Educação • MEC",
    ano: "2023 a 2026",
    desc: "Capacitação de 123h registrada por faculdade credenciada junto ao MEC: HTML, CSS, JavaScript, React, TypeScript, Node, SQL, Git e projetos práticos.",
    logo: "assets/devquest.svg",
    cor: "#a855f7",
    arquivo: "assets/certificados/devquest-mec.pdf",
  },
  {
    titulo: "DevQuest Frontend",
    emissor: "Dev em Dobro",
    ano: "2026",
    desc: "Curso de programação frontend com aulas teóricas e práticas, completando mais de 80 horas.",
    icon: "react/react-original",
    cor: "#2fb6d9",
    arquivo: "assets/certificados/devquest-frontend.pdf",
  },
  {
    titulo: "DevQuest Backend",
    emissor: "Dev em Dobro",
    ano: "2026",
    desc: "Curso de programação backend com aulas teóricas e práticas, completando mais de 20 horas.",
    icon: "nodejs/nodejs-plain",
    cor: "#3c873a",
    arquivo: "assets/certificados/devquest-backend.pdf",
  },
  {
    titulo: "DevQuest Marketing Pessoal",
    emissor: "Dev em Dobro",
    ano: "2026",
    desc: "Marketing pessoal para programadores: criação de currículo, LinkedIn, GitHub e portfólio.",
    icon: "linkedin/linkedin-plain",
    cor: "#0a66c2",
    arquivo: "assets/certificados/devquest-marketing.pdf",
  },
  {
    titulo: "Análise e Desenvolvimento de Sistemas",
    emissor: "Estácio",
    ano: "cursando",
    desc: "Graduação tecnológica em andamento na Universidade Estácio de Sá.",
    logo: "assets/estacio-simbolo.png",
    cor: "#1478d2",
  },
  // 👉 adicione novos certificados aqui
];
