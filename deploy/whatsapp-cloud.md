# WhatsApp Cloud API — ativação controlada

## Estado seguro publicado

- O endpoint é `GET/POST /whatsapp`.
- A automação nasce desligada com `WHATSAPP_AUTOMATION_ENABLED=false`.
- Mesmo ligada, responde somente a `WHATSAPP_TEST_RECIPIENTS` enquanto
  `WHATSAPP_ALLOW_ALL=false`.
- Todo POST exige `X-Hub-Signature-256` válido.
- Retries do mesmo `wamid` não geram uma segunda resposta já enviada.
- O teste controlado não dispara notificação de lead qualificado para a equipe.

## Checklist para o teste das 23h

1. Confirmar no painel da Meta se o número permite coexistência com o aplicativo
   WhatsApp Business e com a operação atual. Não remover o FazzLeads.
2. Obter `Phone Number ID`, token da Cloud API, segredo do app e criar o token
   de verificação do webhook.
3. Cadastrar o callback HTTPS terminado em `/whatsapp` e assinar o campo
   `messages` da conta do WhatsApp Business.
4. Definir somente o celular de teste em `WHATSAPP_TEST_RECIPIENTS`.
5. Manter `WHATSAPP_ALLOW_ALL=false`, ligar
   `WHATSAPP_AUTOMATION_ENABLED=true` e reiniciar o serviço.
6. Mandar uma mensagem do número autorizado, conferir resposta no WhatsApp e
   histórico no CRM.
7. Ao terminar, voltar `WHATSAPP_AUTOMATION_ENABLED=false` até a decisão de
   migração definitiva.

## Liberação definitiva

Somente depois de validar recebimento, resposta, histórico, pausa humana e
coexistência, avaliar `WHATSAPP_ALLOW_ALL=true`. Essa mudança é separada da
integração de formulários Meta Lead Ads.
