"""Citizen Assist AI: assistente de orientação sobre a Tarifa Social de Energia Elétrica.

Execução: python main.py
"""
from pathlib import Path

from assistente import Assistente, EncerrarPrograma, ler_inteiro
from base_conhecimento import BaseConhecimento

PASTA = Path(__file__).resolve().parent

MENU = """
=== Citizen Assist AI ===
1 - Fazer uma pergunta
2 - Navegar por categorias
3 - Ver indicadores
4 - Exportar atendimentos para CSV
0 - Sair"""


def main():
    print("Citizen Assist AI - orientações sobre a Tarifa Social de Energia Elétrica")
    print("Aviso: este assistente NÃO é um canal oficial. Não digite CPF, telefone ou e-mail.")

    base = BaseConhecimento(PASTA / "data" / "base_conhecimento.json")
    if not base.carregar():
        print(f"\nNão foi possível carregar a base de conhecimento: {base.erro}.")
        print("Corrija o arquivo data/base_conhecimento.json e execute de novo.")
        return

    assistente = Assistente("Citizen Assist AI", base, PASTA / "data")
    try:
        while True:
            print(MENU)
            opcao = ler_inteiro("Escolha: ", 0, 4)
            if opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.exibir_indicadores()
            elif opcao == 4:
                if assistente.exportar_csv():
                    print(f"Atendimentos exportados para {assistente.caminho_csv.name}.")
            else:
                assistente.encerrar()
                return
    except (EncerrarPrograma, KeyboardInterrupt):
        print("\nEncerrando.")
        assistente.exportar_csv()


if __name__ == "__main__":
    main()
