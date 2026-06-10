"""Validation rules for P2P network topology files."""

from __future__ import annotations

import networkx as nx

from src.config.loader import NetworkConfig


class NetworkValidator:
    """Validates a network against the project requirements."""

    def validate(self, config: NetworkConfig) -> None:
        """Raise ValueError when any topology rule is violated."""

        network = config.to_network()
        errors: list[str] = []

        if len(config.resources) != config.num_nodes:
            errors.append("num_nodes deve corresponder ao total de nos em resources")

        for node_a, node_b in config.edges:
            if node_a == node_b:
                errors.append(f"self-loop encontrado em {node_a}")
            if node_a not in config.resources or node_b not in config.resources:
                errors.append(f"aresta referencia no inexistente: {node_a}-{node_b}")

        for node_id, resources in config.resources.items():
            if not resources:
                errors.append(f"no sem recursos: {node_id}")

        for node_id in config.resources:
            degree = network.degree(node_id)
            if degree < config.min_neighbors:
                errors.append(f"{node_id} possui grau {degree}, abaixo de min_neighbors")
            if degree > config.max_neighbors:
                errors.append(f"{node_id} possui grau {degree}, acima de max_neighbors")

        if config.resources and not nx.is_connected(network.graph):
            errors.append("rede deve ser conectada")

        if errors:
            raise ValueError("; ".join(errors))

