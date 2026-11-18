import contextlib
import csv
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from assistente import Assistente, tem_dado_pessoal
from base_conhecimento import BaseConhecimento, nivel_confianca, normalizar

JSON_REAL = RAIZ / "data" / "base_conhecimento.json"

EXEMPLO_SUS = [
    {"id": 3, "categoria": "Saúde", "titulo": "Fazer o Cartão Nacional de Saúde (Cartão SUS)",
     "palavras_chave": ["cartao sus", "cartao do sus", "sus", "cns"],
     "resposta": "Pode ser feito em uma UBS ou no app Meu SUS Digital.",
     "documentos": ["Documento com foto", "CPF"], "onde": "Qualquer UBS", "fonte": "https://www.gov.br/saude",
     "verificado_em": "2026-11-05"},
    {"id": 4, "categoria": "Trabalho", "titulo": "Carteira de trabalho digital", "palavras_chave": ["carteira de trabalho", "ctps", "emprego"],
     "resposta": "Baixe o app.", "documentos": [], "onde": "App", "fonte": "https://www.gov.br", "verificado_em": "2026-11-05"},
]

# (pergunta de cidadão, id esperado em 1º lugar; None = não deve encontrar)
PERGUNTAS = [
    ("Quem tem direito à tarifa social?", 1),
    ("Como funciona a tarifa social?", 1),
    ("Quem recebe BPC tem desconto?", 1),
    ("Qual o desconto para quem consome até 80 kWh?", 5),
    ("O desconto de 65% ainda vale?", 6),
    ("Qual a regra antiga de 40%?", 6),
    ("Sou indígena, tenho desconto maior?", 2),
    ("Famílias quilombolas têm direito?", 2),
    ("Até quantos kWh indígenas têm 100%?", 2),
    ("Quem tem doença pode ter tarifa social?", 3),
    ("Moro em duas casas, posso ter em ambas?", 4),
    ("Renda de um salário mínimo tem desconto?", 7),
    ("Tem isenção de 120 kWh?", 7),
    ("Como ler minha fatura?", 8),
    ("O que significa encargos na conta?", 8),
    ("Preciso levar quais documentos?", 9),
    ("Prédio com várias famílias, como pedir cadastro?", 10),
    ("Ninguém me avisou que eu tinha direito", 11),
    ("Mudei de casa, o que faço?", 12),
    ("Cortaram minha luz por atraso", 13),
    ("Como instalar medidor individual?", 14),
    ("Como economizar energia com a geladeira?", 15),
    ("Quanto custa uma pizza?", None),
]


def rodar(metodo, entradas):
    saida = io.StringIO()
    with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
        metodo()
    return saida.getvalue()


class TestNormalizar(unittest.TestCase):
    def test_remove_acentos_pontuacao_e_caixa(self):
        self.assertEqual(normalizar("Como faço o Cartão do SUS?"), " como faco o cartao do sus ")

    def test_espacos_extras(self):
        self.assertEqual(normalizar("  olá,   mundo!  "), " ola mundo ")


