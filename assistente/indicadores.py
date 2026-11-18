"""Indicadores: grava cada consulta em CSV e calcula médias para análise."""

import csv
from datetime import datetime
from pathlib import Path

from .modelos import Resposta
from .privacidade import mascarar

COLUNAS = ("data_hora", "pergunta_mascarada", "servico_id", "confianca", "respondeu", "tempo_ms")
SEPARADOR = ";"


def registrar(caminho: str | Path, pergunta: str, resposta: Resposta, tempo_ms: float) -> None:
    """Acrescenta uma linha no CSV. Cria o arquivo e o cabeçalho na primeira vez."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    arquivo_novo = not caminho.exists()

    with open(caminho, "a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo, delimiter=SEPARADOR)
        if arquivo_novo:
            escritor.writerow(COLUNAS)
        escritor.writerow((
            datetime.now().isoformat(timespec="seconds"),
            mascarar(pergunta)[:120],  # nunca grava a pergunta original
            resposta.servico_id or "",
            resposta.confianca,
            int(resposta.respondeu),
            tempo_ms,
        ))


def resumir(caminho: str | Path) -> dict[str, float]:
    """Lê o CSV e calcula: total, taxa de resposta, confiança média e tempo médio."""
    caminho = Path(caminho)
    vazio = {"total": 0, "taxa_resposta": 0.0, "confianca_media": 0.0, "tempo_medio_ms": 0.0}
    if not caminho.exists():
        return vazio

    with open(caminho, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=SEPARADOR))
    if not linhas:
        return vazio

    total = len(linhas)
    respondidas = sum(int(linha["respondeu"]) for linha in linhas)
    return {
        "total": total,
        "taxa_resposta": round(respondidas / total, 2),
        "confianca_media": round(sum(float(l["confianca"]) for l in linhas) / total, 2),
        "tempo_medio_ms": round(sum(float(l["tempo_ms"]) for l in linhas) / total, 2),
    }
