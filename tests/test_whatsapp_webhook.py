import hashlib
import hmac
import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("GROQ_API_KEY", "gsk_teste")
os.environ.setdefault("WEBHOOK_AGENTE", "aioti")

import webhook_manychat


NUMERO = "5585999999999"


def payload_whatsapp():
    return {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "metadata": {"phone_number_id": "phone-1"},
            "contacts": [{"wa_id": NUMERO, "profile": {"name": "Cliente Teste"}}],
            "messages": [{
                "from": NUMERO,
                "id": "wamid.entrada",
                "type": "text",
                "text": {"body": "Quero comprar um apartamento"},
            }],
        }}]}],
    }


class WhatsAppWebhookTest(unittest.TestCase):
    def setUp(self):
        self.client = webhook_manychat.app.test_client()
        self.env = patch.dict(
            os.environ,
            {
                "WHATSAPP_VERIFY_TOKEN": "verify-test",
                "WHATSAPP_APP_SECRET": "app-secret-test",
                "WHATSAPP_ACCESS_TOKEN": "access-test",
                "WHATSAPP_PHONE_NUMBER_ID": "phone-1",
                "WHATSAPP_AUTOMATION_ENABLED": "true",
                "WHATSAPP_TEST_RECIPIENTS": NUMERO,
                "WHATSAPP_ALLOW_ALL": "false",
            },
        )
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def _post_assinado(self, payload):
        corpo = json.dumps(payload, separators=(",", ":")).encode()
        assinatura = "sha256=" + hmac.new(
            b"app-secret-test", corpo, hashlib.sha256
        ).hexdigest()
        return self.client.post(
            "/whatsapp",
            data=corpo,
            headers={"X-Hub-Signature-256": assinatura},
            content_type="application/json",
        )

    def test_handshake_valido(self):
        resposta = self.client.get(
            "/whatsapp?hub.mode=subscribe&hub.verify_token=verify-test&hub.challenge=987"
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data, b"987")

    def test_rejeita_assinatura_incorreta(self):
        resposta = self.client.post(
            "/whatsapp",
            data=b"{}",
            headers={"X-Hub-Signature-256": "sha256=incorreta"},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 401)

    def test_automacao_desligada_confirma_sem_processar(self):
        with patch.dict(os.environ, {"WHATSAPP_AUTOMATION_ENABLED": "false"}):
            resposta = self._post_assinado(payload_whatsapp())
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.get_json()["inactive"])

    @patch("webhook_manychat.whatsapp_cloud.enviar_texto", return_value="wamid.saida")
    @patch("webhook_manychat.agent.responder", return_value="Qual faixa de valor você procura?")
    @patch("webhook_manychat.crm.historico_do_lead")
    @patch("webhook_manychat.crm.configuracao_ia")
    @patch("webhook_manychat.crm.registrar_saida")
    @patch("webhook_manychat.crm.registrar_entrada")
    @patch("webhook_manychat.crm.disponivel", return_value=True)
    def test_processa_e_responde_apenas_numero_autorizado(
        self, disponivel, registrar_entrada, registrar_saida, configuracao, historico,
        responder, enviar,
    ):
        registrar_entrada.return_value = ({"id": "lead-1", "ia_ativa": True}, True)
        configuracao.return_value = {"modo": "automatico", "canais": ["whatsapp"]}
        historico.return_value = [{"role": "user", "content": "Quero comprar"}]
        with patch.object(
            webhook_manychat,
            "_agentes",
            {"ah_imobiliaria": {"prompt": "Atenda imóveis."}},
        ), patch("webhook_manychat.crm.atualizar_metadados_interacao"):
            resposta = self._post_assinado(payload_whatsapp())

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["processed"], 1)
        enviar.assert_called_once_with(NUMERO, "Qual faixa de valor você procura?")
        registrar_saida.assert_called_once()

    @patch("webhook_manychat.crm.interacao_por_external_id")
    @patch("webhook_manychat.crm.registrar_entrada")
    @patch("webhook_manychat.crm.disponivel", return_value=True)
    @patch("webhook_manychat.whatsapp_cloud.enviar_texto")
    def test_retry_ja_enviado_nao_duplica_resposta(
        self, enviar, disponivel, registrar_entrada, interacao,
    ):
        registrar_entrada.return_value = ({"id": "lead-1", "ia_ativa": True}, False)
        interacao.return_value = {
            "conteudo": "Resposta anterior",
            "metadados": {"status_envio": "enviado", "wamid": "wamid.saida"},
        }
        resposta = self._post_assinado(payload_whatsapp())
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["processed"], 0)
        enviar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
