# Retomada — estado ao desligar em 07/08/2026

## 🏠 17/08 — uploads reais de imóveis no Supabase

O catálogo agora tem **7 imóveis**. O código 7 (`UNICA BENFICA`) está disponível;
os códigos 8 a 13 continuam como **rascunho em destaque**, de propósito, até o
corretor confirmar preço/disponibilidade e publicar pelo painel.

| Código | Imóvel | Fotos |
|---|---|---:|
| 8 | Lúmina Fátima | 20 |
| 9 | Seano Beach & Home | 18 |
| 10 | Nature Eusébio | 11 |
| 11 | Jóquei Condomínio Clube | 21 |
| 12 | Estilo Fátima | 17 |
| 13 | **M.Lar Kennedy** | **19** |

**Último concluído:** M.Lar Kennedy, a partir de **R$ 389.409,93** (tabela
oficial da construtora de julho/2026), 2 ou 3 quartos com suíte e varanda,
50,88 m² a 76,53 m², Avenida Sargento Hermínio Sampaio, 2000, Presidente
Kennedy. Foram usados renders, localização, cinco plantas e implantação do
book em
`C:\Users\Iagho\Downloads\BOOK_MLAR_KENNEDY_1_imagens_alta_qualidade(1)`.
As 19 imagens foram convertidas para WebP 1600×900 e ocupam 2,85 MB. Verificação
final: 19/19 URLs respondendo e código 13 invisível no catálogo público enquanto
rascunho.

**Conferência de Downloads:** as 6 pastas de imagens extraídas em 17/08
(Lúmina, Seano, Nature Eusébio, Jóquei, Estilo Fátima e M.Lar Kennedy) já estão
cadastradas — não repetir nenhuma. Restam dois PDFs sem pasta de imagens e sem
cadastro no banco: `C:\Users\Iagho\Downloads\BOK MLAR CAMBEBA.pdf` e
`C:\Users\Iagho\Downloads\REVISTA ESTILO PASSARÉ DIGITAL.pdf`.

> A sessão do SaaS da imobiliária (seção 4.5) rodou na virada de 05 para
> 06/08. As datas "05/08" espalhadas por este arquivo se referem a ela.
> **Houve uma segunda sessão em 06/08 (seção 0), que é a mais recente.**

> **Por que este arquivo existe:** a memória do Claude Code é local de cada PC (fica em
> `.claude-pessoal`, fora do OneDrive). Ao abrir esta pasta em OUTRO computador, o Claude
> não lembra de nada. Peça pra ele ler este arquivo primeiro.
>
> **Prompt pronto pra colar no outro PC:**
> *"Leia RETOMADA.md na raiz do projeto e me diga onde paramos."*

⚠️ **O caminho da pasta muda por PC.** Em casa é `C:\Users\Iagho\OneDrive\projeto`.
No PC da empresa é `C:\Users\aioti\OneDrive\Documentos\OneDrive\projeto`. Só o
conteúdo sincroniza — memória, credencial do git e chaves SSH não.

