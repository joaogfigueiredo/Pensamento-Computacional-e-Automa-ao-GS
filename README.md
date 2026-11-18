# Pensamento Computacional e Automação: Citizen Assist AI (módulo Python)

"Cérebro" do assistente. Responde perguntas sobre a Tarifa Social de Energia usando
regras, mostra a fonte e o aviso, trata entradas inválidas, protege dados pessoais e
grava indicadores em CSV.

## Como rodar

```bash
python main.py          # menu no terminal
python -m unittest      # testes automatizados
```

Não é preciso instalar nada: usa só a biblioteca padrão do Python 3.10 ou superior.

## Estrutura

```
Pensamento Computacional e Automação/
├── main.py                  menu no terminal (ponto de entrada)
├── assistente/              o pacote com a lógica
│   ├── __init__.py          o que o pacote expõe
│   ├── modelos.py           classes Servico e Resposta
│   ├── carregador.py        lê o servicos.json
│   ├── validacao.py         normaliza texto e recusa entradas inválidas
│   ├── privacidade.py       apaga CPF, e-mail e CEP
│   ├── busca.py             índice de palavras-chave e cálculo de confiança
│   ├── assistente.py        classe Assistente: junta tudo e monta a resposta
│   └── indicadores.py       grava o CSV e calcula médias
├── dados/
│   └── servicos.json        15 serviços, escritos a partir da Lei 12.212/2010 e da Lei 15.235/2025
├── logs/
│   └── consultas.csv        criado automaticamente a cada pergunta
├── tests/
│   └── test_assistente.py   testes automatizados
└── testes_usuarios/
    └── ROTEIRO.md           como aplicar os testes com pessoas e registrar os resultados
```

## Como a resposta é escolhida

1. A pergunta é validada (vazia, longa demais ou só símbolos são recusadas).
2. As palavras-chave de cada serviço são procuradas no texto normalizado.
3. A confiança é `acertos / min(palavras_do_serviço, 3)`, limitada a 1.0.
4. Se a confiança for menor que `0.5`, o assistente diz que não tem certeza.

## Proteção de dados

Antes de gravar uma pergunta no log, CPF, e-mail e CEP são substituídos por marcadores.
O assistente nunca pede dados pessoais.

## Status

- [x] Base de 15 serviços, cada um com fonte oficial (as duas leis); o Ryan deve conferir os textos contra as leis
- [ ] Testes com usuários reais (5+ pessoas): ver `testes_usuarios/ROTEIRO.md`
- [ ] Vídeo técnico (os dois integrantes explicam o código)
