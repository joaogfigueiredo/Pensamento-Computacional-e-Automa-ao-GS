"""Modelos de dados: cada serviço e cada resposta são objetos imutáveis.

dataclass(frozen=True) cria uma classe com __init__ automático e
impede que os campos sejam alterados depois de criados.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Servico:
    """Uma orientação do cadastro (uma linha do servicos.json)."""

    id: str
    categoria: str
    titulo: str
    resumo: str
    passos: tuple[str, ...]
    documentos_necessarios: tuple[str, ...]
    palavras_chave: tuple[str, ...]
    fonte_nome: str
    fonte_url: str
    atualizado_em: str
    aviso: str


@dataclass(frozen=True)
class Resposta:
    """O que o assistente devolve para uma pergunta."""

    texto: str
    servico_id: str | None
    confianca: float
    fonte: str
    aviso: str
    respondeu: bool
