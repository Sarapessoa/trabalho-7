from __future__ import annotations

from pathlib import Path

from src.config.loader import ConfigLoader
from src.experiments.benchmark import Benchmark, build_topology_config
from src.validators.network_validator import NetworkValidator
from src.visualization.plots import generate_plots


def test_generated_topologies_are_valid() -> None:
    for topology in ["line", "ring", "star", "random_mesh"]:
        config = build_topology_config(topology, num_nodes=10, seed=42)

        NetworkValidator().validate(config)


def test_benchmark_returns_expected_rows() -> None:
    benchmark = Benchmark(seed=42)

    results = benchmark.run(topologies=["line"], sizes=[5], ttls=[2], repetitions=2)

    assert len(results) == 8
    assert set(results["algorithm"]) == {
        "flooding",
        "informed_flooding",
        "random_walk",
        "informed_random_walk",
    }
    assert {"total_messages", "total_nodes_involved", "resource_found"}.issubset(results.columns)


def test_benchmark_saves_csv_and_plots(tmp_path: Path) -> None:
    benchmark = Benchmark(seed=42)
    results = benchmark.run(topologies=["line"], sizes=[5], ttls=[2], repetitions=1)

    csv_path, summary_path = benchmark.save_results(results, tmp_path)
    bar_path, line_path = generate_plots(results, tmp_path)

    assert csv_path.exists()
    assert summary_path.exists()
    assert bar_path.exists()
    assert line_path.exists()


def test_random_mesh_example_is_valid() -> None:
    config = ConfigLoader.load("examples/random_mesh.yaml")

    NetworkValidator().validate(config)

