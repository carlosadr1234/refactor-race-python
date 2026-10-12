# Métricas: REFactor Race Python

| Indicador | Antes | Depois |
|---|---|---|
| Testes passando | 4 de 4 | 66 de 66 |
| Quantidade de testes | 4 | 66 |
| Cobertura de testes | 83% | 100% |
| Complexidade da função principal | E (34) | A (1) |
| Complexidade média | E (34.0) | A (2.9) |
| Índice de manutenibilidade | A (51.69) | A (47.03) |
| Problemas identificados pelo Ruff | 4 | 0 |

Todos os valores foram medidos com as ferramentas do enunciado
(pytest, pytest-cov, radon e ruff) sobre `src/legacy_checkout.py`.

## Comparação com a versão original

`python tools/differential_check.py` roda 60000 casos aleatórios (semente
fixa) e compara resultado **e** texto impresso do código atual com a versão
original lida do histórico do Git. Resultado: 60000 casos idênticos.

## Análise

- **Melhoraram:** complexidade da função principal (de 34 para 1), complexidade
  média, cobertura, quantidade de testes e problemas do Ruff. Nenhuma função
  passa de complexidade B (6).
- **Não melhorou:** o índice de manutenibilidade ficou na mesma faixa (A), mas o
  número caiu levemente. O radon penaliza o tamanho do módulo, e a refatoração
  acrescentou constantes nomeadas, docstrings e funções, que aumentam as linhas
  e o volume. Aceitamos esse custo porque o ganho de clareza e de testabilidade
  não aparece nessa fórmula.

## Como reproduzir

    pytest -v
    pytest --cov=legacy_checkout --cov-report=term-missing
    radon cc src/legacy_checkout.py -s -a
    radon mi src/legacy_checkout.py -s
    ruff check src/legacy_checkout.py --statistics
    python tools/differential_check.py
