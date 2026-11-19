# Citizen Assist AI: assistente de orientação sobre a Tarifa Social de Energia

Global Solution 2026.2 (FIAP, desafio CitizenTech). Disciplina: Pensamento Computacional e Automação com Python.

**Integrantes**
- João Guilherme Figueiredo, RM 572697
- Ryan Luther Roque, RM 572993

## Público e problema

**Público:** famílias de baixa renda que recebem ou podem ter direito à Tarifa Social de Energia Elétrica.

**Problema:** o desconto na conta de luz mudou em 2025 (Lei 15.235/2025 alterou a Lei 12.212/2010). Muita informação antiga, como os descontos de 65%, 40% e 10%, continua circulando, e as regras estão espalhadas em textos de lei. O assistente responde em linguagem simples, mostra a fonte e a data em que a equipe conferiu a informação, e deixa claro que **não é um canal oficial**.

## ODS relacionados

- **ODS 7:** energia limpa e acessível (acesso a energia a preço justo).
- **ODS 1:** erradicação da pobreza (alívio do custo da energia para famílias de baixa renda).
- **ODS 10:** redução das desigualdades.
- **ODS 16:** instituições eficazes e acesso à informação pública.

## Como executar

Requer Python 3.10 ou superior. Não usa bibliotecas externas e não tem interface gráfica.

```bash
python main.py                 # abre o menu no terminal
python -m unittest discover -s tests    # 34 testes automatizados
```

Menu: fazer uma pergunta em texto livre, navegar por categorias, ver indicadores, exportar o CSV e sair. Em todas as telas, `0` volta.

## Estrutura

```
├── README.md
├── main.py                  menu e ponto de entrada
├── orientacao.py            classe Orientacao (um registro do JSON)
├── base_conhecimento.py     classe BaseConhecimento (JSON, categorias e busca com pontuação)
├── assistente.py            classe Assistente (atendimento, histórico, indicadores, CSV)
├── tests/test_assistente.py testes automatizados
└── data/
    ├── base_conhecimento.json   15 orientações, 4 categorias
    ├── historico.json           um dicionário por atendimento
    └── atendimentos.csv         atendimentos exportados com csv.DictWriter
```

As classes se encaixam por composição: `Assistente` tem uma `BaseConhecimento`, que tem uma lista de objetos `Orientacao`.

## Base de conhecimento

`data/base_conhecimento.json` é uma lista de dicionários, um por orientação, com os campos `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`. São **15 orientações** em **4 categorias** (Direitos; Desconto na conta; Cadastro e documentos; Atendimento e serviços), cada uma com 5 ou mais palavras-chave. O texto foi escrito a partir das duas leis citadas em "Fontes" e cada resposta traz o artigo de origem. Se o arquivo faltar ou estiver corrompido, o programa avisa o motivo e fecha sem travar.

## Regra de pontuação

A pergunta e as palavras-chave são normalizadas (minúsculas, sem acentos e sem pontuação) e comparadas assim:

| Regra | Pontos |
|---|---|
| Cada palavra-chave da orientação que aparece na pergunta | +3 |
| Cada palavra da pergunta com 4 letras ou mais que aparece no título | +1 |

| Melhor pontuação | Resultado |
|---|---|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação, e o assistente mostra a melhor orientação e até duas alternativas. Em empate, vale o menor `id`. Os pesos e limites são os do enunciado, sem ajustes.

Exemplo: em "Como faço o cartão do SUS?" (exemplo do enunciado) a orientação do Cartão SUS recebe +3 por `cartao do sus`, +3 por `sus` e +1 porque `cartao` está no título: 7 pontos, confiança ALTA. Isso está coberto por um teste automatizado.

## Entradas inválidas, dados pessoais e avisos

- Opção fora da faixa, letras, resposta vazia ou `s/n` inválido são recusados e o programa continua.
- Pergunta com **8 ou mais dígitos** ou com `@` é recusada e **não é registrada**: o assistente nunca pede nome, CPF, telefone ou e-mail.
- Toda resposta mostra a fonte, a data de verificação e o aviso de que o assistente não é canal oficial e não confirma direitos.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com `data`, `origem` (pergunta ou categoria), `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas`, `tempo_s` e `facilidade`. O tempo é medido com `time.time()` do início ao fim do atendimento. Ao sair, o assistente pede uma nota de facilidade de 1 a 5, guardada no último atendimento da sessão, e exporta `data/atendimentos.csv`.

Indicadores exibidos no menu (opção 3):

| Indicador | Como é calculado |
|---|---|
| Resposta encontrada (%) | atendimentos em que alguma orientação teve confiança suficiente, sobre o total |
| Taxa de acerto (%) | atendimentos em que a pessoa disse que a orientação ajudou, sobre o total |
| Tempo médio para encontrar | média do tempo dos atendimentos em que a orientação ajudou |
| Tentativas por atendimento | média de perguntas feitas (ou orientações abertas) por atendimento |
| Facilidade de uso (1 a 5) | média das notas dadas ao sair |
| Dúvidas sem solução | perguntas que não foram encontradas ou não ajudaram |

## Teste com usuários

O teste com pessoas de fora da equipe **não foi aplicado** nesta entrega. O assistente já está preparado para isso: cada atendimento é gravado em `data/historico.json` com o tempo, as tentativas e a nota de facilidade, o menu mostra os indicadores (opção 3) e o CSV é exportado ao sair. O próximo passo seria aplicar o programa a pelo menos 3 pessoas (10 atendimentos ou mais), registrar os indicadores aqui e fazer uma melhoria a partir das dúvidas sem solução.

## Integração com outras disciplinas

Não há integração de código nesta entrega. O conteúdo trata do mesmo tema (Tarifa Social de Energia) das demais disciplinas da Global Solution.

## Fontes consultadas

- Lei 12.212/2010, texto original: https://legis.senado.leg.br/norma/575854/publicacao/15749932
- Lei 15.235/2025, que alterou a anterior: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15235.htm

Data de verificação registrada na base: 2026-11-17.

## Limitações

- A busca é por palavras-chave e pontos: perguntas com vocabulário muito diferente do cadastrado podem não ser encontradas (por isso existe a navegação por categorias).
- A base tem 15 orientações, baseadas só em duas leis. Resoluções da ANEEL e regras de cada distribuidora não estão incluídas.
- O assistente orienta de forma introdutória: não confirma direitos nem a concessão do benefício, e as informações devem ser confirmadas na distribuidora de energia.
- O tempo medido inclui o tempo de digitação e de leitura da pessoa.

## Vídeo técnico

Link: https://youtu.be/X-Z08RFJbl8
