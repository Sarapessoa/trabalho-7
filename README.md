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
- Algoritmos `flooding`, `informed_flooding`, `random_walk` e `informed_random_walk`.
- Simulador de buscas por `node_id`, `resource_id`, `ttl` e `algo`.
- Benchmark automatizado com topologias linha, anel, estrela e malha aleatoria.
- Exportacao de CSV consolidado, tabela resumo e graficos comparativos.
- Exemplos de configuracao em `examples/`.
- Testes unitarios para loader, validacoes, algoritmos, simulador, benchmark e graficos.

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

## Verificar tipagem

```bash
python -m mypy src tests
```

## Executar uma busca via Python

```python
from src.config.loader import ConfigLoader
from src.simulation.search_simulator import SearchSimulator
from src.validators.network_validator import NetworkValidator

config = ConfigLoader.load("examples/line.yaml")
NetworkValidator().validate(config)

simulator = SearchSimulator(config.to_network(), seed=42)
result = simulator.run(node_id="n1", resource_id="r5", ttl=4, algo="flooding")

print(result.total_messages)
print(result.total_nodes_involved)
print(result.resource_found)
print(result.resource_owner)
```

## Executar pela CLI

Busca em uma topologia YAML:

```bash
python -m src.cli.main search --config examples/line.yaml --node-id n1 --resource-id r5 --ttl 4 --algo flooding
```

Depois de instalar o projeto, o mesmo comando tambem fica disponivel pelo entry point:

```bash
p2p-search search --config examples/line.yaml --node-id n1 --resource-id r5 --ttl 4 --algo flooding
```

Benchmark automatizado:

```bash
python -m src.cli.main benchmark
```

O benchmark padrao executa:

- Topologias: linha, anel, estrela e malha aleatoria.
- Tamanhos: 10, 25, 50 e 100 nos.
- TTLs: 2, 4, 8 e 16.
- 30 repeticoes por cenario.

Arquivos gerados em `results/`:

- `benchmark_results.csv`
- `benchmark_summary.csv`
- `success_rate_by_algorithm.png`
- `messages_by_ttl.png`

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
- `examples/random_mesh.yaml`

## Validacoes

O carregamento e a validacao da topologia verificam:

- A rede deve ser conectada.
- Cada no deve respeitar `min_neighbors`.
- Cada no deve respeitar `max_neighbors`.
- Nenhuma aresta pode ser self-loop.
- Todas as arestas devem referenciar nos existentes.
- Todos os nos devem possuir ao menos um recurso.
- `num_nodes` deve corresponder ao total de nos em `resources`.

## Metricas

Cada busca retorna:

- `total_messages`
- `total_nodes_involved`
- `resource_found`
- `found`
- `resource_owner`

O resumo do benchmark calcula:

- media de `total_messages`
- media de `total_nodes_involved`
- `success_rate`
