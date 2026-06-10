# Implementacao de Algoritmos de Busca em Redes P2P

## Objetivo

Simular uma rede peer-to-peer (P2P) nao estruturada para comparar algoritmos de busca distribuida.

Algoritmos previstos:

- Flooding
- Informed Flooding
- Random Walk
- Informed Random Walk

## Funcionalidades implementadas

- Estrutura de projeto conforme `docs/arquitetura.md`.
- Modelo orientado a objetos para nos e rede P2P.
- Leitura de topologias em YAML.
- Validacoes de conectividade, grau minimo, grau maximo, self-loops, referencias invalidas e recursos por no.
- Exemplos de configuracao em `examples/`.
- Testes unitarios para loader e validacoes.

## Estrutura do projeto

```text
src/
  algorithms/
  network/
  validators/
  simulation/
  experiments/
  visualization/
  config/
  cli/
tests/
examples/
results/
docs/
```

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Executar testes

```bash
python -m pytest
```

## Entrada YAML

```yaml
num_nodes: 5
min_neighbors: 1
max_neighbors: 2
resources:
  n1: [r1]
  n2: [r2]
  n3: [r3]
  n4: [r4]
  n5: [r5]
edges:
  - [n1, n2]
  - [n2, n3]
  - [n3, n4]
  - [n4, n5]
```

Exemplos disponiveis:

- `examples/line.yaml`
- `examples/ring.yaml`
- `examples/star.yaml`

## Validacoes

O carregamento e a validacao da topologia verificam:

- A rede deve ser conectada.
- Cada no deve respeitar `min_neighbors`.
- Cada no deve respeitar `max_neighbors`.
- Nenhuma aresta pode ser self-loop.
- Todas as arestas devem referenciar nos existentes.
- Todos os nos devem possuir ao menos um recurso.
- `num_nodes` deve corresponder ao total de nos em `resources`.

