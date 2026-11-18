"""Classe Orientacao: uma informação da base de conhecimento (um registro do JSON)."""

AVISO = "Aviso: este assistente NÃO é um canal oficial. Ele não confirma direitos nem a concessão de benefícios."

CAMPOS_OBRIGATORIOS = ["id", "categoria", "titulo", "palavras_chave", "resposta", "documentos", "onde", "fonte", "verificado_em"]


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria a orientação a partir de um dicionário do JSON, recusando registros incompletos."""
        if not isinstance(dados, dict):
            raise ValueError("cada orientação deve ser um objeto JSON")
        faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in dados]
        if faltando:
            raise ValueError(f"campos ausentes: {', '.join(faltando)}")
        if not isinstance(dados["id"], int):
            raise ValueError("o campo id deve ser um número inteiro")
        if not isinstance(dados["palavras_chave"], list) or not isinstance(dados["documentos"], list):
            raise ValueError("palavras_chave e documentos devem ser listas")
        return cls(**{campo: dados[campo] for campo in CAMPOS_OBRIGATORIOS})

    def exibir(self):
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("Documentos necessários: nenhum documento específico indicado na lei")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(AVISO)
