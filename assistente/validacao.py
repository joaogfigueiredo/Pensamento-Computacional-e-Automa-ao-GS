"""Tratamento de entradas: normaliza o texto e recusa entradas inválidas."""

import re
import unicodedata

TAMANHO_MAXIMO = 300


def normalizar(texto: str) -> str:
    """Deixa o texto em minúsculas, sem acento e com espaços simples.

    Exemplo: '  Tenho DIREITO à  Tarifa ' -> 'tenho direito a tarifa'
    """
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    # Pontuação vira espaço, para "levar?" virar "levar".
    sem_pontuacao = re.sub(r"[^\w\s]", " ", sem_acento.lower())
    return re.sub(r"\s+", " ", sem_pontuacao).strip()


def validar_pergunta(texto: object) -> tuple[bool, str]:
    """Retorna (True, "") se a pergunta é aceitável, ou (False, motivo)."""
    if not isinstance(texto, str):
        return False, "Entrada inválida: envie um texto."

    limpo = texto.strip()
    if not limpo:
        return False, "Digite uma pergunta."
    if len(limpo) > TAMANHO_MAXIMO:
        return False, f"Pergunta muito longa (máximo de {TAMANHO_MAXIMO} caracteres)."
    if not re.search(r"[a-zA-ZÀ-ÿ]", limpo):
        return False, "A pergunta precisa conter palavras, não só símbolos ou números."

    return True, ""
