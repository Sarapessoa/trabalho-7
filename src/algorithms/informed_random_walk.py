"""Informed random walk search algorithm."""

from __future__ import annotations

import random

import networkx as nx

from src.algorithms import SearchResult
from src.network.network import P2PNetwork


class InformedRandomWalk:
    """Random walk that prefers cached paths to known resource owners."""

    name = "informed_random_walk"

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._resource_cache: dict[str, set[str]] = {}

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run informed random walk from a source node."""

        current = node_id
        previous: str | None = None
        involved: set[str] = {current}
        total_messages = 0

        for _ in range(ttl + 1):
            self._learn_from_node(network, current)
            if network.get_node(current).has_resource(resource_id):
                return SearchResult(
                    total_messages=total_messages,
                    total_nodes_involved=len(involved),
                    resource_found=True,
                    found=True,
                    resource_owner=current,
                )

            if total_messages >= ttl:
                break

            candidates = [neighbor for neighbor in network.neighbors(current) if neighbor != previous]
            if not candidates:
                candidates = network.neighbors(current)
            if not candidates:
                break

            next_node = self._choose_next_node(network, current, resource_id, candidates)
            previous = current
            current = next_node
            involved.add(current)
            total_messages += 1

        return SearchResult(
            total_messages=total_messages,
            total_nodes_involved=len(involved),
            resource_found=False,
            found=False,
            resource_owner=None,
        )

    def _learn_from_node(self, network: P2PNetwork, node_id: str) -> None:
        for resource in network.resources_for(node_id):
            self._resource_cache.setdefault(resource, set()).add(node_id)

    def _choose_next_node(
        self,
        network: P2PNetwork,
        current: str,
        resource_id: str,
        candidates: list[str],
    ) -> str:
        owners = self._resource_cache.get(resource_id, set())
        if not owners:
            return self._rng.choice(candidates)

        ranked_candidates: list[tuple[int, str]] = []
        for candidate in candidates:
            distances = [
                nx.shortest_path_length(network.graph, candidate, owner)
                for owner in owners
                if network.has_node(owner)
            ]
            if distances:
                ranked_candidates.append((int(min(distances)), candidate))

        if not ranked_candidates:
            return self._rng.choice(candidates)
        return sorted(ranked_candidates)[0][1]

