"""Automated benchmark for P2P search algorithms."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import random

import pandas as pd

from src.config.loader import NetworkConfig
from src.network.network import P2PNetwork
from src.simulation.search_simulator import SearchSimulator
from src.validators.network_validator import NetworkValidator

DEFAULT_TOPOLOGIES = ["line", "ring", "star", "random_mesh"]
DEFAULT_SIZES = [10, 25, 50, 100]
DEFAULT_TTLS = [2, 4, 8, 16]
DEFAULT_REPETITIONS = 30


class Benchmark:
    """Runs reproducible experiments across topologies, sizes and TTLs."""

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed

    def run(
        self,
        topologies: list[str] | None = None,
        sizes: list[int] | None = None,
        ttls: list[int] | None = None,
        repetitions: int = DEFAULT_REPETITIONS,
    ) -> pd.DataFrame:
        """Run the benchmark and return one row per algorithm execution."""

        selected_topologies = topologies or DEFAULT_TOPOLOGIES
        selected_sizes = sizes or DEFAULT_SIZES
        selected_ttls = ttls or DEFAULT_TTLS
        rows: list[dict[str, object]] = []

        for topology in selected_topologies:
            for num_nodes in selected_sizes:
                config = build_topology_config(topology, num_nodes, seed=self._seed)
                NetworkValidator().validate(config)
                network = config.to_network()

                for ttl in selected_ttls:
                    simulator = SearchSimulator(network, seed=self._seed + ttl + num_nodes)
                    for repetition in range(repetitions):
                        source = f"n{(repetition % num_nodes) + 1}"
                        target_index = ((repetition * 7) % num_nodes) + 1
                        resource = f"r{target_index}"

                        for algorithm in simulator.algorithms:
                            result = simulator.run(
                                node_id=source,
                                resource_id=resource,
                                ttl=ttl,
                                algo=algorithm,
                            )
                            rows.append(
                                {
                                    "topology": topology,
                                    "num_nodes": num_nodes,
                                    "ttl": ttl,
                                    "repetition": repetition + 1,
                                    "algorithm": algorithm,
                                    **asdict(result),
                                }
                            )

        return pd.DataFrame(rows)

    def save_results(self, results: pd.DataFrame, output_dir: str | Path = "results") -> tuple[Path, Path]:
        """Save consolidated CSV and summary CSV."""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        consolidated_path = output_path / "benchmark_results.csv"
        summary_path = output_path / "benchmark_summary.csv"

        results.to_csv(consolidated_path, index=False)
        self.summarize(results).to_csv(summary_path, index=False)

        return consolidated_path, summary_path

    @staticmethod
    def summarize(results: pd.DataFrame) -> pd.DataFrame:
        """Aggregate benchmark rows into the required summary metrics."""

        grouped = results.groupby(["topology", "num_nodes", "ttl", "algorithm"], as_index=False)
        return grouped.agg(
            avg_total_messages=("total_messages", "mean"),
            avg_total_nodes_involved=("total_nodes_involved", "mean"),
            success_rate=("resource_found", "mean"),
        )


def build_topology_config(topology: str, num_nodes: int, seed: int = 42) -> NetworkConfig:
    """Build a reproducible topology configuration."""

    if num_nodes < 2:
        raise ValueError("num_nodes deve ser maior ou igual a 2")

    resources = {f"n{i}": [f"r{i}"] for i in range(1, num_nodes + 1)}

    if topology == "line":
        edges = [(f"n{i}", f"n{i + 1}") for i in range(1, num_nodes)]
        return NetworkConfig(num_nodes, 1, 2, resources, edges)

    if topology == "ring":
        edges = [(f"n{i}", f"n{i + 1}") for i in range(1, num_nodes)]
        edges.append((f"n{num_nodes}", "n1"))
        return NetworkConfig(num_nodes, 2, 2, resources, edges)

    if topology == "star":
        edges = [("n1", f"n{i}") for i in range(2, num_nodes + 1)]
        return NetworkConfig(num_nodes, 1, num_nodes - 1, resources, edges)

    if topology == "random_mesh":
        edges = _build_random_mesh_edges(num_nodes, seed)
        return NetworkConfig(num_nodes, 1, min(6, num_nodes - 1), resources, edges)

    raise ValueError(f"topologia desconhecida: {topology}")


def _build_random_mesh_edges(num_nodes: int, seed: int) -> list[tuple[str, str]]:
    rng = random.Random(seed + num_nodes)
    max_neighbors = min(6, num_nodes - 1)
    edges: set[tuple[str, str]] = set()
    degrees = {f"n{i}": 0 for i in range(1, num_nodes + 1)}

    for i in range(2, num_nodes + 1):
        node = f"n{i}"
        candidates = [f"n{j}" for j in range(1, i) if degrees[f"n{j}"] < max_neighbors]
        parent = rng.choice(candidates)
        _add_sorted_edge(edges, degrees, node, parent)

    possible_edges = [
        (f"n{i}", f"n{j}")
        for i in range(1, num_nodes + 1)
        for j in range(i + 1, num_nodes + 1)
    ]
    rng.shuffle(possible_edges)
    target_edges = min(len(possible_edges), num_nodes * 2)

    for node_a, node_b in possible_edges:
        if len(edges) >= target_edges:
            break
        if degrees[node_a] >= max_neighbors or degrees[node_b] >= max_neighbors:
            continue
        _add_sorted_edge(edges, degrees, node_a, node_b)

    return sorted(edges)


def _add_sorted_edge(
    edges: set[tuple[str, str]],
    degrees: dict[str, int],
    node_a: str,
    node_b: str,
) -> None:
    left, right = sorted((node_a, node_b))
    edge = (left, right)
    if edge in edges:
        return
    edges.add(edge)
    degrees[node_a] += 1
    degrees[node_b] += 1
