import hashlib
import hmac
import unittest
from unittest.mock import patch

from core import meta_leads


class MetaLeadsTest(unittest.TestCase):
    def test_valida_assinatura_sha256(self):
        corpo = b'{"object":"page"}'
        segredo = "segredo-de-teste"
        assinatura = "sha256=" + hmac.new(
            segredo.encode(), corpo, hashlib.sha256
        ).hexdigest()
        self.assertTrue(meta_leads.assinatura_valida(corpo, assinatura, segredo=segredo))
        self.assertFalse(meta_leads.assinatura_valida(corpo + b"x", assinatura, segredo=segredo))

    def test_extrai_somente_eventos_leadgen(self):
        payload = {
            "object": "page",
            "entry": [
                {
                    "id": "page-1",
                    "time": 123,
                    "changes": [
                        {"field": "feed", "value": {"item": "post"}},
                        {
                            "field": "leadgen",
                            "value": {
                                "leadgen_id": "lead-1",
                                "form_id": "form-1",
                                "created_time": 122,
                            },
                        },
                    ],
                }
            ],
        }
        self.assertEqual(
            meta_leads.extrair_notificacoes(payload),
            [
                {
                    "leadgen_id": "lead-1",
                    "page_id": "page-1",
                    "form_id": "form-1",
                    "ad_id": None,
                    "created_time": 122,
                }
            ],
        )

    def test_normaliza_atribuicao_contato_e_opt_in_explicito(self):
        graph = {
            "id": "lead-1",
            "created_time": "2026-09-03T12:00:00+0000",
            "campaign_id": "camp-1",
            "campaign_name": "MCMV Fortaleza",
            "adset_id": "set-1",
            "adset_name": "Aberto 17km",
            "ad_id": "ad-1",
            "ad_name": "Criativo A",
            "form_id": "form-1",
            "platform": "facebook",
            "is_organic": False,
            "field_data": [
                {"name": "full_name", "values": ["Maria Silva"]},
                {"name": "phone_number", "values": ["+55 (85) 99999-1111"]},
                {"name": "email", "values": ["maria@example.com"]},
                {"name": "autoriza_contato_por_whatsapp", "values": ["Sim, autorizo"]},
                {"name": "bairro_de_interesse", "values": ["Eusébio"]},
            ],
        }
        dados = meta_leads.normalizar_lead(
            graph, {"leadgen_id": "lead-1", "page_id": "page-1", "form_id": "form-1"}
        )
        self.assertEqual(dados["nome"], "Maria Silva")
        self.assertEqual(dados["telefone"], "+55 (85) 99999-1111")
        self.assertEqual(dados["meta_campaign_id"], "camp-1")
        self.assertEqual(dados["meta_adset_id"], "set-1")
        self.assertEqual(dados["meta_ad_id"], "ad-1")
        self.assertTrue(dados["whatsapp_opt_in"])
        self.assertEqual(
            dados["whatsapp_opt_in_fonte"],
            "meta_form:autoriza_contato_por_whatsapp",
        )
        self.assertIn("Bairro De Interesse: Eusébio", dados["mensagem"])

    def test_telefone_sem_pergunta_nao_vira_consentimento(self):
        dados = meta_leads.normalizar_lead(
            {
                "id": "lead-2",
                "field_data": [{"name": "phone_number", "values": ["85999991111"]}],
            },
            {"leadgen_id": "lead-2", "page_id": "page-1"},
        )
        self.assertIsNone(dados["whatsapp_opt_in"])
        self.assertIsNone(dados["whatsapp_opt_in_em"])

    def test_recusa_explicita_vira_false(self):
        dados = meta_leads.normalizar_lead(
            {
                "id": "lead-3",
                "created_time": "2026-09-03T12:00:00+0000",
                "field_data": [
                    {
                        "name": "autoriza_contato_por_whatsapp",
                        "values": ["Não autorizo"],
                    }
                ],
            },
            {"leadgen_id": "lead-3", "page_id": "page-1"},
        )
        self.assertIs(dados["whatsapp_opt_in"], False)
        self.assertIsNone(dados["whatsapp_opt_in_em"])

    @patch("core.meta_leads.leads.enviar_lead")
    @patch("core.meta_leads.crm.marcar_evento_meta")
    @patch("core.meta_leads.crm.registrar_lead_meta")
    @patch("core.meta_leads.buscar_lead")
    @patch("core.meta_leads.crm.preparar_evento_meta")
    def test_processa_e_notifica_apenas_lead_novo(
        self, preparar, buscar, registrar, marcar, notificar
    ):
        preparar.return_value = True
        buscar.return_value = {"id": "lead-1", "field_data": []}
        registrar.return_value = ({"id": "crm-1", "leadgen_id": "lead-1"}, True)

        resultado = meta_leads.processar_notificacao(
            {"leadgen_id": "lead-1", "page_id": "page-1", "form_id": "form-1"}
        )

        self.assertEqual(resultado["status"], "processado")
        marcar.assert_called_once_with("lead-1", "processado", lead_id="crm-1")
        notificar.assert_called_once()

    @patch.dict("os.environ", {"CRM_AGENTE": "agente-teste"})
    @patch("core.meta_leads.leads.enviar_lead")
    @patch("core.meta_leads.crm.marcar_evento_meta")
    @patch("core.meta_leads.crm.registrar_lead_meta")
    @patch("core.meta_leads.buscar_lead")
    @patch("core.meta_leads.crm.preparar_evento_meta")
    def test_notificacao_respeita_agente_configurado(
        self, preparar, buscar, registrar, _marcar, notificar
    ):
        preparar.return_value = True
        buscar.return_value = {"id": "lead-1", "field_data": []}
        registrar.return_value = ({"id": "crm-1", "leadgen_id": "lead-1"}, True)

        meta_leads.processar_notificacao({"leadgen_id": "lead-1"})

        self.assertEqual(notificar.call_args.args[0], "agente-teste")

    @patch("core.meta_leads.crm.marcar_evento_meta")
    @patch("core.meta_leads.buscar_lead", side_effect=meta_leads.MetaErro("falhou"))
    @patch("core.meta_leads.crm.preparar_evento_meta", return_value=True)
    def test_falha_fica_marcada_para_retry(self, _preparar, _buscar, marcar):
        with self.assertRaises(meta_leads.MetaErro):
            meta_leads.processar_notificacao({"leadgen_id": "lead-erro"})
        marcar.assert_called_once_with("lead-erro", "erro", erro="falhou")

    @patch.dict("os.environ", {"META_ALLOWED_PAGE_IDS": "page-certa"})
    @patch("core.meta_leads.crm.marcar_evento_meta")
    @patch("core.meta_leads.crm.preparar_evento_meta", return_value=True)
    def test_pagina_fora_da_allowlist_e_ignorada(self, _preparar, marcar):
        with patch("core.meta_leads.buscar_lead") as buscar:
            resultado = meta_leads.processar_notificacao(
                {"leadgen_id": "lead-1", "page_id": "page-errada"}
            )
        self.assertEqual(resultado["status"], "ignorado")
        marcar.assert_called_once_with("lead-1", "ignorado")
        buscar.assert_not_called()

    @patch("core.meta_leads.crm.preparar_evento_meta", return_value=False)
    def test_retry_processado_nao_busca_graph_novamente(self, _preparar):
        with patch("core.meta_leads.buscar_lead") as buscar:
            resultado = meta_leads.processar_notificacao({"leadgen_id": "lead-1"})
        self.assertEqual(resultado["status"], "duplicado")
        buscar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
