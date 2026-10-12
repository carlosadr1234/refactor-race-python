# REFactor Race Python

## EQUIPE

- Carlos

## DESCRIÇÃO

Refatoração de um sistema legado de processamento de pedidos (`process_order`), preservando o comportamento existente e comprovando a melhoria por meio de testes e métricas (pytest, pytest-cov, radon e ruff).

## DIAGNÓSTICO INICIAL

Métricas medidas antes de qualquer alteração (detalhes em `METRICS.md`): complexidade ciclomática E (34), cobertura de 83%, manutenibilidade A (51.69) e 4 problemas no Ruff.

1. **Função com responsabilidades demais.** `process_order` valida, calcula subtotal, desconto, frete, imposto e pontos, detecta duplicados, guarda estado, imprime e monta o resultado. Isso explica a complexidade E (34) e torna cada regra impossível de testar isoladamente.
2. **Código duplicado e variável morta.** O subtotal é calculado duas vezes (`total1` e `subtotal`) e `total1` nunca é usado. Existe até um comentário admitindo a duplicação.
3. **Condicionais aninhadas.** O desconto por tipo de cliente usa `if/else` dentro de `else` em vários níveis, e o Ruff aponta SIM102 (ifs que podem ser combinados).
4. **Cadeia de `elif` para impostos.** A alíquota por estado deveria ser um mapeamento, e MG e ES repetem o mesmo valor em ramos separados.
5. **Condição repetitiva no frete.** `state == "MG" or state == "SP" or ...` pode virar uma verificação em conjunto, e `express == False` / `express == True` são comparações redundantes com booleanos.
6. **Números mágicos.** 0.15, 0.10, 0.20, 0.05, 1000, 800, 500, 0.25, 1.8, 20, 35, 0.4, 0.6 e as alíquotas aparecem soltos no código, sem nome que explique a regra.
7. **Strings mágicas.** `"vip"`, `"employee"`, `"regular"`, `"PROMO10"`, `"PROMO20"`, `"VIP50"` e os siglas de estados estão espalhados.
8. **Estado global e efeitos colaterais.** A lista global `ORDERS_PROCESSED` e os `print` dentro da função de cálculo misturam regra de negócio com armazenamento e saída.
9. **Busca quadrática de duplicados.** Dois loops aninhados (O(n²)) com `not in` sobre lista, quando uma contagem em passada única (O(n)) produz o mesmo resultado.
10. **Nomes pouco descritivos e idiomas misturados.** `x`, `total1`, `taxa`, `frete`, `desconto` convivem com `subtotal` e `total_final`, dificultando a leitura.
11. **Baixa testabilidade.** Cobertura de 83%: sem testes para VIP abaixo de 1000, funcionário, PROMO20, VIP50, teto de 25%, frete fora do Sudeste, frete expresso e impostos de RJ, ES e demais estados.
12. **Comentários compensando código confuso.** Como "procura produtos repetidos de forma bem pouco elegante", que apontam o problema em vez de resolvê-lo.

## CODE SMELLS ENCONTRADOS

| Code smell | Onde estava | Como foi tratado |
|---|---|---|
| Função longa e com muitas responsabilidades | `process_order` (complexidade E, 34) | Extract Function: virou orquestrador (complexidade A, 1) |
| Código duplicado e variável morta | `total1` e `subtotal` | Cálculo duplicado removido |
| Condicionais aninhadas | desconto por tipo de cliente | Retornos antecipados em `calculate_customer_discount` |
| Números mágicos | percentuais, limites, frete, multiplicador | Constantes nomeadas |
| Strings mágicas | tipos de cliente e cupons | Constantes nomeadas |
| Cadeia de `elif` | alíquota por estado | Mapeamento `TAX_RATES` + `get_tax_rate` |
| Comparações redundantes | `express == True/False`, `state == ... or ...` | `express`, `not express`, `state in {...}` |
| Estrutura de dados e laço inadequados | duplicados com dois laços e `not in` em lista (O(n²)) | `Counter` em passada única (O(n)) |
| Efeitos colaterais misturados ao cálculo | `print` e lista global dentro da regra | `print_order_summary` isolado; global mantido (ver decisões) |
| Nomes pouco descritivos e idiomas misturados | `x`, `total1`, `taxa`, `frete` | Nomes em inglês que revelam intenção |
| Comentários que compensavam código confuso | "pouco elegante", "não confiava" | Removidos; funções com docstring |
| Baixa testabilidade | 83% de cobertura, só via `process_order` | 100% de cobertura e funções testáveis isoladamente |

## REFATORAÇÕES REALIZADAS

### 1. Subtotal duplicado e condicionais redundantes
**PROBLEMA ENCONTRADO:** o subtotal era calculado duas vezes (`total1` nunca era usado) e o frete usava `express == False`, `express == True` e quatro comparações com `or`.
**ALTERAÇÃO REALIZADA:** removido o cálculo morto; condições trocadas por `not express`, `express` e `state in {...}`.
**JUSTIFICATIVA:** menos código sem efeito e condições que dizem o que querem dizer, sem mudar nenhum resultado.

### 2. Números e textos mágicos viram constantes
**PROBLEMA ENCONTRADO:** percentuais, limites, valores de frete, tipos de cliente e cupons espalhados pelo código, e uma cadeia de `elif` para as alíquotas.
**ALTERAÇÃO REALIZADA:** constantes nomeadas no topo do módulo e `TAX_RATES` com `DEFAULT_TAX_RATE`.
**JUSTIFICATIVA:** cada regra de negócio passa a ter um único lugar para ser lida e alterada.

