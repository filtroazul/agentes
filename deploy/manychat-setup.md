# Ligar a IA no ManyChat (Instagram DM e WhatsApp)

> ## 🔴 20/AGO/2026 — PARADO DE PROPÓSITO. Ler antes de retomar.
>
> **O passo 3 deste guia não funciona no plano grátis.** Conferido na conta real,
> clicando até o fim:
>
> - Automação → Começar Do Zero → Flow Builder → **Escolher Próximo Passo**
> - O passo **"Executar Ações" é livre**, sem selo.
> - Mas dentro dele, aba **Automação**, a ação **"Fazer uma consulta externa"**
>   (*"Envie uma requisição HTTP para o seu servidor"*, que é o External Request
>   traduzido) está com selo **PRO**.
> - Todas as ações liberadas são internas do ManyChat (tag, campo, sequência,
>   pausar automação). **Nenhuma fala com servidor de fora.**
> - Também são PRO: Condição, Randomizador, Atraso Inteligente, Coleta de Dados,
>   Galeria e Dinâmico. Livres: Instagram, Etapa de IA, Executar Ações,
>   Iniciar outra automação, Selecionar Passo Existente.
>
> **NÃO refazer esse caminho pra "confirmar".** Já foi confirmado tela por tela.
>
> ### Por que não vale pagar (hoje)
>
> Uns R$ 80 a R$ 90 por mês **por conta conectada**. Pra revender pras barbearias
> comeria de um terço a metade da mensalidade de R$ 150-250. Hoje o chat do site
> custa R$ 0 por cliente porque roda no Groq grátis.
>
> ### O que se está comprando não é código
>
> A cadeia inteira **já existe e está pronta**: recebimento, dedup por
> `external_id`, gravação dos dois lados, resposta da IA, aviso no Telegram,
> contador de não lidas e a conversa desenhada na ficha do lead. Ver
> `core/crm.py` (`registrar_entrada`, `registrar_saida`,
> `resposta_por_external_id`, `historico_do_lead`) e a tabela `lead_interacoes`
> do `ah-imobiliaria/supabase/schema.sql`, que já prevê o canal `instagram`.
>
> Falta só **o cano**: algo que perceba o Direct chegando e faça o POST.
> E esse buraco é **burocrático, não técnico** — qualquer ferramenta que leia DM
> do Instagram precisa de permissão da Meta, e a Meta só libera depois de revisar
> o app. O ManyChat consegue porque já é provedor aprovado. Por isso Zapier, Make
> e n8n esbarram no mesmo muro. **O que os R$ 90/mês compram é a aprovação da
> Meta deles.**
>
> ### A decisão tomada em 20/08 (a divisão)
>
> Não construir o cano. Usar dois lugares, cada um no que é bom:
>
> | | Meta Business Suite (grátis) | Painel do CRM |
> |---|---|---|
> | Direct, Messenger e comentários | ✅ | ❌ |
> | Chat do site com IA que conhece o catálogo | ❌ | ✅ |
> | Funil com etapas, métrica de conversão, campos do lead | ❌ só etiqueta | ✅ |
> | Resposta automática | texto fixo | IA que consulta os imóveis |
>
> **Business Suite é a portaria** (primeiro contato, barulho, curioso). **O painel
> é quem já entrou.** Lead do site cai sozinho no painel; Direct que esquentou o
> corretor promove no botão "Novo lead", que já existe.
>
> Isso elimina a necessidade do cano agora: sem ManyChat, sem mensalidade, sem
> Revisão de App.
>
> ### O plano B é melhor que o plano A (mas é pra depois)
>
> Fazer a **Revisão do App da Meta uma vez**, no nome da AIOTI: o app aprovado
> atende quantos clientes quiser, cada um conectando o próprio Instagram. Custo
> por cliente **R$ 0 pra sempre**, contra R$ 90/mês por cliente revendendo
> ManyChat. **A rota da Meta não é o plano pobre, é o produto.**
>
> Custo de entrada: política de privacidade publicada, ícone, vídeo demonstrando
> o uso, e semanas de análise. Por isso só depois do primeiro cliente pagante.
>
> ### O que ficou feito e continua valendo
>
> - Conta ManyChat criada, **@ah.imobiliaria conectada** (aparece como "AH Imóveis",
>   plano FREE, avatar com a logo certa). Não precisa refazer.
> - Login do ManyChat é por **e-mail**, não pelo Facebook. Isso é normal: o login
>   é só a identidade do operador, a conexão do Instagram é outra camada, feita
>   por "+ Adicionar Nova Conta".
>
> ### Armadilhas pagas nessa sessão (não repetir)
>
> - **Loop na tela de login do Instagram.** A caixa "Fazer login como" do
>   gerenciador de senhas do Google não é a lista de sessões ativas. Clicar numa
>   senha salva ali, na tela de *escolher perfil já logado*, não tem campo pra
>   preencher e a tela recarrega igual, pra sempre. O caminho é **"Usar outro
>   perfil"**, que abre o formulário de verdade.
> - **Sessão não passa de um navegador pro outro.** Logar o Instagram no Chrome e
>   abrir o ManyChat no Edge cai no mesmo loop.
> - **O Flow Builder não cabe em janela pequena.** A coluna do passo fica cortada
>   e parece que acabou. Maximizar e dar Ctrl+menos até 67%.
> - **Não existe seção "Ações" dentro do passo de mensagem.** A ação é um passo
>   separado: botão **"Escolher Próximo Passo"** no fim da coluna.
> - Os modelos prontos marcados **"Quick Automation"** não servem: é o construtor
>   simplificado, sem Ações. Só **"Flow Builder"** serve.

