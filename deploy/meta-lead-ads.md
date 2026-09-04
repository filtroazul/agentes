# Meta Lead Ads em paralelo com o FazzLeads

Este fluxo recebe formulários instantâneos da Meta no CRM próprio sem desligar
nem alterar o FazzLeads:

```text
Meta Lead Ads -> POST /meta/lead-ads -> Graph API -> Supabase -> painel + aviso
                                      |-> meta_webhook_eventos (retry/falhas)
```

## O que já está protegido no código

- handshake por `META_VERIFY_TOKEN`;
- validação de cada POST com `X-Hub-Signature-256` e o App Secret;
- consulta do `leadgen_id` na Graph API com `appsecret_proof`;
- filtros opcionais por Page ID e Form ID;
- índice único por `leadgen_id`, inclusive sob entregas simultâneas;
- fila durável com estado `pendente`, `processado`, `erro` ou `ignorado`;
- nenhum token, payload ou dado pessoal escrito nos logs;
- lead de formulário nasce com `ia_ativa=false`;
- telefone sem resposta explícita de consentimento deixa
  `whatsapp_opt_in=NULL`.

As referências oficiais usadas foram o
[exemplo de Lead Ads da Meta](https://github.com/fbsamples/lead-ads-webhook-sample),
a [classe Lead do Business SDK](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/lead.py)
e a [documentação de Webhooks](https://developers.facebook.com/docs/graph-api/webhooks/getting-started/webhooks-for-leadgen/).

## Onde isto parou (03/set)

Passos 1 e 2 **feitos e conferidos**. Falta o 3, que depende da conta do
Alejandro no Facebook.

A ordem não é opcional: o painel da Meta valida a Callback URL no momento em
que você salva. Sem o passo 2 o endpoint responde 404 e a Meta recusa o
cadastro — foi exatamente onde a primeira tentativa travou.

Nesta fase o health responde `meta_leads:false` de propósito: `configurado()`
exige App Secret e token da Página. O handshake, que só usa o
`META_VERIFY_TOKEN`, já funciona e é o que a Meta checa pra aceitar a URL.

## 1. Aplicar o banco

No SQL Editor do projeto `ah.imobiliaria`, execute inteiro:

```text
ah-imobiliaria/supabase/migrations/20260903_meta_lead_ads.sql
```

É idempotente e não altera os leads existentes.

Depois confira:

```sql
select column_name
from information_schema.columns
where table_schema = 'public' and table_name = 'leads'
  and column_name in ('leadgen_id', 'meta_campaign_id', 'whatsapp_opt_in');

select relname
from pg_class
where relname in ('leads_leadgen_id_unico', 'meta_webhook_eventos');
```

## 2. Configurar a VM

Use `deploy/leadiot-webhook.env.example` como referência. No servidor, edite
somente `/etc/leadiot-webhook.env` e mantenha o modo `600`:

```bash
sudo cp /etc/leadiot-webhook.env /etc/leadiot-webhook.env.bak-meta-$(date +%Y%m%d)
sudo nano /etc/leadiot-webhook.env
sudo chmod 600 /etc/leadiot-webhook.env
sudo systemctl restart leadiot-webhook
```

Variáveis obrigatórias novas:

```ini
META_VERIFY_TOKEN=segredo-longo-criado-por-voce
META_APP_SECRET=segredo-do-app-meta
META_PAGE_ACCESS_TOKEN=token-da-pagina-ou-usuario-de-sistema
META_GRAPH_API_VERSION=v26.0
META_ALLOWED_PAGE_IDS=ID_DA_PAGINA
META_ALLOWED_FORM_IDS=ID_FORM_1,ID_FORM_2
META_WHATSAPP_OPT_IN_FIELDS=nome_tecnico_da_pergunta_de_consentimento
```

Para mais de uma página, prefira `META_PAGE_ACCESS_TOKENS_JSON` com um token
por Page ID. Nunca coloque esses valores em `js/config.js`, GitHub ou arquivos
do site público.

O health check deve passar a mostrar:

```json
{"ok":true,"crm":true,"meta_leads":true}
```

## 3. Preparar o app da Meta

Antes de conectar, confirmar que Alejandro controla o portfólio empresarial,
a Página, a conta de anúncios e os formulários. Não remover a FazzLeads.

No app em `developers.facebook.com`:

1. adicionar o produto **Webhooks**;
2. escolher o objeto **Page** e o campo **leadgen**;
3. usar como Callback URL `https://SEU-DOMINIO/meta/lead-ads`;
4. informar exatamente o mesmo `META_VERIFY_TOKEN` da VM;
5. gerar um token autorizado para recuperar leads da Página;
6. garantir `leads_retrieval` e a permissão necessária para gerenciar a
   assinatura da Página (`pages_manage_metadata`); a Meta pode exigir revisão
   e permissões adicionais conforme o tipo de token/ativo;
7. assinar o app na Página para `leadgen`;
8. testar com a ferramenta de teste de formulário da própria Meta.

Em modo de desenvolvimento, leads reais de pessoas fora dos papéis do app
podem não ser entregues. A ativação pública depende das permissões e da revisão
mostradas no painel do app.

## 4. Regra do consentimento

O formulário deve ter uma pergunta explícita para WhatsApp. Configure em
`META_WHATSAPP_OPT_IN_FIELDS` o **nome técnico** devolvido pela Graph API.

O código reconhece respostas afirmativas e negativas, mas não inventa
consentimento. Para prova jurídica completa, arquive também a versão/texto do
formulário publicado na Meta; o webhook recebe o nome do campo e a resposta,
não é usado como arquivo histórico do texto legal.

Mesmo com opt-in, iniciar conversa pela API do WhatsApp fora da janela de
atendimento exige o template aplicável e aprovado. Nesta fase o webhook apenas
cria o lead, marca prioridade e avisa a equipe.

## 5. Operação paralela

Durante pelo menos duas semanas:

1. manter FazzLeads e o webhook próprio ativos;
2. comparar diariamente `leadgen_id`, Page, formulário, campanha, conjunto e
   anúncio;
3. investigar qualquer linha em `meta_webhook_eventos` com erro:

```sql
select leadgen_id, page_id, form_id, status, tentativas, ultimo_erro, atualizado_em
from public.meta_webhook_eventos
where status in ('pendente', 'erro')
order by atualizado_em;
```

4. não fazer contato automático enquanto `whatsapp_opt_in` for `NULL` ou
   `false`;
5. só planejar a retirada do FazzLeads depois de 100% de correspondência na
   captura e depois de identificar o provedor do módulo `WhatsApp Alejandro`.

## 6. Testes locais

```bash
python -m unittest discover -s tests -p "test_*meta*.py" -v
```

Os testes usam payloads fictícios e não chamam Meta, Supabase ou Telegram.
