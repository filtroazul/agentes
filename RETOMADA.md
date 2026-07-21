# Retomada — estado ao desligar em 20/07/2026

> Este arquivo existe porque a memória do Claude Code é local de cada PC (fica fora do OneDrive).
> Se você abrir esta pasta em outro computador, cole o conteúdo deste arquivo pro Claude ler e recuperar o contexto.

## Feito hoje (20/07/2026)

- **Vídeo da Sabtec pronto**: `vendas/video-sabtec.mp4` (~55s), gravado direto do site publicado em https://gyshro.github.io/Sabtec/. Mesma ideia do vídeo da Colmeia (`vendas/video-colmeia.mp4`).
- **Instruções de upload do portfólio pro GitHub Pages** (dadas, ainda não executadas):
  - Subir o **conteúdo de dentro** de `portifolio-site/` (não a pasta em si): `index.html`, `css/`, `js/`, `assets/`, e **obrigatório** `colmeia-encantada/` (o card da Colmeia linka pra `colmeia-encantada/index.html`). `sabtec/` é opcional (já tem repo próprio).
  - `index.html` precisa ficar na **raiz** do repo.
  - Passos: criar repo em https://github.com/new (sugestão de nome: `Gyshro.github.io` pra ficar na raiz `gyshro.github.io/`, ou outro nome tipo `portfolio` pra ficar em `gyshro.github.io/portfolio/`) → Add file → Upload files (dá pra arrastar pastas) → commit → Settings → Pages → Source: branch main, pasta `/ (root)`.
  - **Ainda não decidimos o nome do repo** — usuário ia escolher e avisar.

## Pendência em aberto (sem resposta ainda)

Chegou uma mensagem de WhatsApp de um contato (+55 85 9702-6232): *"Procura uma que tá normal"* / *"me retorna aí pra eu poder alterar aqui pra subir logo"*. **Não ficou claro do que se trata** (perguntei e o usuário disse "deixa pra lá" por ora). Possíveis hipóteses levantadas: logo da Sabtec (`graficalogo.jpg`, já existe na raiz do projeto — é o "S" verde da gráfica), alguma foto do site, ou outra coisa. **Retomar isso perguntando ao usuário antes de agir.**

## Sites já no ar

- Colmeia Encantada: https://gyshro.github.io/Colmeia/
- Sabtec: https://gyshro.github.io/Sabtec/
- Portfólio pessoal: **publicado** em https://portifolio-rho-eight-70.vercel.app/ (repo https://github.com/Gyshro/Portifolio, deploy via Vercel). Fonte local continua em `portifolio-site/`.
  - 21/07/2026: CV refeito (foto fundo branco, full stack, link do Vercel) em `portifolio-site/assets/curriculo.pdf`; fonte editável em `portifolio/curriculo-fonte.html`. Commit de atualização do repo Portifolio pode estar pendente de push (conta filtroazul não tem permissão no repo Gyshro — precisa logar como Gyshro).

## Outros contextos relevantes (resumo, detalhes completos na memória do PC original)

- Objetivo do usuário: gerar renda (R$5-6k até dez/2026) via venda de sites + agente de leads (chatbot) pra pequenos negócios locais. Colmeia e Sabtec são os 2 primeiros cases/demos.
- Produto do chatbot é genérico (`?agente=atendimento`), rodando no Streamlit Cloud (dorme por inatividade, ~30s pra acordar).
- Guia de setup de cliente novo: `guia-envio-leads.md` na raiz do projeto.
