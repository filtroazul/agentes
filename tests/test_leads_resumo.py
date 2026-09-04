import unittest

from core import leads


class ResumoInternoTest(unittest.TestCase):
    def test_remove_resumo_com_separadores(self):
        texto = "Oi! Como posso ajudar?\n\n---\n📋 RESUMO DO LEAD\nNome: João\n---"
        self.assertEqual(leads.remover_resumo(texto), "Oi! Como posso ajudar?")

    def test_remove_resumo_mesmo_sem_separador(self):
        texto = "Oi! Como posso ajudar?\n\nRESUMO PARA O CORRETOR: teste"
        self.assertEqual(leads.remover_resumo(texto), "Oi! Como posso ajudar?")


if __name__ == "__main__":
    unittest.main()