class TestBaseReal(unittest.TestCase):
    def setUp(self):
        self.base = BaseConhecimento(JSON_REAL)
        self.assertTrue(self.base.carregar(), self.base.erro)

    def test_tamanho_e_categorias(self):
        self.assertGreaterEqual(len(self.base.orientacoes), 10)
        self.assertGreaterEqual(len(self.base.categorias()), 3)

    def test_campos_e_regras_do_enunciado(self):
        for o in self.base.orientacoes:
            self.assertGreaterEqual(len(o.palavras_chave), 3, o.titulo)
            self.assertTrue(o.fonte.startswith("https://"), o.titulo)
            self.assertRegex(o.verificado_em, r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(o.resposta and o.onde, o.titulo)
            self.assertIsInstance(o.documentos, list)

    def test_ids_unicos(self):
        ids = [o.id for o in self.base.orientacoes]
        self.assertEqual(len(ids), len(set(ids)))

    def test_por_categoria(self):
        for categoria in self.base.categorias():
            self.assertTrue(all(o.categoria == categoria for o in self.base.por_categoria(categoria)))


class TestBaseInvalida(unittest.TestCase):
    def tentar(self, conteudo):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "base.json"
            if conteudo is not None:
                arquivo.write_text(conteudo, encoding="utf-8")
            base = BaseConhecimento(arquivo)
            return base.carregar(), base.erro

    def test_arquivo_ausente(self):
        ok, erro = self.tentar(None)
        self.assertFalse(ok)
        self.assertIn("não encontrado", erro)

    def test_json_corrompido(self):
        ok, erro = self.tentar("[{ isto não é json")
        self.assertFalse(ok)
        self.assertIn("corrompido", erro)

    def test_registro_sem_campo(self):
        ok, erro = self.tentar(json.dumps([{"id": 1, "titulo": "x"}]))
        self.assertFalse(ok)
        self.assertIn("campos ausentes", erro)

    def test_lista_vazia_e_tipo_errado(self):
        self.assertFalse(self.tentar("[]")[0])
        self.assertFalse(self.tentar('{"a": 1}')[0])

    def test_ids_repetidos(self):
        dados = [dict(EXEMPLO_SUS[0]), dict(EXEMPLO_SUS[0])]
        ok, erro = self.tentar(json.dumps(dados))
        self.assertFalse(ok)
        self.assertIn("ids repetidos", erro)


class TestPontuacao(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        arquivo = Path(self.pasta.name) / "base.json"
        arquivo.write_text(json.dumps(EXEMPLO_SUS), encoding="utf-8")
        self.base = BaseConhecimento(arquivo)
        self.assertTrue(self.base.carregar())

    def tearDown(self):
        self.pasta.cleanup()

    def test_exemplo_do_enunciado_vale_7_pontos(self):
        resultados = self.base.buscar("Como faço o cartão do SUS?")
        pontos, melhor = resultados[0]
        self.assertEqual((pontos, melhor.id), (7, 3))
        self.assertEqual(nivel_confianca(pontos), "ALTA")

    def test_buscar_devolve_tuplas_da_maior_para_a_menor(self):
        resultados = self.base.buscar("cartao sus e carteira de trabalho")
        self.assertTrue(all(isinstance(r, tuple) and len(r) == 2 for r in resultados))
        pontos = [r[0] for r in resultados]
        self.assertEqual(pontos, sorted(pontos, reverse=True))

    def test_limites_da_confianca(self):
        self.assertEqual(nivel_confianca(6), "ALTA")
        self.assertEqual(nivel_confianca(5), "MÉDIA")
        self.assertEqual(nivel_confianca(3), "MÉDIA")
        self.assertIsNone(nivel_confianca(2))

    def test_palavra_chave_repetida_so_conta_uma_vez(self):
        self.base.orientacoes[0].palavras_chave = ["sus", "SUS", "sús"]
        self.assertEqual(self.base.pontuar("sus", self.base.orientacoes[0]), 3)


class TestBuscaComPerguntasReais(unittest.TestCase):
    def test_primeira_orientacao_esperada(self):
        base = BaseConhecimento(JSON_REAL)
        self.assertTrue(base.carregar())
        for pergunta, esperado in PERGUNTAS:
            with self.subTest(pergunta=pergunta):
                resultados = base.buscar(pergunta)
                if esperado is None:
                    self.assertTrue(not resultados or resultados[0][0] < 3)
                else:
                    self.assertTrue(resultados, "nenhuma orientação pontuou")
                    pontos, melhor = resultados[0]
                    self.assertGreaterEqual(pontos, 3)
                    self.assertEqual(melhor.id, esperado, f"obteve {melhor.id} com {pontos} pontos")


class TestDadosPessoais(unittest.TestCase):
    def test_bloqueia_cpf_telefone_e_email(self):
        for texto in ["meu cpf é 123.456.789-00", "liga 11 91234-5678", "ana@exemplo.com", "12345678"]:
            self.assertTrue(tem_dado_pessoal(texto), texto)

    def test_aceita_numeros_pequenos(self):
        for texto in ["desconto de 65%", "até 80 kWh", "preciso de 120 kwh", "1234567"]:
            self.assertFalse(tem_dado_pessoal(texto), texto)


class TestAtendimento(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        base = BaseConhecimento(JSON_REAL)
        self.assertTrue(base.carregar())
        self.assistente = Assistente("Teste", base, self.pasta.name)

    def tearDown(self):
        self.pasta.cleanup()

    def test_pergunta_encontrada_e_resolvida(self):
        saida = rodar(self.assistente.perguntar, ["Quem tem direito à tarifa social?", "s"])
        self.assertIn("Confiança da resposta: ALTA", saida)
        self.assertIn("Fonte: https://", saida)
        self.assertIn("verificado em", saida)
        self.assertIn("NÃO é um canal oficial", saida)
        a = self.assistente.historico[0]
        self.assertEqual((a["origem"], a["id_orientacao"], a["encontrou"], a["ajudou"], a["tentativas"]), ("pergunta", 1, True, True, 1))
        self.assertTrue(Path(self.pasta.name, "historico.json").exists())

    def test_mostra_ate_duas_alternativas(self):
        saida = rodar(self.assistente.perguntar, ["Qual o desconto de 65% até 80 kWh?", "s"])
        self.assertIn("Outras orientações que podem ajudar", saida)

    def test_nao_encontrou_sugere_categorias_e_conta_tentativas(self):
        saida = rodar(self.assistente.perguntar, ["quanto custa uma pizza", "mudei de casa", "s"])
        self.assertIn("Não encontrei", saida)
        self.assertIn("Categorias:", saida)
        a = self.assistente.historico[0]
        self.assertEqual((a["tentativas"], a["id_orientacao"], a["ajudou"]), (2, 12, True))

    def test_voltar_depois_de_nao_encontrar_registra_sem_solucao(self):
        rodar(self.assistente.perguntar, ["quanto custa uma pizza", "0"])
        a = self.assistente.historico[0]
        self.assertEqual((a["encontrou"], a["ajudou"], a["tentativas"], a["id_orientacao"]), (False, False, 1, None))

    def test_voltar_sem_perguntar_nao_registra(self):
        rodar(self.assistente.perguntar, ["0"])
        self.assertEqual(self.assistente.historico, [])

    def test_dado_pessoal_e_recusado_e_nao_registrado(self):
        saida = rodar(self.assistente.perguntar, ["meu cpf é 123.456.789-00", "0"])
        self.assertIn("não digite CPF, telefone ou e-mail", saida)
        self.assertEqual(self.assistente.historico, [])
        self.assertNotIn("123.456", Path(self.pasta.name, "historico.json").read_text(encoding="utf-8") if Path(self.pasta.name, "historico.json").exists() else "")

    def test_entradas_invalidas_nao_encerram(self):
        saida = rodar(self.assistente.perguntar, ["", "   ", "mudei de casa", "talvez", "", "s"])
        self.assertIn("Escreva sua dúvida", saida)
        self.assertIn("Responda com s (sim) ou n (não)", saida)
        self.assertEqual(len(self.assistente.historico), 1)

    def test_navegar_por_categorias(self):
        saida = rodar(self.assistente.navegar, ["1", "1", "s"])
        self.assertIn("Categorias:", saida)
        self.assertIn("0 - Voltar", saida)
        a = self.assistente.historico[0]
        self.assertEqual((a["origem"], a["id_orientacao"], a["ajudou"]), ("categoria", 1, True))

    def test_navegar_com_opcoes_invalidas(self):
        saida = rodar(self.assistente.navegar, ["abc", "", "99", "-1", "0"])
        self.assertIn("Digite apenas números", saida)
        self.assertIn("Escolha um número de 0 a 4", saida)
        self.assertEqual(self.assistente.historico, [])

    def test_navegar_nao_resolveu_e_voltou(self):
        rodar(self.assistente.navegar, ["1", "1", "n", "0", "0"])
        a = self.assistente.historico[0]
        self.assertEqual((a["origem"], a["encontrou"], a["ajudou"]), ("categoria", True, False))


class TestIndicadoresECsv(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        base = BaseConhecimento(JSON_REAL)
        base.carregar()
        self.assistente = Assistente("Teste", base, self.pasta.name)
        self.assistente.registrar("pergunta", "a", 1, True, True, 1, 10.0)
        self.assistente.registrar("pergunta", "b", 2, True, False, 2, 20.0)
        self.assistente.registrar("categoria", "c", None, False, False, 3, 30.0)

    def tearDown(self):
        self.pasta.cleanup()

    def test_indicadores(self):
        i = self.assistente.indicadores()
        self.assertEqual(i["total"], 3)
        self.assertEqual(i["resposta_encontrada_pct"], 66.7)
        self.assertEqual(i["taxa_de_acerto_pct"], 33.3)
        self.assertEqual(i["tempo_medio_s"], 10.0)
        self.assertEqual(i["tentativas_por_atendimento"], 2.0)
        self.assertIsNone(i["facilidade_media"])
        self.assertEqual(i["duvidas_sem_solucao"], ["b", "c"])

    def test_sem_atendimentos(self):
        self.assistente.historico.clear()
        self.assertEqual(self.assistente.indicadores(), {"total": 0})
        self.assertIn("Ainda não há atendimentos", rodar(self.assistente.exibir_indicadores, []))

    def test_exportar_csv(self):
        self.assertTrue(self.assistente.exportar_csv())
        with open(self.assistente.caminho_csv, encoding="utf-8-sig", newline="") as f:
            linhas = list(csv.DictReader(f))
        self.assertEqual(len(linhas), 3)
        self.assertEqual(linhas[0]["pergunta"], "a")
        self.assertIn("tempo_s", linhas[0])

    def test_nota_de_facilidade_ao_sair(self):
        self.assistente._inicio_da_sessao = len(self.assistente.historico)
        saida = rodar(self.assistente.encerrar, [])
        self.assertNotIn("quão fácil", saida)
        self.assistente._inicio_da_sessao = 0
        saida = rodar(self.assistente.encerrar, ["9", "x", "4"])
        self.assertIn("Escolha um número de 1 a 5", saida)
        self.assertEqual(self.assistente.historico[-1]["facilidade"], 4)
        self.assertEqual(self.assistente.indicadores()["facilidade_media"], 4.0)
        self.assertTrue(self.assistente.caminho_csv.exists())

    def test_historico_persiste_entre_execucoes(self):
        base = BaseConhecimento(JSON_REAL)
        base.carregar()
        novo = Assistente("Teste", base, self.pasta.name)
        self.assertEqual(len(novo.historico), 3)

    def test_historico_corrompido_nao_trava(self):
        Path(self.pasta.name, "historico.json").write_text("{{ quebrado", encoding="utf-8")
        base = BaseConhecimento(JSON_REAL)
        base.carregar()
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            novo = Assistente("Teste", base, self.pasta.name)
        self.assertEqual(novo.historico, [])
        self.assertIn("histórico estava inválido", saida.getvalue())
        self.assertTrue(Path(self.pasta.name, "historico.corrompido.json").exists())


if __name__ == "__main__":
    unittest.main()
