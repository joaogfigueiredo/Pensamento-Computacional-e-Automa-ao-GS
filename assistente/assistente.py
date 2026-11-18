"""Classe Assistente: junta validação, busca e montagem da resposta."""

from .busca import IndiceRegras, LIMIAR
from .modelos import Resposta, Servico
from .validacao import validar_pergunta

AVISO_GERAL = "Este assistente não é canal oficial. Confirme no órgão responsável."


class Assistente:
    """Recebe perguntas e devolve respostas com fonte e aviso.

    A classe guarda o índice montado uma única vez, no construtor,
    e reutiliza em todas as perguntas.
    """

    def __init__(self, servicos: tuple[Servico, ...]) -> None:
        self._indice = IndiceRegras(servicos)

    def responder(self, pergunta: str) -> Resposta:
        valido, motivo = validar_pergunta(pergunta)
        if not valido:
            return Resposta(motivo, None, 0.0, "", AVISO_GERAL, False)

        encontrado = self._indice.buscar(pergunta)
        if encontrado is None:
            texto = "Não encontrei informação sobre isso. Procure o canal oficial."
            return Resposta(texto, None, 0.0, "", AVISO_GERAL, False)

        servico_id, confianca = encontrado
        if confianca < LIMIAR:
            texto = "Não tenho certeza da resposta. Procure o canal oficial."
            return Resposta(texto, None, confianca, "", AVISO_GERAL, False)

        servico = self._indice.obter(servico_id)
        texto = f"{servico.resumo}\nDocumentos: {', '.join(servico.documentos_necessarios)}."
        fonte = f"{servico.fonte_nome}, atualizado em {servico.atualizado_em}: {servico.fonte_url}"
        return Resposta(texto, servico_id, confianca, fonte, servico.aviso, True)
