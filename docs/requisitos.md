# Requisitos

## Entrada

Arquivo YAML contendo:

- num_nodes
- min_neighbors
- max_neighbors
- resources
- edges

## Validações

- Rede conectada
- Grau mínimo respeitado
- Grau máximo respeitado
- Nenhum nó sem recursos
- Nenhuma aresta para o próprio nó

## Operação de busca

Parâmetros:

- node_id
- resource_id
- ttl
- algo

## Algoritmos

- flooding
- informed_flooding
- random_walk
- informed_random_walk

## Resultado

- total_messages
- total_nodes_involved
- found
- resource_owner