### 3. Subtotal, peso e duplicados em funções próprias
**PROBLEMA ENCONTRADO:** cálculos de coleção embutidos em `process_order`, com busca de duplicados em dois laços aninhados.
**ALTERAÇÃO REALIZADA:** `calculate_subtotal`, `calculate_total_weight` e `find_duplicate_products`, esta última com `Counter`.
**JUSTIFICATIVA:** responsabilidades separadas e testáveis; a busca de duplicados caiu de O(n²) para O(n) mantendo a ordem da primeira ocorrência.

### 4. Regras de desconto separadas
**PROBLEMA ENCONTRADO:** desconto por cliente, cupons e teto misturados, com `if` aninhado em `else`.
**ALTERAÇÃO REALIZADA:** `calculate_customer_discount`, `calculate_coupon_discount` e `calculate_discount`, com retornos antecipados.
**JUSTIFICATIVA:** cada regra fica isolada e legível, e o teto de 25% aparece em um único ponto.

### 5. Frete, imposto, pontos e impressão
**PROBLEMA ENCONTRADO:** `process_order` ainda calculava frete, imposto e pontos e imprimia o resumo.
**ALTERAÇÃO REALIZADA:** `calculate_shipping`, `get_tax_rate`, `calculate_loyalty_points` e `print_order_summary`; `process_order` só orquestra.
**JUSTIFICATIVA:** separa calcular de imprimir e deixa a função principal com complexidade 1.

## TESTES ADICIONADOS

- **Testes de caracterização (32):** travam o comportamento antes de refatorar. Cobrem desconto de VIP (abaixo e a partir de 1000), funcionário e regular (abaixo e a partir de 800), cliente desconhecido, cupons `PROMO20`, `VIP50` e inexistente, teto de 25%, frete grátis, expresso, fora do Sudeste, peso por quantidade, alíquota por estado, estado padrão, duplicados (nenhum, repetidos várias vezes, ordem) e efeitos colaterais (histórico e impressão).
- **Testes unitários das funções extraídas (30):** verificam cada regra isoladamente, incluindo casos limite (999 e 1000, 799 e 800, 499 e 500).
- **Verificação diferencial:** `tools/differential_check.py` compara o código atual com a versão original em 60000 casos aleatórios, incluindo o texto impresso.
- Total: 66 testes, todos passando.

## MÉTRICAS ANTES E DEPOIS

| Indicador | Antes | Depois |
|---|---|---|
| Testes passando | 4 de 4 | 66 de 66 |
| Cobertura de testes | 83% | 100% |
| Complexidade da função principal | E (34) | A (1) |
| Complexidade média | E (34.0) | A (2.9) |
| Índice de manutenibilidade | A (51.69) | A (47.03) |
| Problemas do Ruff | 4 | 0 |

Detalhes e análise em `METRICS.md`. O índice de manutenibilidade caiu levemente
(mesma faixa A): o radon penaliza o tamanho do módulo, e a refatoração
acrescentou constantes, docstrings e funções.

## DECISÕES TÉCNICAS

- **Mesmo nome de arquivo, módulo e assinatura.** Os testes (inclusive os do professor) importam `legacy_checkout.process_order`; mudar isso quebraria a interface sem ganho.
- **Laço explícito em vez de `sum()`.** No Python 3.12+ `sum()` de floats usa soma compensada: `sum([0.1] * 10)` dá `1.0`, enquanto o laço dá `0.9999999999999999`. Isso poderia mudar centavos em relação ao original, então o laço foi mantido.
- **`Counter` para duplicados.** Mantém a ordem da primeira ocorrência, igual ao código original, em uma única passada.
- **Constantes simples em vez de classes ou enums.** O sistema é pequeno; mais estrutura seria complexidade sem necessidade.
- **`not express` assume valor booleano.** Difere do `express == False` original só se `express` receber algo não booleano (por exemplo `None`).
- **`ORDERS_PROCESSED` e `print` mantidos.** São comportamento observável; remover seria mudança de regra. O `print` foi isolado em `print_order_summary`.
- **Pontos calculados sobre o valor não arredondado**, como no original.
- **Regras que parecem estranhas foram preservadas**, por exemplo o peso somar itens com quantidade não positiva, e não corrigidas.
- **Prova de equivalência:** testes de caracterização, testes unitários, cobertura de 100% e comparação diferencial com a versão original.

## USO DE INTELIGÊNCIA ARTIFICIAL

Ferramenta utilizada: Claude (Anthropic).

Finalidade: apoio na leitura do código, no planejamento das etapas, na escrita dos testes de caracterização e na proposta das refatorações. As métricas foram medidas com as ferramentas do enunciado.

Exemplo de sugestão recebida: usar `Counter` para achar duplicados em uma passada; trocar `express == True/False` por `express`/`not express`; e, como ideia descartada, usar `sum()` nas somas.

A sugestão foi aceita, modificada ou rejeitada? `Counter` e a simplificação de `express` foram aceitas; `sum()` foi rejeitada porque pode alterar centavos no Python 3.12+ (ver Decisões Técnicas).

Como a equipe validou a solução? Rodando os testes após cada etapa (cada commit só foi feito com testes passando), 100% de cobertura, comparação diferencial com a versão original em 60000 casos e leitura do diff de cada commit.

## MELHORIAS FUTURAS

- Validar entradas (quantidade inválida, itens sem `name` ou `price`); depende de requisito do professor, por exemplo o Ticket 1.
- Tornar o cupom insensível a maiúsculas (Ticket 2, se for liberado).
- Revisar a regra de pontos (Ticket 3, se for liberado).
- Tirar o histórico global `ORDERS_PROCESSED` e o `print` da função de pedido, o que mudaria comportamento observável e exige um requisito.
- Usar `decimal.Decimal` para valores monetários em vez de `float`.
- Revisar o peso de itens com quantidade não positiva, que hoje entra no frete mas não no subtotal.
