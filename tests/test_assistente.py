"""Testes automatizados. Rode com:  python -m unittest"""

import csv
import tempfile
import unittest
from pathlib import Path

from assistente import Assistente, carregar_servicos
from assistente import indicadores
from assistente.busca import LIMIAR
from assistente.privacidade import mascarar
from assistente.validacao import normalizar, validar_pergunta

ARQ_SERVICOS = Path(__file__).resolve().parent.parent / "dados" / "servicos.json"


class TestValidacao(unittest.TestCase):
    def test_normaliza_acento_e_caixa(self):
        self.assertEqual(normalizar("  Tenho DIREITO à  Tarifa "), "tenho direito a tarifa")

    def test_pontuacao_nao_atrapalha_a_busca(self):
        self.assertEqual(normalizar("Quais documentos levar?"), "quais documentos levar")

    def test_recusa_vazio(self):
        self.assertFalse(validar_pergunta("   ")[0])

    def test_recusa_so_simbolos(self):
        self.assertFalse(validar_pergunta("!!! ??? 123")[0])

    def test_recusa_texto_longo(self):
        self.assertFalse(validar_pergunta("a" * 301)[0])

    def test_recusa_tipo_errado(self):
        self.assertFalse(validar_pergunta(None)[0])

    def test_aceita_pergunta_comum(self):
        self.assertEqual(validar_pergunta("Quais documentos levar?"), (True, ""))


class TestPrivacidade(unittest.TestCase):
    def test_remove_cpf(self):
        self.assertNotIn("123.456.789-09", mascarar("meu cpf é 123.456.789-09"))

    def test_remove_email(self):
        self.assertIn("[e-mail removido]", mascarar("fale com joao@exemplo.com"))

    def test_mantem_texto_sem_dados(self):
        self.assertEqual(mascarar("tarifa social"), "tarifa social")


class TestAssistente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assistente = Assistente(carregar_servicos(ARQ_SERVICOS))

    def test_responde_com_servico_certo(self):
        resposta = self.assistente.responder("Tenho direito ao desconto na conta de luz?")
        self.assertTrue(resposta.respondeu)
        self.assertEqual(resposta.servico_id, "S001")

    def test_resposta_traz_fonte_e_aviso(self):
        resposta = self.assistente.responder("Quais documentos levar?")
        self.assertIn("atualizado em", resposta.fonte)
        self.assertTrue(resposta.aviso)

    def test_pergunta_sem_relacao_nao_responde(self):
        resposta = self.assistente.responder("qual a capital da frança")
        self.assertFalse(resposta.respondeu)

    def test_entrada_invalida_nao_responde(self):
        resposta = self.assistente.responder("")
        self.assertFalse(resposta.respondeu)
        self.assertEqual(resposta.confianca, 0.0)

    def test_confianca_sempre_entre_0_e_1(self):
        for pergunta in ["tarifa social direito desconto baixa renda", "documentos", "x"]:
            confianca = self.assistente.responder(pergunta).confianca
            self.assertTrue(0.0 <= confianca <= 1.0)

    def test_abaixo_do_limiar_nao_responde_com_certeza(self):
        resposta = self.assistente.responder("desconto")
        if resposta.confianca < LIMIAR:
            self.assertFalse(resposta.respondeu)


class TestIndicadores(unittest.TestCase):
    def test_registra_e_resume(self):
        assistente = Assistente(carregar_servicos(ARQ_SERVICOS))
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "consultas.csv"
            for pergunta in ["tenho direito ao desconto", "qual a capital da frança"]:
                resposta = assistente.responder(pergunta)
                indicadores.registrar(arq, pergunta, resposta, 1.5)

            dados = indicadores.resumir(arq)
            self.assertEqual(dados["total"], 2)
            self.assertEqual(dados["taxa_resposta"], 0.5)

    def test_nao_grava_dado_pessoal(self):
        assistente = Assistente(carregar_servicos(ARQ_SERVICOS))
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "consultas.csv"
            pergunta = "tarifa social, meu cpf 123.456.789-09"
            indicadores.registrar(arq, pergunta, assistente.responder(pergunta), 1.0)
            conteudo = arq.read_text(encoding="utf-8")
            self.assertNotIn("123.456.789-09", conteudo)

    def test_resumo_sem_arquivo(self):
        dados = indicadores.resumir(Path("nao_existe.csv"))
        self.assertEqual(dados["total"], 0)


if __name__ == "__main__":
    unittest.main()