---

O webhook já roda na VM e está exposto num HTTPS fixo pelo ngrok. O ManyChat
só precisa chamar essa URL em cada mensagem do cliente e devolver a resposta.

## Dados do endpoint da Ah Imobiliaria

- **URL:** `https://clergyman-rewrite-jolt.ngrok-free.dev/manychat/ah_imobiliaria`
- **Método:** POST
- **Headers:**
  - `Content-Type: application/json`
  - `X-Webhook-Secret: <o mesmo valor de WEBHOOK_SECRET na VM>`
  - `ngrok-skip-browser-warning: true`
- **Body (JSON):**
  ```json
  {
    "subscriber_id": "<ID do assinante>",
    "message_id": "<ID unico da mensagem>",
    "message": "<último texto que o cliente digitou>",
    "origem": "instagram",
    "name": "<nome do contato>",
    "phone": "<telefone, quando existir>",
    "email": "<email, quando existir>"
  }
  ```
- **Resposta:** `reply` traz o texto do agente. `handoff=true` significa que a
  IA esta pausada e o fluxo deve encaminhar o atendimento para uma pessoa.

O endpoint antigo `/manychat` continua atendendo o agente definido por
`WEBHOOK_AGENTE`. Assim a AIOTI e a Ah Imobiliaria nao dividem historico nem
misturam leads.

## Passo a passo no ManyChat

1. **Conectar o canal**
   - Instagram: conta Profissional/Business ligada a uma Página do Facebook.
   - WhatsApp: número novo (não usado no WhatsApp comum), plano pago do ManyChat.

2. **Criar a automação**
   - Automation → New Automation → gatilho **Default Reply** (responde qualquer
     mensagem) ou uma Keyword pra testar.

3. **Ação External Request** — 🔴 **É AQUI QUE TRAVA: recurso PRO.** Ver o aviso
   no topo do arquivo. No plano grátis ela aparece como "Fazer uma consulta
   externa" com selo PRO e não deixa adicionar.
   - Adicione o passo **External Request** (Actions).
   - Method: `POST`
   - Request URL: a URL do endpoint acima.
   - Headers: os três de cima.
   - Body → Raw / JSON: o corpo acima. Use o seletor de campos ("+"/`{}`) pra
     inserir o **Id do assinante** em `subscriber_id` e o **Last Text Input**
     em `message`.

4. **Mapear a resposta**
   - Em "Response Mapping", mapeie `$.reply` para um **Custom Field** (ex.:
     `resposta_ia`, tipo texto).
   - Mapeie tambem `$.handoff` para um campo booleano `transferir_corretor`.

5. **Enviar ou transferir**
   - Se `transferir_corretor` for falso, adicione **Send Message** com o
     conteúdo `{{resposta_ia}}`.
   - Se for verdadeiro, notifique o corretor e nao tente enviar uma mensagem
     vazia.

   ⚠️ **O passo "Condição" também é PRO.** Se um dia isto for retomado, dá pra
   dispensar a condição: a VM devolve no próprio `reply` o texto certo, inclusive
   quando for caso de transferir, e o Telegram da equipe avisa em paralelo. O
   fluxo fica com três peças só, todas de passos livres:
   `gatilho de DM → Executar Ações (consulta externa) → Enviar Mensagem {{resposta_ia}}`.

6. **Testar** - mande uma mensagem pro Instagram/WhatsApp conectado e veja a IA
   responder. O resumo do lead cai no Telegram da equipe, igual nos outros canais.

## Variaveis novas na VM

Adicione ao arquivo de ambiente do `leadiot-webhook`:

```ini
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sb_publishable_...
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...
CRM_AGENTE=ah_imobiliaria
CRM_ALLOWED_ORIGINS=https://filtroazul.github.io
```

Depois reinicie o servico. A chave `SUPABASE_SERVICE_ROLE_KEY` fica apenas na
VM. Ela nunca entra no GitHub Pages nem em `js/config.js`.

O segredo que já apareceu em arquivo ou mensagem deve ser rotacionado antes do
uso em produção. O documento guarda somente o placeholder.

## Trocar a URL depois (se precisar)

A URL do ngrok é fixa enquanto a conta ngrok for a mesma. Se um dia mudar de
túnel/domínio, é só reeditar a Request URL no passo External Request.
