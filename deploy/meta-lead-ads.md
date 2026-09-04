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

## Estado final em 04/set

Banco e backend estão prontos. No app da Meta, a Callback URL foi validada,
o objeto **Page** foi selecionado e o campo **leadgen** ficou em **Assinado**.
FazzLeads, WhatsApp e campanhas continuam intactos.

A ordem não é opcional: o painel da Meta valida a Callback URL no momento em
que você salva. Sem o passo 2 o endpoint responde 404 e a Meta recusa o
cadastro — foi exatamente onde a primeira tentativa travou.

O health agora responde `meta_leads:true`. App Secret e token da Página estão
no env protegido da VM, nunca em arquivo local ou Git. A Graph API confirmou:

- `leads_retrieval`, `pages_show_list`, `pages_read_engagement`,
  `pages_manage_metadata` e `business_management` concedidos;
- o app inscrito na Página AH Imóveis com `leadgen`;
- a assinatura Page/`leadgen` ativa no app e a Callback URL correta.

O teste assinado completo passou: o backend recuperou o lead sintético na
Graph API, gravou o evento como `processado`, criou exatamente um lead
`meta_ads` e ignorou a repetição sem duplicar.

O teste oficial em **Webhooks → Page → leadgen → Teste** também passou: a Meta
enviou um POST real, o endpoint respondeu HTTP 200 e o evento foi corretamente
marcado como `ignorado`, porque o payload de exemplo usa uma Page fictícia.
Isso valida a entrega Meta → endpoint. O teste precisou ser aberto em uma sessão
limpa porque uma extensão do Brave bloqueava o carregamento dos dados de
exemplo.

O app **AH Imoveis Leads CRM** foi publicado depois do cadastro das páginas
legais públicas, domínio e ícone exigidos pela Meta. Em seguida, foi excluído o
lead sintético antigo e criado outro pela ferramenta oficial no formulário real
da Página AH Imóveis. A Meta marcou `Success` tanto para o app próprio quanto
para o LeadConnector/FazzLeads.

No backend, esse novo evento ficou `processado` na primeira tentativa, sem erro,
com Page e formulário corretos. No Supabase foi criada exatamente uma linha em
`leads`, com origem `meta_ads`. Isso valida o caminho completo Meta → webhook →
Graph API → Supabase → CRM já com o app público. FazzLeads, WhatsApp e campanhas
continuam intactos; manter os dois captadores em paralelo durante a conferência
operacional.

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

1. ✅ adicionar o produto **Webhooks**;
2. ✅ escolher o objeto **Page** e o campo **leadgen**;
3. ✅ usar como Callback URL `https://SEU-DOMINIO/meta/lead-ads`;
4. ✅ informar exatamente o mesmo `META_VERIFY_TOKEN` da VM;
5. gerar um token autorizado para recuperar leads da Página;
6. garantir `leads_retrieval` e a permissão necessária para gerenciar a
   assinatura da Página (`pages_manage_metadata`); a Meta pode exigir revisão
   e permissões adicionais conforme o tipo de token/ativo;
7. assinar o app na Página para `leadgen`;
8. testar com a ferramenta de teste de formulário da própria Meta.

O app está publicado. Se um novo formulário ou uma nova Página for usado, será
necessário adicioná-lo aos filtros da VM e assinar essa Página em `leadgen` antes
de esperar a entrega.

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

## 6. Testar o chatbot sem tocar no WhatsApp

No painel publicado, abra **Leads e funil → Atendimento com IA → Testar
chatbot**. A rota autenticada `POST /crm/testar-chat` usa o agente real e o
catálogo, mas não persiste histórico, não cria lead e não possui envio para
WhatsApp, ManyChat ou FazzLeads. O botão **Nova conversa** limpa o contexto; um
recarregamento da página também apaga tudo.

Esse teste valida o cérebro, não o canal. Para o atendimento aparecer no número
real ainda será necessário conectar a WhatsApp Business Platform, receber as
mensagens por webhook e enviar as respostas pela API oficial. Não desconectar o
FazzLeads antes de validar a opção de coexistência ou uma migração controlada.

## 7. Testes locais

```bash
python -m unittest discover -s tests -p "test_*meta*.py" -v
```

Os testes usam payloads fictícios e não chamam Meta, Supabase ou Telegram.
