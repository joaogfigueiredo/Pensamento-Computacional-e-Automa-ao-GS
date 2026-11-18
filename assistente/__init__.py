"""Pacote do assistente Citizen Assist AI (módulo de regras)."""

from .modelos import Servico, Resposta
from .carregador import carregar_servicos
from .assistente import Assistente

__all__ = ["Servico", "Resposta", "carregar_servicos", "Assistente"]
