"""Proteção de dados: apaga CPF, e-mail e CEP antes de qualquer registro."""

import re

# Lista de pares (padrão, texto que substitui). Cada padrão é compilado uma vez.
PADROES = (
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF removido]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[e-mail removido]"),
    (re.compile(r"\b\d{5}-?\d{3}\b"), "[CEP removido]"),
)


def mascarar(texto: str) -> str:
    """Substitui dados pessoais por marcadores. Ex.: 'meu cpf 123.456.789-09'."""
    for padrao, substituto in PADROES:
        texto = padrao.sub(substituto, texto)
    return texto
