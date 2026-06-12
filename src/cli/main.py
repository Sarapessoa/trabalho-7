"""CLI entry point for searches and benchmark execution."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config.loader import ConfigLoader
from src.experiments.benchmark import Benchmark
from src.simulation.report import format_search_result
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
    search.add_argument("--trace-output", help="Arquivo para salvar o passo a passo da busca.")

    interactive = subparsers.add_parser("interactive", help="Carrega uma topologia e abre um menu de buscas.")
    interactive.add_argument("--config", required=True, help="Arquivo YAML da topologia.")
    interactive.add_argument("--seed", type=int, default=42, help="Semente para reprodutibilidade.")

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
        output = format_search_result(result)
        print(output)
        if args.trace_output:
            Path(args.trace_output).write_text(output + "\n", encoding="utf-8")
        return

    if args.command == "interactive":
        config = ConfigLoader.load(args.config)
        NetworkValidator().validate(config)
        simulator = SearchSimulator(config.to_network(), seed=args.seed)
        run_interactive_menu(simulator)
        return

    benchmark = Benchmark(seed=args.seed)
    results = benchmark.run(repetitions=args.repetitions)
    csv_path, summary_path = benchmark.save_results(results, Path(args.output_dir))
    bar_path, line_path = generate_plots(results, Path(args.output_dir))
    print(f"CSV consolidado: {csv_path}")
    print(f"Tabela resumo: {summary_path}")
    print(f"Grafico de barras: {bar_path}")
    print(f"Grafico de linhas: {line_path}")


def run_interactive_menu(simulator: SearchSimulator) -> None:
    """Run repeated searches over an already loaded network."""

    print("Rede carregada. Digite 'sair' no node_id para encerrar.")
    print(f"Algoritmos disponiveis: {', '.join(simulator.algorithms)}")
    while True:
        node_id = input("node_id: ").strip()
        if node_id.lower() in {"sair", "exit", "q"}:
            return
        resource_id = input("resource_id: ").strip()
        ttl_text = input("ttl: ").strip()
        algo = input("algo: ").strip()
        output_path = input("arquivo de rastro opcional: ").strip()

        try:
            ttl = int(ttl_text)
            result = simulator.run(node_id=node_id, resource_id=resource_id, ttl=ttl, algo=algo)
        except ValueError as error:
            print(f"Erro: {error}")
            continue

        output = format_search_result(result)
        print(output)
        if output_path:
            Path(output_path).write_text(output + "\n", encoding="utf-8")
            print(f"Rastro salvo em: {output_path}")


if __name__ == "__main__":
    main()
