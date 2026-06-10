"""YAML configuration loader for P2P topologies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.network.network import P2PNetwork


@dataclass(frozen=True)
class NetworkConfig:
    """Raw network configuration loaded from YAML."""

    num_nodes: int
    min_neighbors: int
    max_neighbors: int
    resources: dict[str, list[str]]
    edges: list[tuple[str, str]]

    def to_network(self) -> P2PNetwork:
        """Convert this configuration into a P2PNetwork."""

        return P2PNetwork.from_data(resources=self.resources, edges=self.edges)


class ConfigLoader:
    """Loads network configurations from YAML files."""

    @staticmethod
    def load(path: str | Path) -> NetworkConfig:
        """Load and normalize a YAML topology file."""

        file_path = Path(path)
        with file_path.open("r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file) or {}
        return ConfigLoader.from_dict(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> NetworkConfig:
        """Create a NetworkConfig from a dictionary."""

        required_fields = {"num_nodes", "min_neighbors", "max_neighbors", "resources", "edges"}
        missing = required_fields.difference(data)
        if missing:
            raise ValueError(f"Campos obrigatorios ausentes: {', '.join(sorted(missing))}")

        resources = {
            str(node_id): [str(resource) for resource in node_resources]
            for node_id, node_resources in dict(data["resources"]).items()
        }
        edges = [(str(edge[0]), str(edge[1])) for edge in data["edges"]]

        return NetworkConfig(
            num_nodes=int(data["num_nodes"]),
            min_neighbors=int(data["min_neighbors"]),
            max_neighbors=int(data["max_neighbors"]),
            resources=resources,
            edges=edges,
        )

