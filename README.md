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
- Rastro passo a passo das mensagens enviadas, do TTL restante, de retornos e de recursos encontrados.
- Modo interativo para carregar uma rede uma vez e executar varias buscas.
- Interface grafica interativa para carregar YAML, executar buscas e salvar rastros.
- Benchmark automatizado com topologias linha, anel, estrela e malha aleatoria.
- Exportacao de CSV consolidado, tabela resumo e graficos comparativos.
- Exemplos de configuracao em `examples/`.
- Testes unitarios para loader, validacoes, algoritmos, simulador, benchmark e graficos.

## Plano do projeto

- [x] Ler todos os arquivos Markdown do repositorio antes de iniciar.
- [x] Criar a estrutura completa conforme `docs/arquitetura.md`.
- [x] Implementar modelo orientado a objetos para nos e rede P2P.
- [x] Implementar leitura de YAML.
- [x] Implementar validacao de conectividade da rede.
- [x] Implementar validacao de `min_neighbors`.
- [x] Implementar validacao de `max_neighbors`.
- [x] Implementar validacao de ausencia de self-loops.
- [x] Implementar validacao de recursos em todos os nos.
- [x] Implementar algoritmo `flooding`.
- [x] Implementar algoritmo `informed_flooding`.
- [x] Implementar algoritmo `random_walk`.
- [x] Implementar algoritmo `informed_random_walk`.
- [x] Implementar simulador de buscas.
- [x] Implementar rastro detalhado de execucao das buscas.
- [x] Implementar modo interativo para buscas repetidas.
- [x] Implementar interface grafica interativa.
- [x] Implementar benchmark automatizado.
- [x] Gerar CSV consolidado com resultados.
- [x] Gerar tabela resumo.
- [x] Gerar graficos comparativos.
- [x] Criar exemplos de configuracao em `examples/`.
- [x] Criar testes unitarios.
- [x] Atualizar README com uso, metricas e comandos.
- [x] Configurar checagem de tipos com `mypy`.
- [x] Configurar entry point `p2p-search`.
- [x] Executar testes e validacoes finais.
- [x] Fazer commits pequenos e organizados.

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
for event in result.trace:
    print(event.message)
```

## Executar pela CLI

Busca em uma topologia YAML:

```bash
python -m src.cli.main search --config examples/line.yaml --node-id n1 --resource-id r5 --ttl 4 --algo flooding
```

Salvar o passo a passo em arquivo:

```bash
python -m src.cli.main search --config examples/line.yaml --node-id n1 --resource-id r5 --ttl 4 --algo flooding --trace-output results/rastro.txt
```

Carregar uma rede uma vez e executar varias buscas pelo menu:

```bash
python -m src.cli.main interactive --config examples/line.yaml
```

## Executar pela interface grafica

A interface grafica permite selecionar o arquivo YAML, escolher no inicial, recurso, TTL, algoritmo e seed, executar a busca e salvar o rastro em `.txt`.

```bash
python -m src.gui.app
```

Depois de instalar o projeto, tambem e possivel abrir pela entrada:

```bash
p2p-search-gui
```

A busca via CLI tambem fica disponivel pelo entry point depois de instalar o projeto:

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
- `trace`

## Semantica das buscas

O `ttl` representa a profundidade maxima da busca.

No `flooding`, cada no repassa a consulta para todos os vizinhos validos enquanto ainda houver TTL. Se um ramo encontra o recurso, os outros ramos continuam executando ate o TTL acabar, simulando entidades independentes que nao recebem uma notificacao global de parada.

No `random_walk`, a busca escolhe um vizinho por vez em ordem aleatoria. Quando um caminho acaba ou atinge TTL 0 sem encontrar o recurso, a busca volta para o no anterior e tenta outro vizinho ainda nao explorado. Assim, se o recurso estiver dentro da profundidade permitida, a busca consegue encontra-lo; a aleatoriedade afeta a ordem das tentativas e a quantidade de mensagens.

As versoes `informed_flooding` e `informed_random_walk` mantem uma cache simples de recursos aprendidos para priorizar caminhos conhecidos quando possivel.

O resumo do benchmark calcula:

- media de `total_messages`
- media de `total_nodes_involved`
- `success_rate`
