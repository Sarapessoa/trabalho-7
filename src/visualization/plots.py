"""Comparative charts for benchmark results."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.experiments.benchmark import Benchmark


def generate_plots(results: pd.DataFrame, output_dir: str | Path = "results") -> tuple[Path, Path]:
    """Generate bar and line charts from benchmark results."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = Benchmark.summarize(results)

    bar_path = output_path / "success_rate_by_algorithm.png"
    line_path = output_path / "messages_by_ttl.png"

    success = summary.groupby("algorithm", as_index=True)["success_rate"].mean().sort_index()
    success.plot(kind="bar", color="#2F6F73")
    plt.title("Taxa de sucesso por algoritmo")
    plt.xlabel("Algoritmo")
    plt.ylabel("Taxa de sucesso")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    messages = summary.groupby(["ttl", "algorithm"], as_index=False)["avg_total_messages"].mean()
    for algorithm, group in messages.groupby("algorithm"):
        ordered = group.sort_values("ttl")
        plt.plot(ordered["ttl"], ordered["avg_total_messages"], marker="o", label=algorithm)
    plt.title("Mensagens medias por TTL")
    plt.xlabel("TTL")
    plt.ylabel("Mensagens medias")
    plt.legend()
    plt.tight_layout()
    plt.savefig(line_path)
    plt.close()

    return bar_path, line_path

