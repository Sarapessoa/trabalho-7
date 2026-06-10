"""Flooding search algorithm."""

from __future__ import annotations

from collections import deque

from src.algorithms import SearchResult
from src.network.network import P2PNetwork


class Flooding:
    """Propagates the query to all neighbors until TTL expires."""

    name = "flooding"

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run flooding from a source node."""

        queue: deque[tuple[str, str | None, int]] = deque([(node_id, None, 0)])
        visited: set[str] = set()
        involved: set[str] = {node_id}
        total_messages = 0
        resource_owner: str | None = None

        while queue:
            current, previous, depth = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if network.get_node(current).has_resource(resource_id):
                resource_owner = current
                break

            if depth >= ttl:
                continue

            for neighbor in network.neighbors(current):
                if neighbor == previous or neighbor in visited:
                    continue
                total_messages += 1
                involved.add(neighbor)
                queue.append((neighbor, current, depth + 1))

        found = resource_owner is not None
        return SearchResult(
            total_messages=total_messages,
            total_nodes_involved=len(involved),
            resource_found=found,
            found=found,
            resource_owner=resource_owner,
        )

