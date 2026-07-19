/* =========================================================
   DADOS DO PORTFÓLIO — edite aqui, sem mexer no resto!
   ========================================================= */

const PERFIL = {
  nome: "Maxwell Gomes",
  usuario: "maxyzao",
  titulo: "Desenvolvedor Full Stack",
  local: "Fortaleza — CE, Brasil",
  bio: "Criando websites modernos com visual limpo, responsivo e elegante. Transformo ideias e design em experiências digitais que funcionam.",
  disponivel: "DISPONÍVEL PARA TRABALHO",
  email: "maxgomeix@gmail.com",          // ← confira/edite seu e-mail
  whatsapp: "5585992932642",             // ← só números, com DDI+DDD
  github: "https://github.com/Gyshro",
  linkedin: "https://www.linkedin.com/in/maxwell-gomes", // ← cole a URL certa
  instagram: "https://instagram.com/maxyzao",
};

/* ---------------------------------------------------------
   SKILLS — cada uma vira uma keycap do teclado 3D.
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
   PROJETOS — cards com filtro por categoria.
   categoria: aparece como filtro (use a mesma string para agrupar)
   cor: cor de destaque do card
   link / repo: pode deixar "" se não tiver
   --------------------------------------------------------- */
const PROJETOS = [
  {
    titulo: "Agente de Atendimento com IA",
    desc: "Chatbot que qualifica leads automaticamente, faz perguntas objetivas e envia o resultado por Telegram e planilha Google.",
    categoria: "Python",
    stack: ["Python", "Streamlit", "IA"],
    cor: "#366fa3",
    link: "",
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
    desc: "Site pessoal com teclado 3D interativo, crachá com física e animações de scroll — feito do zero, sem frameworks.",
    categoria: "JavaScript",
    stack: ["HTML", "CSS", "JavaScript", "GSAP"],
    cor: "#6d54c4",
    link: "",
    repo: "https://github.com/Gyshro",
  },
  // 👉 adicione seus projetos aqui, seguindo o mesmo formato
];

/* ---------------------------------------------------------
   CERTIFICADOS — logo: caminho de imagem OU icon do Devicon.
   --------------------------------------------------------- */
const CERTIFICADOS = [
  {
    titulo: "Formação Full Stack — Dev em Dobro",
    emissor: "DevQuest",
    ano: "2025",
    desc: "Formação completa em desenvolvimento web: HTML, CSS, JavaScript, React, Node.js e banco de dados.",
    icon: "react/react-original",
    cor: "#6d54c4",
  },
  {
    titulo: "Python para Automação",
    emissor: "— edite em js/data.js —",
    ano: "2025",
    desc: "Automação de tarefas, integração com APIs e criação de bots.",
    icon: "python/python-plain",
    cor: "#366fa3",
  },
  // 👉 adicione seus certificados aqui
];
