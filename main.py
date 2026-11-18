"""Ponto de entrada: menu no terminal para perguntar e ver indicadores.

Rode com:  python main.py
"""

import time
from pathlib import Path

from assistente import Assistente, carregar_servicos
from assistente import indicadores

BASE = Path(__file__).resolve().parent
ARQ_SERVICOS = BASE / "dados" / "servicos.json"
ARQ_LOG = BASE / "logs" / "consultas.csv"

MENU = """
=== Citizen Assist AI ===
1 - Fazer uma pergunta
2 - Ver indicadores
0 - Sair
"""


def fazer_pergunta(assistente: Assistente) -> None:
    pergunta = input("Sua pergunta: ")

    inicio = time.perf_counter()
    resposta = assistente.responder(pergunta)
    tempo_ms = round((time.perf_counter() - inicio) * 1000, 3)

    indicadores.registrar(ARQ_LOG, pergunta, resposta, tempo_ms)

    print()
    if resposta.respondeu:
        print(resposta.texto)
        print(f"Fonte: {resposta.fonte}")
    else:
        print(resposta.texto)
    print(f"Confiança: {resposta.confianca:.0%}")
    print(f"Aviso: {resposta.aviso}")


def mostrar_indicadores() -> None:
    dados = indicadores.resumir(ARQ_LOG)
    print()
    print(f"Consultas registradas: {dados['total']}")
    print(f"Taxa de resposta:      {dados['taxa_resposta']:.0%}")
    print(f"Confiança média:       {dados['confianca_media']:.0%}")
    print(f"Tempo médio:           {dados['tempo_medio_ms']} ms")


def main() -> None:
    assistente = Assistente(carregar_servicos(ARQ_SERVICOS))
    while True:
        print(MENU)
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            fazer_pergunta(assistente)
        elif opcao == "2":
            mostrar_indicadores()
        elif opcao == "0":
            print("Até logo.")
            break
        else:
            print("Opção inválida. Digite 0, 1 ou 2.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado.")
