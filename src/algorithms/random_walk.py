"""Random walk search algorithm."""

from __future__ import annotations

import random

from src.algorithms import SearchResult, TraceEvent
from src.network.network import P2PNetwork


class RandomWalk:
    """Forwards the query to one random neighbor at each hop."""

    name = "random_walk"

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run a random walk from a source node."""

        involved: set[str] = {node_id}
        total_messages = 0
        resource_owner: str | None = None
        trace: list[TraceEvent] = []

        def walk(current: str, remaining_ttl: int, path: tuple[str, ...]) -> bool:
            nonlocal resource_owner, total_messages

            trace.append(
                TraceEvent(
                    event="visit",
                    node_id=current,
                    ttl=remaining_ttl,
                    message=f"{current} visitou a busca por {resource_id} com TTL {remaining_ttl}",
                )
            )
            if network.get_node(current).has_resource(resource_id):
                resource_owner = current
                trace.append(
                    TraceEvent(
                        event="found",
                        node_id=current,
                        ttl=remaining_ttl,
                        message=f"{current} encontrou o recurso {resource_id} com TTL {remaining_ttl}",
                    )
                )
                return True

            if remaining_ttl == 0:
                trace.append(
                    TraceEvent(
                        event="ttl_expired",
                        node_id=current,
                        ttl=remaining_ttl,
                        message=f"{current} parou porque o TTL chegou a 0",
                    )
                )
                return False

            candidates = [neighbor for neighbor in network.neighbors(current) if neighbor not in path]
            self._rng.shuffle(candidates)
            if not candidates:
                trace.append(
                    TraceEvent(
                        event="dead_end",
                        node_id=current,
                        ttl=remaining_ttl,
                        message=f"{current} nao possui vizinhos novos para tentar",
                    )
                )
                return False

            for neighbor in candidates:
                next_ttl = remaining_ttl - 1
                total_messages += 1
                involved.add(neighbor)
                trace.append(
                    TraceEvent(
                        event="send",
                        node_id=current,
                        ttl=remaining_ttl,
                        from_node=current,
                        to_node=neighbor,
                        message=f"{current} escolheu {neighbor}; TTL {remaining_ttl} -> {next_ttl}",
                    )
                )
                if walk(neighbor, next_ttl, (*path, neighbor)):
                    return True
                trace.append(
                    TraceEvent(
                        event="backtrack",
                        node_id=current,
                        ttl=remaining_ttl,
                        from_node=neighbor,
                        to_node=current,
                        message=f"{neighbor} voltou para {current}; {current} tentara outro vizinho se existir",
                    )
                )

            return False

        walk(node_id, ttl, (node_id,))
        found = resource_owner is not None
        return SearchResult(
            total_messages=total_messages,
            total_nodes_involved=len(involved),
            resource_found=found,
            found=found,
            resource_owner=resource_owner,
            trace=tuple(trace),
        )
