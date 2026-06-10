"""CLI entry point for searches and benchmark execution."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config.loader import ConfigLoader
from src.experiments.benchmark import Benchmark
from src.simulation.search_simulator import SearchSimulator
from src.validators.network_validator import NetworkValidator
from src.visualization.plots import generate_plots


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(description="Simulador de buscas em redes P2P.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Executa uma busca em uma topologia YAML.")
    search.add_argument("--config", required=True, help="Arquivo YAML da topologia.")
    search.add_argument("--node-id", required=True, help="No inicial da busca.")
    search.add_argument("--resource-id", required=True, help="Recurso procurado.")
    search.add_argument("--ttl", required=True, type=int, help="TTL da busca.")
    search.add_argument("--algo", required=True, help="Algoritmo de busca.")
    search.add_argument("--seed", type=int, default=42, help="Semente para reprodutibilidade.")

    benchmark = subparsers.add_parser("benchmark", help="Executa o benchmark automatizado.")
    benchmark.add_argument("--output-dir", default="results", help="Diretorio de saida.")
    benchmark.add_argument("--seed", type=int, default=42, help="Semente para reprodutibilidade.")
    benchmark.add_argument("--repetitions", type=int, default=30, help="Repeticoes por cenario.")

    return parser


def main() -> None:
    """Run the CLI."""

    args = build_parser().parse_args()

    if args.command == "search":
        config = ConfigLoader.load(args.config)
        NetworkValidator().validate(config)
        simulator = SearchSimulator(config.to_network(), seed=args.seed)
        result = simulator.run(args.node_id, args.resource_id, args.ttl, args.algo)
        print(result)
        return

    benchmark = Benchmark(seed=args.seed)
    results = benchmark.run(repetitions=args.repetitions)
    csv_path, summary_path = benchmark.save_results(results, Path(args.output_dir))
    bar_path, line_path = generate_plots(results, Path(args.output_dir))
    print(f"CSV consolidado: {csv_path}")
    print(f"Tabela resumo: {summary_path}")
    print(f"Grafico de barras: {bar_path}")
    print(f"Grafico de linhas: {line_path}")


if __name__ == "__main__":
    main()

