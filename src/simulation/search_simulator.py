"""Coordinates search execution over a validated P2P network."""

from __future__ import annotations

import random

from src.algorithms import SearchAlgorithm, SearchResult
from src.algorithms.flooding import Flooding
from src.algorithms.informed_flooding import InformedFlooding
from src.algorithms.informed_random_walk import InformedRandomWalk
from src.algorithms.random_walk import RandomWalk
from src.network.network import P2PNetwork


class SearchSimulator:
    """Runs named search algorithms against a P2P network."""

    def __init__(self, network: P2PNetwork, seed: int | None = None) -> None:
        self._network = network
        rng = random.Random(seed)
        self._algorithms: dict[str, SearchAlgorithm] = {
            Flooding.name: Flooding(),
            InformedFlooding.name: InformedFlooding(),
            RandomWalk.name: RandomWalk(rng),
            InformedRandomWalk.name: InformedRandomWalk(rng),
        }

    @property
    def algorithms(self) -> list[str]:
        """Return the available algorithm names."""

        return sorted(self._algorithms)

    def run(self, node_id: str, resource_id: str, ttl: int, algo: str) -> SearchResult:
        """Run one search operation."""

        if ttl < 0:
            raise ValueError("ttl deve ser maior ou igual a zero")
        if not self._network.has_node(node_id):
            raise ValueError(f"node_id inexistente: {node_id}")
        if algo not in self._algorithms:
            raise ValueError(f"algoritmo desconhecido: {algo}")

        return self._algorithms[algo].search(self._network, node_id, resource_id, ttl)

