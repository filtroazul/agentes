import hashlib
import hmac
import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("GROQ_API_KEY", "gsk_teste")
os.environ.setdefault("WEBHOOK_AGENTE", "aioti")

import webhook_manychat


class MetaWebhookTest(unittest.TestCase):
    def setUp(self):
        self.client = webhook_manychat.app.test_client()
        self.env = patch.dict(
            os.environ,
            {"META_VERIFY_TOKEN": "verify-test", "META_APP_SECRET": "app-secret-test"},
        )
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_handshake_valido_devolve_challenge_em_texto(self):
        resposta = self.client.get(
            "/meta/lead-ads?hub.mode=subscribe&hub.verify_token=verify-test&hub.challenge=12345"
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data, b"12345")
        self.assertTrue(resposta.content_type.startswith("text/plain"))

    def test_handshake_rejeita_token_incorreto(self):
        resposta = self.client.get(
            "/meta/lead-ads?hub.mode=subscribe&hub.verify_token=errado&hub.challenge=12345"
        )
        self.assertEqual(resposta.status_code, 403)

    def test_post_rejeita_assinatura_incorreta(self):
        resposta = self.client.post(
            "/meta/lead-ads",
            data=b'{"object":"page"}',
            headers={"X-Hub-Signature-256": "sha256=errada"},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 401)

    @patch("webhook_manychat.meta_leads.processar_payload")
    def test_post_assinado_processa_payload(self, processar):
        payload = {"object": "page", "entry": []}
        corpo = json.dumps(payload, separators=(",", ":")).encode()
        assinatura = "sha256=" + hmac.new(
            b"app-secret-test", corpo, hashlib.sha256
        ).hexdigest()
        processar.return_value = {
            "recebidos": 0,
            "processados": 0,
            "duplicados": 0,
            "ignorados": 0,
        }
        resposta = self.client.post(
            "/meta/lead-ads",
            data=corpo,
            headers={"X-Hub-Signature-256": assinatura},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.get_json()["received"])
        processar.assert_called_once_with(payload)


if __name__ == "__main__":
    unittest.main()
