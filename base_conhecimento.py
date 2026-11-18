"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação por pontuação."""
import json
from pathlib import Path

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
MIN_LETRAS_TITULO = 4
CONFIANCA_ALTA = 6
CONFIANCA_MEDIA = 3


def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def nivel_confianca(pontos):
    if pontos >= CONFIANCA_ALTA:
        return "ALTA"
    if pontos >= CONFIANCA_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []
        self.erro = ""

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Devolve False (sem travar) se o arquivo faltar ou estiver inválido."""
        self.orientacoes = []
        try:
            texto = self.caminho.read_text(encoding="utf-8-sig")
        except FileNotFoundError:
            self.erro = f"arquivo não encontrado: {self.caminho}"
            return False
        except (OSError, UnicodeDecodeError) as problema:
            self.erro = f"não foi possível ler o arquivo ({problema})"
            return False
        try:
            dados = json.loads(texto)
        except json.JSONDecodeError as problema:
            self.erro = f"o JSON está corrompido (linha {problema.lineno}, coluna {problema.colno})"
            return False
        if not isinstance(dados, list) or not dados:
            self.erro = "o JSON deve ser uma lista com pelo menos uma orientação"
            return False
        try:
            orientacoes = [Orientacao.de_dicionario(item) for item in dados]
        except ValueError as problema:
            self.erro = f"registro inválido: {problema}"
            return False
        ids = [o.id for o in orientacoes]
        if len(ids) != len(set(ids)):
            self.erro = "há ids repetidos na base"
            return False
        self.orientacoes = orientacoes
        return True

    def categorias(self):
        return list(dict.fromkeys(o.categoria for o in self.orientacoes))

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """+3 por palavra-chave presente na pergunta; +1 por palavra (4+ letras) da pergunta que está no título."""
        texto = normalizar(pergunta)
        pontos = 0
        for palavra_chave in {normalizar(p) for p in orientacao.palavras_chave}:
            if palavra_chave in texto:
                pontos += PONTOS_PALAVRA_CHAVE
        palavras_titulo = normalizar(orientacao.titulo).split()
        for palavra in set(texto.split()):
            if len(palavra) >= MIN_LETRAS_TITULO and palavra in palavras_titulo:
                pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor pontuação (só quem pontuou)."""
        resultados = [(self.pontuar(pergunta, o), o) for o in self.orientacoes]
        resultados = [r for r in resultados if r[0] > 0]
        resultados.sort(key=lambda r: (-r[0], r[1].id))
        return resultados
