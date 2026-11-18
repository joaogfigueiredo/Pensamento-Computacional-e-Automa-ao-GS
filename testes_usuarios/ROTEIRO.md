# Roteiro dos testes com usuários

**Objetivo:** medir, com pessoas reais, os 3 indicadores do case: **acerto das orientações**, **tempo para encontrar a informação** e **facilidade de uso**. Os resultados alimentam o Pensamento Computacional (indicadores) e a Modelagem Linear (seção 9 do notebook).

**Quantas pessoas:** de 5 a 8 já ajudam; de 15 a 20 deixam a análise estatística bem melhor. Escolha pessoas fora de TI, que não viram o sistema.

## Antes de começar

1. Apague o arquivo `logs/consultas.csv` (para o log ter só os testes reais).
2. Tenha um cronômetro (celular) e uma folha ou planilha para anotar.
3. Abra o assistente: `python main.py` (pasta `Pensamento Computacional e Automação`).
4. Explique: "É um trabalho acadêmico. Vou pedir 3 tarefas. O teste avalia o sistema, não você. Pode desistir quando quiser."
5. **Não anote nome, CPF, endereço ou qualquer dado pessoal.** Use P1, P2, P3...

## As 3 tarefas

Peça para a pessoa usar a opção 1 (fazer uma pergunta) com as palavras dela. Não dê dicas de como perguntar.

| Tarefa | O que pedir | Resposta certa (serviço) |
|---|---|---|
| 1 | "Descubra se uma família inscrita no CadÚnico, com renda de até meio salário mínimo por pessoa, tem direito à Tarifa Social." | S001: tem direito (art. 2º da Lei 12.212/2010) |
| 2 | "Descubra quanto é o desconto na conta para quem consome 80 kWh por mês." | S003: 100% até 80 kWh (Lei 15.235/2025) |
| 3 | "Descubra o que uma pessoa que recebe a Tarifa Social deve fazer ao mudar de casa." | S008: informar o novo endereço à distribuidora, sob pena de perder o benefício |

## O que anotar, por tarefa

- **tempo_s:** segundos desde a pergunta da tarefa até a pessoa dizer a resposta (use o cronômetro; pare em 180 s se não achou).
- **acertou:** 1 se a pessoa disse a informação certa com as próprias palavras; 0 se não achou ou errou. Confira com a tabela acima.
- **facilidade_1a5** (pergunte depois de cada tarefa): "De 1 (muito difícil) a 5 (muito fácil), como foi achar isso?"
- **comentario:** o que confundiu ou faltou, em poucas palavras, sem dados pessoais.

## Planilha de registro

Salve como CSV em `Modelagem Linear/dados/testes_usuarios.csv` (modelo em `testes_usuarios_MODELO.csv`):

```
participante,tarefa,acertou,tempo_s,facilidade_1a5,comentario
P1,1,1,34,4,"achei o texto claro"
P1,2,1,28,4,""
P1,3,0,95,2,"não entendi a palavra distribuidora"
```

Cada pessoa gera 3 linhas. Com 5 pessoas são 15 linhas; com 15, são 45.

## Depois dos testes

1. No assistente, escolha a opção 2 (**Ver indicadores**) e anote: total de consultas, taxa de resposta, confiança média e tempo médio de resposta do sistema.
2. Copie o `testes_usuarios.csv` para a pasta de Modelagem Linear e rode `python scripts/gerar_notebook.py` lá: a seção 9 é preenchida.
3. Escreva no README do Pensamento Computacional um resumo de 5 linhas: taxa de acerto, tempo médio, facilidade média, o que confundiu e qual ajuste foi feito (por exemplo, incluir uma palavra-chave que as pessoas usaram e o sistema não reconheceu).

## Cuidado com a leitura dos resultados

Com poucas pessoas, os números têm margem de erro grande. Apresente a taxa de acerto **com o intervalo de confiança** (o notebook calcula) e diga que a amostra é pequena.
