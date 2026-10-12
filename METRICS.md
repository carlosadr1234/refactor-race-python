# Métricas: REFactor Race Python

| Indicador | Antes | Depois |
|---|---|---|
| Testes passando | 4 de 4 | |
| Quantidade de testes | 4 | |
| Cobertura de testes | 83% | |
| Complexidade da função principal | E (34) | |
| Complexidade média | E (34.0) | |
| Índice de manutenibilidade | A (51.69) | |
| Problemas identificados pelo Ruff | 4 | |

## Como reproduzir

    pytest -v
    pytest --cov=legacy_checkout --cov-report=term-missing
    radon cc src/legacy_checkout.py -s -a
    radon mi src/legacy_checkout.py -s
    ruff check src/legacy_checkout.py --statistics
