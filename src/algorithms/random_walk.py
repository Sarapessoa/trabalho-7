"""Random walk search algorithm."""

from __future__ import annotations

import random

from src.algorithms import SearchResult
from src.network.network import P2PNetwork


class RandomWalk:
    """Forwards the query to one random neighbor at each hop."""

    name = "random_walk"

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run a random walk from a source node."""

        current = node_id
        previous: str | None = None
        involved: set[str] = {current}
        total_messages = 0

        for _ in range(ttl + 1):
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

            previous = current
            current = self._rng.choice(candidates)
            involved.add(current)
            total_messages += 1

        return SearchResult(
            total_messages=total_messages,
            total_nodes_involved=len(involved),
            resource_found=False,
            found=False,
            resource_owner=None,
        )

