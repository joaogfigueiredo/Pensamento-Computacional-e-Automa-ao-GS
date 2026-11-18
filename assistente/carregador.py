"""Lê o servicos.json e transforma cada item em um objeto Servico."""

import json
from pathlib import Path

from .modelos import Servico

CAMPOS = (
    "id",
    "categoria",
    "titulo",
    "resumo",
    "passos",
    "documentos_necessarios",
    "palavras_chave",
    "fonte_nome",
    "fonte_url",
    "atualizado_em",
    "aviso",
)


def carregar_servicos(caminho: str | Path) -> tuple[Servico, ...]:
    """Lê o arquivo JSON e devolve uma tupla de Servico.

    Lança ValueError se algum item estiver sem campo obrigatório,
    para que um erro no arquivo apareça logo na inicialização.
    """
    with open(caminho, encoding="utf-8") as arquivo:
        itens = json.load(arquivo)

    servicos = []
    for item in itens:
        faltando = [campo for campo in CAMPOS if campo not in item]
        if faltando:
            raise ValueError(f"Item {item.get('id', '?')} sem campos: {faltando}")

        # JSON devolve listas; convertemos para tupla, que não pode ser alterada.
        valores = {
            campo: tuple(item[campo]) if isinstance(item[campo], list) else item[campo]
            for campo in CAMPOS
        }
        servicos.append(Servico(**valores))

    return tuple(servicos)
