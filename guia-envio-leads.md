# Guia — envio de leads pra equipe (Telegram + Planilha Google)

> O app já detecta o RESUMO DO LEAD e envia pros destinos configurados nos
> secrets. Este guia é o passo a passo pra ativar cada destino — pra você e
> pra cada cliente novo. Nada aqui exige mexer em código.

## 1. Telegram (aviso na hora no celular) — ~2 min

1. No Telegram, fale com **@BotFather** → `/newbot` → dê um nome (ex.:
   "Leads AH") → copie o **token** (formato `123456:ABC...`).
2. Mande um "oi" pro seu bot recém-criado (procure pelo @ dele).
3. Abra no navegador: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   → ache `"chat":{"id":123456789` → esse número é o **chat_id**.
4. Cole nos secrets (Streamlit Cloud: App → Settings → Secrets):

```toml
TELEGRAM_BOT_TOKEN = "123456:ABC-seu-token"
TELEGRAM_CHAT_ID = "123456789"
```

**Pra cliente receber direto**: crie um grupo no Telegram, adicione o SEU bot
e a equipe do cliente, mande um "oi" no grupo e pegue o chat_id do grupo no
mesmo `getUpdates` (id de grupo é negativo, ex.: `-100987...`). Depois:

```toml
TELEGRAM_CHAT_ID_AIOTI = "-100987654321"
```

Um bot só serve todos os clientes — o que muda é o chat_id por agente.

## 2. Planilha Google (funil de leads) — ~5 min

1. Crie a planilha: https://sheets.new (ex.: "Funil de Leads").
2. Menu **Extensões → Apps Script**. Apague o que estiver lá e cole:

```javascript
const ABA = "Leads";

function doPost(e) {
  const dados = JSON.parse(e.postData.contents);
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  let aba = planilha.getSheetByName(ABA);
  if (!aba) {
    aba = planilha.insertSheet(ABA);
    aba.appendRow(["Momento", "Agente", "Resumo", "Status", "Obs da equipe"]);
    aba.setFrozenRows(1);
  }
  aba.appendRow([dados.momento, dados.agente, dados.resumo, "novo", ""]);
  return ContentService.createTextOutput("ok");
}
```

3. **Implantar → Nova implantação → tipo: App da Web**:
   - Executar como: **Eu**
   - Quem pode acessar: **Qualquer pessoa** (necessário pro app conseguir postar;
     a URL é secreta e só recebe dados, não lê nada da sua conta)
4. Autorize quando o Google pedir e copie a **URL do app da Web** (`https://script.google.com/macros/s/.../exec`).
5. Cole nos secrets:

```toml
LEADS_WEBHOOK_URL = "https://script.google.com/macros/s/SEU_ID/exec"
```

Cada lead vira uma linha com status "novo" — a equipe atualiza a coluna
Status (contatado → proposta → fechado) e isso é o funil. **Esses números
alimentam o case** (`vendas/case-esqueleto.md`): leads atendidos, qualificados
por semana, taxa de fechamento.

**Planilha por cliente**: repita os passos na planilha DO CLIENTE (ou numa que
você compartilha com ele) e use o sufixo:

```toml
LEADS_WEBHOOK_URL_AIOTI = "https://script.google.com/macros/s/OUTRO_ID/exec"
```

## 3. Como o app decide pra onde enviar

- Existe `TELEGRAM_CHAT_ID_<AGENTE>`? Usa ele. Senão usa `TELEGRAM_CHAT_ID`.
- Existe `LEADS_WEBHOOK_URL_<AGENTE>`? Usa ele. Senão usa `LEADS_WEBHOOK_URL`.
- Telegram e webhook configurados = envia pros DOIS.
- Nenhum configurado = só mostra o card na conversa (nada quebra).
- `<AGENTE>` = nome do agente no agents.yaml em MAIÚSCULO (ex.: `AIOTI`,
  `CORRETOR_IMOVEIS`).

## 4. Testar depois de configurar

Abra o link demo (`?agente=...`), converse como lead até sair o card verde de
resumo e confira: mensagem no Telegram + linha nova na planilha + legenda
"Resumo enviado para a equipe ✓" no chat.

## Checklist de setup de cliente novo (o que o setup cobra)

- [ ] Agente no `agents.yaml` (ramo, tom, perguntas, resumo) + push
- [ ] Widget no site do cliente OU link no ManyChat/bio
- [ ] Grupo no Telegram com o bot + `TELEGRAM_CHAT_ID_<AGENTE>` nos secrets
- [ ] Planilha de funil + `LEADS_WEBHOOK_URL_<AGENTE>` nos secrets
- [ ] Teste de lead completo de ponta a ponta
- [ ] Ensinar a equipe: responder o lead + atualizar o Status na planilha
