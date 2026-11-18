"""Busca por regras: encontra o serviço cujas palavras-chave aparecem na pergunta.

Como funciona:
1. Cada palavra-chave é normalizada e guardada em um dicionário:
   palavra -> conjunto de ids de serviços que a usam.
2. Para uma pergunta, contamos quantas palavras-chave de cada serviço aparecem nela.
3. A confiança é: acertos / min(total_de_palavras_do_serviço, 3), limitada a 1.0.
   Assim, bater 2 palavras já dá confiança boa, sem exigir todas.
4. Se a confiança ficar abaixo de LIMIAR, o assistente não responde com certeza.
"""

from collections import defaultdict

from .modelos import Servico
from .validacao import normalizar

LIMIAR = 0.5
ACERTOS_PARA_CONFIANCA_TOTAL = 3


class IndiceRegras:
    def __init__(self, servicos: tuple[Servico, ...]) -> None:
        self._servicos = {s.id: s for s in servicos}
        # defaultdict(set): se a chave não existe, cria um conjunto vazio automaticamente.
        self._indice: dict[str, set[str]] = defaultdict(set)
        for servico in servicos:
            for palavra in servico.palavras_chave:
                self._indice[normalizar(palavra)].add(servico.id)

    def obter(self, servico_id: str) -> Servico:
        return self._servicos[servico_id]

    def buscar(self, pergunta: str) -> tuple[str, float] | None:
        """Retorna (id_do_servico, confianca) ou None se nada bateu."""
        # Espaços nas bordas evitam casar "rendas" quando a regra é "renda".
        texto = f" {normalizar(pergunta)} "

        acertos: dict[str, int] = defaultdict(int)
        for expressao, ids in self._indice.items():
            if f" {expressao} " in texto:
                for servico_id in ids:
                    acertos[servico_id] += 1

        if not acertos:
            return None

        melhor_id, quantidade = max(acertos.items(), key=lambda par: par[1])
        total_palavras = len(self._servicos[melhor_id].palavras_chave)
        confianca = min(1.0, quantidade / min(total_palavras, ACERTOS_PARA_CONFIANCA_TOTAL))
        return melhor_id, round(confianca, 2)
