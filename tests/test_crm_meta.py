import unittest
from unittest.mock import patch

from core import crm


class CRMMetaTest(unittest.TestCase):
    @patch("core.crm.disponivel", return_value=True)
    @patch("core.crm._rest")
    def test_cria_lead_meta_sem_ativar_ia(self, rest, _disponivel):
        rest.side_effect = [
            [],
            [{"id": "crm-1", "leadgen_id": "lead-1"}],
            [],
            [],
        ]

        lead, criado = crm.registrar_lead_meta(
            {
                "leadgen_id": "lead-1",
                "nome": "Maria",
                "telefone": "+55 (85) 99999-1111",
                "mensagem": "Formulário da Meta recebido.",
                "whatsapp_opt_in": None,
            }
        )

        self.assertTrue(criado)
        self.assertEqual(lead["id"], "crm-1")
        chamada_criacao = rest.call_args_list[1]
        registro = chamada_criacao.kwargs["json"]
        self.assertEqual(registro["origem"], "meta_ads")
        self.assertEqual(registro["telefone"], "5585999991111")
        self.assertFalse(registro["ia_ativa"])
        self.assertIsNone(registro["whatsapp_opt_in"])

        chamada_interacao = rest.call_args_list[3]
        interacao = chamada_interacao.kwargs["json"]
        self.assertEqual(interacao["canal"], "meta_ads")
        self.assertEqual(interacao["external_id"], "meta-lead:lead-1")


if __name__ == "__main__":
    unittest.main()