📄 **Busca de emprego é assunto à parte:** veja `RETOMADA-CANDIDATURAS.md`
(sessão de 14/08 — pacote de 20 vagas do GPT verificado, 15 links estavam mortos;
5 currículos corrigidos e prontos em `Downloads\ENVIAR-AGORA\`).

---

## 🧠 15/08 — O cérebro do Obsidian virou material de vídeo

Sessão inteira no cofre `OneDrive\cerebro` (fora deste repo, sincroniza igual).
Ele quer um **Reels** se apresentando e mostrando o "cérebro de IA".

**O cofre foi enchido: de 18 notas para 69, com 491 links** (média 7,1 por nota,
zero órfã). Passou a cobrir o que só existia na memória local: os 17 sites, as 7
barbearias, a Ah Imobiliária, a página de serviços e as candidaturas. O grafo é
colorido em 6 grupos **por tag** (`#cliente #tecnico #negocio #carreira
#pessoal #mapa`).

**Arquivos novos neste repo (untracked):**

| Arquivo | O que é |
|---|---|
| `vendas/cerebro/video-cerebro.mp4` | B-roll pronto, **12,7s em 900x1600** (9:16 nativo) |
| `vendas/cerebro/roteiro-reels-cerebro.md` | roteiro com tempos, alvo 50-55s |
| `vendas/cerebro/gravar-cerebro.py` | o gravador — dirige o **Obsidian por CDP**, não um site |

🔴 **Falta ele gravar o rosto e publicar.** O B-roll está pronto.

⚠️ **Não abrir na câmera** as notas `Ah Imobiliária` (WhatsApp do pai) e
`Maxwell Gomes` (telefone e e-mail dele). O vídeo abre `As 7 barbearias` de
propósito: tabela de clientes, nenhum dado de contato.

⚠️ **Antes de mexer no gravador**, ler o cabeçalho do `gravar-cerebro.py` e o
fim do `roteiro-reels-cerebro.md`: os limites do grafo do Obsidian já foram
medidos (rótulo só a partir de zoom ~5x e só no hover; `setScale` tem que vir
junto com `targetScale`; `pan` é posição de tela da origem). Sem isso, é
redescobrir na marra.

---

## 0. 🆕 SESSÃO DE 07/08 — a mais recente

### AS TRÊS BARBEARIAS FICARAM PRONTAS

Site + agente de IA + vídeo de venda para cada uma. **Cada pasta tem um
`RETOMAR.md` próprio com o detalhe fino — ler antes de mexer.**

| | LS Barbearia | Drummer | Diretoria |
|---|---|---|---|
| Instagram | @lsbarbearia_ | @drummerbarbearia | @diretoriabarberoficial |
| Seguidores | **18,6 mil** | 1.320 | 850 |
| Pasta | `portifolio-site/lsbarbearia/` | `.../drummer/` | `.../diretoria/` |
| Agente | `ls_barbearia` | `drummer_barbearia` | `diretoria_barber` |
| Vídeo (49s) | `vendas/video-lsbarbearia.mp4` | `vendas/video-drummer.mp4` | `vendas/video-diretoria.mp4` |
| Seção-assinatura | seletor de degradê | montador de combo | a semana / horário |
| Mostra preço? | não (não publicam) | **sim** | **sim** |
| Contato | Direct do IG | WhatsApp 85 99188-0170 | WhatsApp 85 99612-1736 |

### ✅ O push FOI FEITO (commit `7b53e94`)

`agents.yaml` commitado e pushado pro `main` de `filtroazul/agentes`. Foram
4 agentes: os 3 das barbearias + o `ah_imobiliaria`, que estava pronto desde
06/08 e nunca tinha sido commitado.

**NÃO entraram no commit** (são mudanças de outras sessões, não desta):
`core/tools.py`, `requirements.txt`, `.gitignore`,
`.streamlit/secrets.toml.example`, `deploy/oracle-setup.md`.

### 🔴 O CHAT NÃO ESTÁ RESPONDENDO NO AR — e NÃO é bug dos agentes

Depois do push, testei os três no Streamlit Cloud:

- ✅ O deploy **funcionou**: o app serviu o cabeçalho "Atendimento LS Barbearia
  — Novo Mondubim, Fortaleza", texto que só existe no arquivo recém-pushado.
- ✅ **Uma resposta real saiu e estava certa**: recusou preço, disse que
  atendem de terça a sábado e não no domingo, e respondeu as DUAS perguntas
  da mesma mensagem.
- ❌ **Da segunda chamada em diante, tudo devolve** "O assistente está
  temporariamente indisponível" — nos três agentes igual. ~6 tentativas em
  10 minutos, com pausas.
- ✅ **A API da Groq responde normal** chamada direto do PC com a chave do
  `.streamlit/secrets.toml`. Não é o modelo, não é a chave local, não é cota
  da conta, não é bug dos prompts.

**Hipótese principal: a `GROQ_API_KEY` configurada nos SECRETS DO APP no
Streamlit Cloud é outra chave e estourou o limite.** É o único lugar que não
dá pra inspecionar do PC.

**Primeira coisa a fazer:** abrir as configurações do app no Streamlit Cloud e
conferir essa chave. Depois testar:
`?agente=ls_barbearia&embed=true&cor=faec41` ·
`?agente=drummer_barbearia&embed=true&cor=a97b2e` ·
`?agente=diretoria_barber&embed=true&cor=e8a71d`

⚠️ **Não sair mexendo nos prompts** achando que quebraram. Os três passaram
em 4 a 9 armadilhas cada, testados localmente contra `core.agent.responder`.

### 🔴 Pendência que muda um site inteiro: o horário da Diretoria

As duas fontes públicas deles **discordam**:

- **Bio do Instagram:** "Seg a Sab- 08:30 à 12hrs - **14:30 à 19hrs**; Dom
  08:30 às 12hrs" — ou seja, **fecham para o almoço**.
- **Página de agendamento:** seg–sex 08:30–19:00 corrido, **sem intervalo**.

O site usa a versão da BIO. **A seção-assinatura inteira depende disso** (é um
quadro da semana em que o intervalo aparece como um buraco). Se ele confirmar
que não fecham pro almoço, mexer nas constantes `MANHA`/`TARDE` no fim de
`portifolio-site/diretoria/js/main.js` E no bloco "HORÁRIO" do agente
`diretoria_barber` no `agents.yaml`.

### A descoberta que mudou dois dos três sites

**Drummer e Diretoria têm página de agendamento PÚBLICA** no `schedweb.com.br`
(`/drummerbarbearia` e `/diretoriabarber`), com tabela de preços completa,
horário, formas de pagamento e comodidades. Por isso esses dois sites mostram
preço e os agentes deles informam preço — mesmo caso do Félix.

Foi lá que apareceram a **rua e o telefone da Diretoria**, que a pesquisa
anterior dava como inexistentes. **Sempre procurar o link de agendamento na
bio antes de assumir que não há dados.**

### Como separei três barbearias de logo amarela

Mantive o amarelo real de cada uma e separei pela SUPERFÍCIE e pela TIPOGRAFIA.
**Não unificar os três amarelos** — se parecerem parentes, mexer na superfície.

- **LS**: limão ácido `#faec41` sobre escuro + concreto cinza frio (a parede
  deles). Oswald + Barlow, heráldico.
- **Drummer**: latão `#a97b2e` + **papel BRANCO** com preto pesado (o salão
  deles é branco). Anton + Space Grotesk, cartaz de show. Fotos em **P&B
  duotone** — reversível, as originais em cor estão em `*-cor.jpg`.
- **Diretoria**: laranja-mel `#e8a71d` + **tijolo `#b58860`** sobre osso (a
  casa é clássica: tijolo, poste de barbeiro, sofá capitonê). Bevan + Work
  Sans, placa esmaltada. Fotos em cor com grade quente vintage.

### Armadilhas técnicas pagas nesta sessão

- **Bigode de logo tem que ser PREENCHIDO** (LS e Diretoria). Em contorno vira
  rabisco. Muda a intro: os `.tr` se desenham, o bigode entra por escala.
- **Amarelo claro não pode ser TEXTO sobre fundo claro** (dá ~1,1:1). Cada
  site tem uma versão escurecida do próprio amarelo só pra virar letra.
- **`overflow:hidden` na linha do título CORTA o acento** de É/Á. Precisa de
  `padding-top` com `margin-top` negativo. Pegou o Drummer: saía "TODO DIA E
  DIA" em vez de "TODO DIA É DIA".
- **Arrastar sem `user-select:none` pinta os rótulos de azul** e isso aparece
  no vídeo de venda. Pegou a Diretoria.
- **O Streamlit volta o scroll do iframe pro TOPO a cada rerun**, então as
  bolhas novas somem abaixo da dobra e o vídeo mostra a conversa pela metade.
  Solução: `rolar_chat(quadro)` depois de cada resposta, já nos scripts do
  Drummer e da Diretoria. **Custou uma gravação inteira.**
- **Nome de arquivo de foto da sessão anterior não é confiável**: no LS o
  `fachada-resenha.jpg` era um cliente na rua, não a fachada. Conferir foto a
  foto antes de escrever legenda.
- **O agente pode INVENTAR fato sobre o lugar**: o do Drummer inventou que
  havia estacionamento nas proximidades. Os três ganharam regra explícita de
  não afirmar nem negar nada sobre a estrutura que não esteja no prompt.

### O que falta (por site)

- **LS**: confirmar se fazem barba (é dedução minha); o mural parece assinar
  "Leandro Silva", o que explicaria o LS — não entrou no site por estar
  borrado; **não existe foto da fachada**.
- **Drummer**: as fotos ficaram em P&B (ele pode preferir cor); a foto de
  equipe é com camisa da seleção e data a peça; não sabemos o nome dos
  barbeiros.
- **Diretoria**: o horário (acima); qual corte entra no "Combo completo de
  R$ 45" (a tabela não diz e o agente foi instruído a não chutar).
- **Nas três: faltam fotos da fachada e do interior.** Tudo é frame de reel a
  360px. **Pedir fotos é o maior ganho possível nos três.**

### ⚠️ O gargalo continua o mesmo

São **13 sites de cliente prontos** e **ZERO abordagem enviada**. Os vídeos
das três barbearias estão em `vendas/`. Nenhum dos 3 sites foi publicado.

---

## 0.1. SESSÃO DE 06/08

### Ah Imobiliária: a logo CHEGOU e virou o site inteiro

Ele mandou `Downloads/IMG-20251121-WA0000.jpg` — monograma AH sob telhado, em anel
dourado, com chave descendo. **Isso encerra a pergunta 4 da seção 7.**

- `ah-imobiliaria/marca.svg` — logo redesenhada em vetor (medida no pixel), usada
  no cabeçalho e rodapé das 3 páginas. `favicon.svg` é a versão pra 16px.
- **Abertura animada:** a logo se desenha do zero na 1ª visita da aba.
- **Cores reais:** vinho `#6e181b` + dourado `#c3a35c` (eram chute antes).
- **Superfícies champanhe:** ele pediu "molde as cores conforme a logo". O fundo
  do cartão da logo (`#c9ae6b`→`#efdfa1`) virou a família das superfícies
  (`--bg: #faf5e9`) e o hero cita o degradê via `--hero-veu`.
- **Contatos reais no `js/config.js`:** IG `@ah.imobiliaria`, WhatsApp
  `558599928999`, **CRECI-CE 28277** (estava impresso na logo). Endereço e
  e-mail VAZIOS — o site esconde a linha sozinho. Não inventar.

⚠️ **O WhatsApp tem 8 dígitos depois do DDD e ESTÁ CERTO.** Parece erro (celular
no Ceará tem 9 desde 2016), mas ele confirmou duas vezes. **NÃO "consertar"** pra
`5585999928999`. O `wa.me` aceita os dois formatos, então testar não distingue.

### 🆕 Fila nova: 3 BARBEARIAS (as barbearias passaram na frente do RFlores)

| | LS Barbearia | Drummer | Diretoria |
|---|---|---|---|
| Instagram | @lsbarbearia_ | @drummerbarbearia | @diretoriabarberoficial |
| Seguidores | **18,6 mil** | 1.320 | 850 |
| Endereço | Av. Contorno Leste, 125 — Novo Mondubim | Av. Édson Magalhães, 817 — Industrial | Conjunto Esperança |
| Telefone | não achado | 85 99188-0170 | não achado |

**Decisões dele (não reabrir):** LS primeiro, mostrar, aprovar, depois os outros
dois. Contato do LS aponta pro **Direct do Instagram** (o link da bio não abre
deslogado). Vídeo só dos sites de cliente, **não da imobiliária**.

**Três coisas que mudam o trabalho:** (1) as três logos são amarelo-no-preto, e
preto+dourado já é do Félix — separar por tipografia e assinatura, não por cor;
(2) LS e Drummer **já têm sistema de agendamento**, então o site não vende isso —
vende vitrine e, no LS, a loja de produtos (relógios, carteiras, bebidas);
(3) faltam hora do LS, horário do Drummer e rua da Diretoria: viram "combinado
pelo WhatsApp".

**LS em construção** em `portifolio-site/lsbarbearia/`. Feito: 10 fotos do feed
tratadas em 3:4 e o brasão em `assets/brasao.svg`. Falta o site inteiro.
Assinatura decidida: **seletor de degradê interativo** (o feed dele é quase 100%
degradê). Amarelo da marca: `#faec41`.

### 🔴 Conferido: só 2 dos 12 sites estão NO AR

| No ar | Link | Repo |
|---|---|---|
| Colmeia | https://gyshro.github.io/Colmeia/ | `Gyshro/Colmeia` |
| Sabtec | https://gyshro.github.io/Sabtec/ | `Gyshro/Sabtec` |
| Portfólio | https://portifolio-rho-eight-70.vercel.app/ | `Gyshro/Portifolio` |

⚠️ **`Gyshro/Sabtec.` (com ponto) serve o PORTFÓLIO, não o site da Sabtec.** Não
mandar esse link pro cliente.

Os outros 10 nunca foram publicados e **nem estão commitados**. O portfólio no ar
**não linka nenhum site de cliente** (só âncoras internas), então não serve de
vitrine. Publicar exige login como `Gyshro` (o PC só tem credencial `filtroazul`)
e o `gh` CLI **não está instalado**.

### Vídeos: nada a gravar

**Todo site pronto já tem vídeo.** Os dois sem vídeo são os dois sem site:
`rflores` e `lsbarbearia`. Só Colmeia e Sabtec estão levemente desatualizados
(commit `c5f444d` mudou a cor do chat, que aparece no vídeo) — regravação
oferecida, sem resposta.

⚠️ `vendas/gravar-video.py` tem `CHAT` chumbado no agente do Estúdio (linha 23).
Ajustar antes de reusar pra outro cliente.

### Onde parou

Terminar o **site do LS**: index.html, paleta/fontes, seção do degradê, agente,
testes, vídeo. Depois Drummer e Diretoria.

---

## 1. Onde as coisas estão (mapa rápido)

| O quê | Onde |
|---|---|
| Detalhe de CADA site de cliente | `portifolio-site/<cliente>/RETOMAR.md` |
| Checklist pra site novo + armadilhas | `portifolio-site/_modelo/COMO-FAZER.md` |
| Contexto antigo (Oracle, ManyChat, CV, presente) | `MEMORIA-RESUMO.md` (raiz) |
| Próximo cliente (pesquisa pronta) | `portifolio-site/rflores/RETOMAR.md` |
| **SaaS da imobiliária do pai** | **`ah-imobiliaria/RETOMAR.md`** |
| Agentes de IA | `agents.yaml` |
| Vídeos demo | `vendas/*.mp4` + `vendas/gravar-video*.py` |

**Regra de ouro:** antes de mexer num site, ler o `RETOMAR.md` da pasta dele. É lá que
está o dado do cliente, a decisão tomada e a pendência.

---

## 2. Estado: 10 sites de cliente prontos

Todos untracked dentro de `portifolio-site/` (de propósito — cada um vira repo próprio):

`colmeia-encantada` · `sabtec` · `felix` · `estudioeconceito` · `claudia` ·
`spacobeauty` · `butterflydreams` · `fisioclin` · `jkpapelaria` · `reservaiguatemi`

✅ **Nada pendente de push.** Conferido em 04/08: `git log origin/main..main` vazio.
Os agentes `jk_papelaria` e `reserva_iguatemi` subiram nos commits `1d0bb85` e `658cf62`
e foram testados no ar. Os chats dos 10 sites funcionam.

### 10 vídeos demo gravados — TODOS os sites já têm vídeo (04/08)

`video-colmeia` · `video-sabtec` · `video-felix` · `video-estudioeconceito` ·
`video-claudia` · `video-jkpapelaria` · `video-reservaiguatemi` ·
`video-fisioclin` · `video-butterfly` · `video-spacobeauty` (todos em `vendas/`).

Os 3 últimos (fisioclin, butterfly, spacobeauty) foram gravados em 04/08. Cada
um tem script próprio: `vendas/gravar-video-fisioclin.py`,
`gravar-video-butterfly.py`, `gravar-video-spaco.py` (ainda untracked).

⚠️ **Toolchain instalado NESTE PC (o da empresa) em 04/08**, que não tinha nada:
`pip install playwright` e `ffmpeg` (winget Gyan.FFmpeg 9.0). Os scripts novos
**auto-detectam a versão do Chrome** do agent-browser (não fixam mais a 150).
Dois detalhes do ffmpeg 9.0: use `-fps_mode vfr` (o `-vsync` foi removido) e
chame pelo caminho absoluto se o `ffmpeg` não estiver no PATH do shell novo:
`~/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_*/ffmpeg-9.0-full_build/bin/ffmpeg.exe`.

---

## 3. 🔴 O gargalo real do negócio

**10 sites prontos, 10 vídeos gravados, ZERO abordagem enviada.**

Isso não muda há semanas. Agora TODO site tem site + vídeo + agente testado: não
falta mais material de venda, falta MANDAR. A meta é R$ 5-6k até dez/2026
(4-5 clientes) e nenhum lead foi contatado. Os melhores alvos, por tamanho:

- **Fisioclin** — 4.978 seguidores, site + vídeo (04/08) prontos.
- **JK Papelaria** — 4.524 seguidores, tem o melhor vídeo de todos (46,5s).
- **Spaço Beauty** e **Butterfly Dreams** — site + vídeo prontos (04/08).

Receita de abordagem já definida (`vendas/abordagem-fria.md`): **não mandar link na
primeira mensagem**, mandar o vídeo junto, oferecer 2 semanas grátis sem compromisso.
Preço: setup R$ 400-600 + mensalidade R$ 150-250.

**Cobrar isso antes de produzir site novo.**

⚠️ **05/08: continua zero abordagem enviada.** A sessão de 05/08 construiu o
SaaS da imobiliária do pai (seção 4.5), que é trabalho legítimo mas **não
aproxima o primeiro cliente pagante** — é projeto de produto, exatamente o que
a sua própria regra manda despriorizar. O material de venda dos 10 sites segue
pronto e parado. Se abrir uma sessão nova sem saber o que fazer: mandar
mensagem pra Fisioclin ou JK Papelaria vem antes de qualquer código.

---

## 4. RFlores Floricultura (saiu do topo da fila — ver seção 0)

`@rfloreseusebio` — **16,4 mil seguidores**, o maior alvo da carteira (3× a Fisioclin).
Negócio próprio, sem franqueador no caminho.

- ✅ **Pronto:** pesquisa completa + **as 46 páginas do catálogo Canva já capturadas**
  em `portifolio-site/rflores/catalogo-fonte/p01..p46.jpg`. **Não recapturar.**
- ❌ **Falta:** extrair a tabela produto/preço/composição, o site, o agente `rflores`
  e o vídeo.
- **Decisões já tomadas (não reabrir):** tudo aponta pro Direct
  (`ig.me/m/rfloreseusebio` — não tem WhatsApp publicado; **não usar o número da matriz
  de Cascavel**), e o catálogo entra completo com preço.
- ⚠️ Paleta rosa+lilás: medir no pixel e **cuidar pra não sair irmã da JK Papelaria**
  (magenta+menta) nem da Colmeia (mel+rosa pastel).

Tudo detalhado em `portifolio-site/rflores/RETOMAR.md`.

### Fora da fila

`@aramis_terrazo` — é **loja franqueada** da grife Aramis, 652 seguidores. Decisão sua:
deixar de fora. Não retomar sem você pedir.

---

## 4.5. 🆕 SaaS da Ah Imobiliária (do pai) — construído em 05/08/2026

Trilha **separada** dos sites de cliente. Detalhe completo em
`ah-imobiliaria/RETOMAR.md` (leia esse antes de mexer). O essencial:

**O que é:** site + catálogo + painel do corretor + agente, pra imobiliária do
pai dele. Ele procrastinava isso fazia tempo. Pasta autocontida, 18 arquivos.

**Stack decidida (não reabrir):** HTML/CSS/JS puro + **Supabase free**
(Postgres, Auth, Storage) + Leaflet/OpenStreetMap. Custo R$ 0.

**Foi decidido NÃO usar a VM da Oracle** para este projeto, apesar de ele ter
cogitado. Motivo: exigiria abrir 80/443, comprar domínio só pra ter HTTPS,
backup manual, e o IP dela é efêmero. Ela continua só com `leadiot-bot` e
`leadiot-webhook`, que só fazem conexão de saída. A saída do Supabase é barata
porque é Postgres puro (`pg_dump` e move pra onde quiser).

**Limite que importa:** o gargalo do plano free não é banco (500 MB é infinito
pra texto), é **1 GB de foto**. Por isso o admin comprime pra WebP 1600px
(~200 KB) no navegador antes de subir. Dá uns 400 imóveis.

**Rodar:** `cd ah-imobiliaria && python -m http.server 8720`. Tem que ser por
servidor: `file://` bloqueia `import` de módulo. Sem Supabase configurado sobe
em modo demonstração com 9 imóveis falsos e uma faixa vermelha avisando.

### ⚠️ Estado real: escrito ≠ testado

| Testado de verdade | Só escrito, NUNCA rodou |
|---|---|
| Landing, parallax, seção presa, tema claro e escuro | Todo o painel admin contra banco real |
| Catálogo, filtros, paginação, 3 estados | Login, upload, compressão, salvar, excluir |
| Página do imóvel, galeria, mapa Leaflet | As policies de RLS na prática |
| Agente: import, YAML e schema das ferramentas | O agente conversando com catálogo real |

**Primeiro teste obrigatório depois de criar o Supabase:** abrir o site em aba
anônima e tentar editar um imóvel pela API. **Tem que dar 403.** Se passar,
qualquer visitante mexe na carteira do pai dele.

### Também mudou na raiz (ainda não commitado)

- `core/tools.py`: ferramenta nova `buscar_imoveis`, que chama a RPC do
  Supabase por HTTP. Lê `SUPABASE_URL`/`SUPABASE_ANON_KEY` do ambiente e cai
  no `.streamlit/secrets.toml`. O import de `tomllib` é opcional de propósito,
  porque a VM roda Python 3.10.
- `agents.yaml`: agente `ah_imobiliaria`, com a regra de perguntas empilhadas
  já embutida (a armadilha da seção 6) e proibição explícita de inventar
  imóvel quando a ferramenta falhar.

### Pendências dele (não são técnicas)

1. **A logo nunca foi enviada.** As cores são chute meu (`#9B1B30` vermelho,
   `#C8A249` dourado), em variável no `css/tokens.css`. Uma linha cada.
2. **Confirmar a praça.** Chutei Fortaleza/CE no padrão e nos bairros da demo.
3. Ele **já tem um domínio `.com.br`** e vai apontar depois.
4. Depoimentos da landing são inventados. Trocar antes de mostrar pra alguém.

---

## 5. Regra que vale pra TODO site novo

**Cada site é publicado como repo/pasta independente**, com o conteúdo da pasta na raiz.
Nada pode apontar pra fora da pasta (`../_comum/chat.js` quebraria). O reuso é na
CRIAÇÃO: copiar `portifolio-site/_modelo/` e seguir o `COMO-FAZER.md`.

**Nunca inventar preço, horário ou endereço** que não esteja publicado no perfil do
cliente. O agente também não pode.

---

## 6. Armadilhas técnicas já pagas (não repetir)

- **O WhatsApp da Ah Imobiliária tem 8 dígitos e está CERTO** (`558599928999`).
  Parece erro de digitação; o dono confirmou duas vezes. Não "corrigir".
- **Gradiente SVG em `objectBoundingBox` some em traço reto.** Linha vertical
  tem caixa de largura zero, o gradiente degenera e não pinta nada. Usar
  `gradientUnits="userSpaceOnUse"`. (Custou uma rodada de depuração no `marca.svg`.)
- **Bigode em contorno não lê como bigode.** No brasão do LS, só preenchido
  funciona. Vale pra qualquer forma orgânica pequena redesenhada em SVG.
- **Brasão detalhado morre abaixo de ~90px.** Fazer um monograma simplificado
  pra nav e usar o brasão só em tamanho grande.

**Agentes de IA**
- **Perguntas empilhadas:** se a pessoa manda 3 perguntas numa mensagem só, o modelo
  responde uma e ignora as outras. Só apareceu no ar (JK e Reserva). Precisa de regra
  explícita no prompt: *"se vier MAIS DE UMA pergunta na mesma mensagem, responda TODAS"*.
  **Copiar essa regra pro agente da RFlores e testar com pergunta tripla.**
- **Testar agente sem subir o Streamlit:** script de ~25 linhas que lê o `agents.yaml`,
  pega a chave em `.streamlit/secrets.toml` com `tomllib` e chama `core.agent.responder`
  com histórico fake. Roda 4 curveballs em ~15s.
- **Cifrão vira LaTeX no Streamlit:** já corrigido em `app.py` (`escapar_cifrao()`).
  Não escapar dentro do card de RESUMO (lá é HTML bruto).

**Front-end (achadas no SaaS da imobiliária, valem pra todo site)**
- **`[hidden]` perde pra qualquer classe com `display` próprio.** `.btn` é
  `inline-flex`, então `elemento.hidden = true` não escondia nada. Trave o
  assunto no reset com `[hidden] { display: none !important }`.
- **`.leaflet-container` sobrescreve a altura do mapa.** O Leaflet aplica essa
  classe no PRÓPRIO elemento. Declarar `height` nela ganha do `height` que
  você definiu e o mapa colapsa pra zero. Não declare altura ali.
- **Mapa criado com o container escondido nasce cinza.** Chame
  `invalidateSize()` depois de mostrar o painel.
- **Foto dimensionada pela largura estoura o primeiro olhar.** Numa coluna de
  600px, `aspect-ratio: 4/5` vira 750px de altura e empurra o CTA pra fora da
  tela. Deixe a ALTURA mandar (`height: min(66dvh, 38rem)`).
- **Faixa/banner solto no `<body>` passa por baixo de cabeçalho `fixed`.**
  Coloque dentro do próprio cabeçalho e meça a altura em JS.
- **`prefers-reduced-motion` não pode deixar a página em branco.** Só aplique
  o estado inicial escondido quando o JS confirmar que pode animar, e remova a
  classe se o CDN da animação não carregar.

**Deploy**
- Remote: `origin https://github.com/filtroazul/agentes.git`, branch `main`, **sem
  upstream** — `git status` não mostra ahead/behind. Sempre conferir
  `git log origin/main..main` antes de dar trabalho por publicado.
- **Push na main é bloqueado pro agente.** Você roda `! git push origin main`.
  ⚠️ No PC da empresa a credencial do git pode não estar salva.
- **O Streamlit Cloud free DORME de verdade** — aparece "Zzzz... this app has gone to
  sleep", precisa clicar "Yes, get this app back up!" e esperar 1-2 min. Antes de
  qualquer demo ao vivo, acordar o app e mandar um "oi" pra aquecer.

**Gravar vídeo**
- **Não usar a gravação nativa do browser** — acelera e come as pausas. O que funciona é
  renderizar frame a frame com Playwright: `vendas/gravar-video.py` (é só trocar as
  constantes do topo). O `gravar-video-interativo.py` tem o cursor sintético SVG (o
  screenshot do Playwright não desenha o mouse, sem isso o vídeo mostra painel mudando
  sozinho).
- **Gravar contra o Streamlit LOCAL:** copiar a pasta do site pro scratchpad, trocar a
  constante `APP` do `js/chat.js` por `http://localhost:8512/` e subir
  `streamlit run app.py --server.port 8512`. Não depende do deploy nem do app dormindo.
- Passar `reduced_motion="no-preference"` no contexto, senão o vídeo sai capado.

**Seu PC reporta `prefers-reduced-motion: reduce`** (animações do Windows desligadas).
Você vê a versão reduzida de qualquer site. Não é bug. Se quiser ver o efeito cheio,
ligar as animações do Windows.

---

## 7. Perguntas suas ainda sem resposta

1. **O movimento dos fios no site do Estúdio E Conceito ficou no ponto?** Você ia abrir
   no navegador e não respondeu. (Lembrar do reduced-motion acima.)
2. **O WhatsApp do 85 9702-6232** ("Procura uma que tá normal" / "me retorna aí pra eu
   poder alterar aqui pra subir logo") era sobre o quê? Você disse "deixa pra lá" na
   época. Não presumir — perguntar.
3. Pendências antigas: secrets de leads no Streamlit Cloud (Telegram/webhook), publicar
   `empresaindex/` da AIOTI, ~~terminar o fluxo do ManyChat~~.
   ✅ **ManyChat ENCERRADO em 20/08** — o External Request é PRO (R$ 80-90/mês por
   conta) e não dá pra fazer no grátis. Decidido usar **Meta Business Suite como
   portaria** (Direct/Messenger, grátis) e o **painel do CRM pra lead qualificado**.
   Descoberta que veio junto: a caixa de entrada unificada **já estava construída**
   (tabela `lead_interacoes` com canal `instagram` e `external_id`, `core/crm.py`,
   e a conversa já renderizada em `js/crm.js`). Faltava só a permissão da Meta, que
   é o que o ManyChat de fato vende. **Não sugerir ManyChat de novo.**
   Detalhe em `deploy/manychat-setup.md` (topo) e `ah-imobiliaria/RETOMAR.md`.
4. ~~A logo da Ah Imobiliária.~~ ✅ **RESOLVIDO em 06/08** — ver seção 0.
5. **Qual a cidade/praça da imobiliária do pai?** Assumi Fortaleza/CE por
   causa do DDD 85, mas ele não confirmou.

---

## 8. Links úteis

- Demo genérico: `https://agentes-s68ksrzb97z5q4qqp7f8nq.streamlit.app/?agente=atendimento`
- Widget de cliente: `.../?agente=<nome>&embed=true&cor=<hex>`
- ⚠️ Sem `?agente=` cai no **modo admin com sidebar** — nunca compartilhar essa URL.
- Sites no ar: https://gyshro.github.io/Colmeia/ · https://gyshro.github.io/Sabtec/
- Portfólio: https://portifolio-rho-eight-70.vercel.app/


---

## 08/AGO (fim do dia) — Ah Imobiliaria publicada; keep-alive PENDENTE

**FALTA VOCE FAZER (1 clique):** ligar o GitHub Pages em
https://github.com/filtroazul/ah-imobiliaria/settings/pages
-> Source: **Deploy from a branch** -> **main** -> **/ (root)** -> Save.
Link do site: **https://filtroazul.github.io/ah-imobiliaria/**
(Nao deu pra ligar por workflow: a permissao do GITHUB_TOKEN do repo e somente
leitura, deu "Resource not accessible by integration".)

**FEITO:** site pushado (repo local em `C:\Users\Iagho\repos\ah-imobiliaria`),
chat de IA integrado ao site, e a ferramenta `buscar_imoveis` commitada no repo
`agentes` (commit `5428415`) — ela estava declarada no agents.yaml mas nunca
tinha sido commitada, entao o agente rodava sem catalogo, em silencio.
Agente testado no ar: respondeu em 3,7s e nao inventou imovel.

**PENDENTE — deixar a IA acordada:** o `keep-alive.yml` esta VERDE E INUTIL.
`/_stcore/health` devolve 303 (redirect de auth) e o GET da pagina devolve 200
mesmo dormindo (e so o esqueleto HTML; o "Zzzz" e desenhado pelo JS). O
Streamlit conta sessao de **websocket**, nao HTTP. O conserto e trocar o
workflow por um Playwright headless que abre o app e clica em "Yes, get this
app back up!". O app foi acordado na mao hoje e esta no ar agora.
