# Ligar a IA no ManyChat (Instagram DM e WhatsApp)

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

3. **Ação External Request**
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
