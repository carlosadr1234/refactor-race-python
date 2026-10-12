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

(Será consolidado depois da refatoração.)

## REFATORAÇÕES REALIZADAS

(Para cada uma: problema encontrado, alteração realizada e justificativa.)

## TESTES ADICIONADOS

(A preencher.)

## MÉTRICAS ANTES E DEPOIS

Ver `METRICS.md`.

## DECISÕES TÉCNICAS

(A preencher.)

## USO DE INTELIGÊNCIA ARTIFICIAL

Ferramenta utilizada: Claude (Anthropic).
Finalidade: apoio na leitura do código, no planejamento das etapas e na configuração do ambiente.
Exemplo de sugestão recebida: (a preencher)
A sugestão foi aceita, modificada ou rejeitada? (a preencher)
Como a equipe validou a solução? (a preencher)

## MELHORIAS FUTURAS

(A preencher.)
