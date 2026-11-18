"""Classe Assistente: conversa com o cidadão, guarda o histórico e calcula os indicadores."""
import csv
import json
import time
from datetime import datetime
from pathlib import Path

from base_conhecimento import CONFIANCA_MEDIA, nivel_confianca

PASTA_DADOS = Path(__file__).resolve().parent / "data"
CAMPOS_ATENDIMENTO = ["data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou", "tentativas", "tempo_s", "facilidade"]


class EncerrarPrograma(Exception):
    """Sinaliza que a entrada de dados acabou (Ctrl+Z/Ctrl+D) e o programa deve fechar com calma."""


def ler(mensagem):
    try:
        return input(mensagem).strip()
    except EOFError:
        raise EncerrarPrograma


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        texto = ler(mensagem)
        if not texto:
            print("Digite uma opção.")
            continue
        try:
            numero = int(texto)
        except ValueError:
            print("Digite apenas números.")
            continue
        if numero < minimo or numero > maximo:
            print(f"Escolha um número de {minimo} a {maximo}.")
            continue
        return numero


def ler_sim_nao(mensagem):
    while True:
        texto = ler(mensagem).lower()
        if texto in ("s", "sim"):
            return True
        if texto in ("n", "nao", "não"):
            return False
        print("Responda com s (sim) ou n (não).")


def tem_dado_pessoal(texto):
    """CPF, telefone ou e-mail: 8 ou mais dígitos, ou o sinal @."""
    return "@" in texto or sum(c.isdigit() for c in texto) >= 8


def media(valores):
    return round(sum(valores) / len(valores), 1) if valores else None


class Assistente:
    def __init__(self, nome, base, pasta_dados=PASTA_DADOS):
        self.nome = nome
        self.base = base
        self.pasta_dados = Path(pasta_dados)
        self.caminho_historico = self.pasta_dados / "historico.json"
        self.caminho_csv = self.pasta_dados / "atendimentos.csv"
        self.historico = self._carregar_historico()
        self._inicio_da_sessao = len(self.historico)

    def _carregar_historico(self):
        try:
            conteudo = json.loads(self.caminho_historico.read_text(encoding="utf-8-sig"))
            if isinstance(conteudo, list):
                return conteudo
        except FileNotFoundError:
            return []
        except (OSError, ValueError):
            pass
        print("Aviso: o histórico estava inválido e foi guardado como historico.corrompido.json; começando um novo.")
        try:
            self.caminho_historico.replace(self.caminho_historico.with_name("historico.corrompido.json"))
        except OSError:
            pass
        return []

    def _salvar_historico(self):
        try:
            self.pasta_dados.mkdir(parents=True, exist_ok=True)
            self.caminho_historico.write_text(json.dumps(self.historico, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as problema:
            print(f"Aviso: não consegui salvar o histórico ({problema}).")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo_s):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_s": tempo_s,
            "facilidade": None,
        }
        self.historico.append(atendimento)
        self._salvar_historico()
        return atendimento

    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        ultima = {"pergunta": "", "id": None, "encontrou": False}
        while True:
            texto = ler("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                break
            if not texto:
                print("Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue
            tentativas += 1
            ultima = {"pergunta": texto, "id": None, "encontrou": False}
            resultados = self.base.buscar(texto)
            if not resultados or resultados[0][0] < CONFIANCA_MEDIA:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (por exemplo: desconto, documentos, mudança de endereço) ou use a navegação por categorias.")
                print("Categorias: " + ", ".join(self.base.categorias()))
                continue
            pontos, melhor = resultados[0]
            ultima.update(id=melhor.id, encontrou=True)
            print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()
            alternativas = resultados[1:3]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for pontos_alt, alternativa in alternativas:
                    print(f"  - {alternativa.titulo} ({pontos_alt} pontos)")
            if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                self.registrar("pergunta", texto, melhor.id, True, True, tentativas, round(time.time() - inicio, 1))
                return
        if tentativas:
            self.registrar("pergunta", ultima["pergunta"], ultima["id"], ultima["encontrou"], False, tentativas, round(time.time() - inicio, 1))

    def navegar(self):
        categorias = self.base.categorias()
        inicio = time.time()
        tentativas = 0
        ultima = None
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, 1):
                print(f"  {numero} - {categoria}")
            print("  0 - Voltar")
            escolha = ler_inteiro("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                break
            categoria = categorias[escolha - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print(f"\n{categoria}:")
                for numero, orientacao in enumerate(orientacoes, 1):
                    print(f"  {numero} - {orientacao.titulo}")
                print("  0 - Voltar")
                numero = ler_inteiro("Escolha uma orientação: ", 0, len(orientacoes))
                if numero == 0:
                    break
                ultima = orientacoes[numero - 1]
                tentativas += 1
                ultima.exibir()
                if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    self.registrar("categoria", ultima.titulo, ultima.id, True, True, tentativas, round(time.time() - inicio, 1))
                    return
        if tentativas:
            self.registrar("categoria", ultima.titulo, ultima.id, True, False, tentativas, round(time.time() - inicio, 1))

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            return {"total": 0}
        encontrados = [a for a in self.historico if a["encontrou"]]
        ajudaram = [a for a in self.historico if a["ajudou"]]
        return {
            "total": total,
            "resposta_encontrada_pct": round(100 * len(encontrados) / total, 1),
            "taxa_de_acerto_pct": round(100 * len(ajudaram) / total, 1),
            "tempo_medio_s": media([a["tempo_s"] for a in ajudaram]),
            "tentativas_por_atendimento": media([a["tentativas"] for a in self.historico]),
            "facilidade_media": media([a["facilidade"] for a in self.historico if a.get("facilidade") is not None]),
            "duvidas_sem_solucao": list(dict.fromkeys(a["pergunta"] for a in self.historico if not a["ajudou"])),
        }

    def exibir_indicadores(self):
        dados = self.indicadores()
        print("\n=== Indicadores ===")
        if dados["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return
        sem_dado = "sem dados"
        print(f"Atendimentos registrados:        {dados['total']}")
        print(f"Resposta encontrada:             {dados['resposta_encontrada_pct']}%")
        print(f"Taxa de acerto (ajudou):         {dados['taxa_de_acerto_pct']}%")
        tempo = dados["tempo_medio_s"]
        print(f"Tempo médio para encontrar:      {sem_dado if tempo is None else str(tempo) + ' s'}")
        print(f"Tentativas por atendimento:      {dados['tentativas_por_atendimento']}")
        facilidade = dados["facilidade_media"]
        print(f"Facilidade de uso (1 a 5):       {sem_dado if facilidade is None else facilidade}")
        print("Dúvidas sem solução:")
        if dados["duvidas_sem_solucao"]:
            for duvida in dados["duvidas_sem_solucao"]:
                print(f"  - {duvida}")
        else:
            print("  nenhuma")

    def exportar_csv(self):
        try:
            self.pasta_dados.mkdir(parents=True, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_ATENDIMENTO, extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
        except OSError as problema:
            print(f"Não consegui exportar o CSV ({problema}). Feche o arquivo se ele estiver aberto em outro programa.")
            return False
        return True

    def pedir_nota_de_facilidade(self):
        """Ao sair: uma nota de 1 a 5, guardada no último atendimento da sessão."""
        if len(self.historico) <= self._inicio_da_sessao:
            return
        nota = ler_inteiro("\nDe 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
        self.historico[-1]["facilidade"] = nota
        self._salvar_historico()

    def encerrar(self):
        self.pedir_nota_de_facilidade()
        if self.exportar_csv():
            print(f"Atendimentos exportados para {self.caminho_csv.name}.")
        print("Até logo.")
