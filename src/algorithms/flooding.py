"""Flooding search algorithm."""

from __future__ import annotations

from collections import deque

from src.algorithms import SearchResult, TraceEvent
from src.network.network import P2PNetwork


class Flooding:
    """Propagates the query to all neighbors until TTL expires."""

    name = "flooding"

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run flooding from a source node."""

        queue: deque[tuple[str, str | None, int]] = deque([(node_id, None, ttl)])
        visited: set[str] = set()
        involved: set[str] = {node_id}
        total_messages = 0
        resource_owner: str | None = None
        trace: list[TraceEvent] = [
            TraceEvent(
                event="start",
                node_id=node_id,
                ttl=ttl,
                message=f"{node_id} iniciou a busca por {resource_id} com TTL {ttl}",
            )
        ]

        while queue:
            current, previous, remaining_ttl = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            trace.append(
                TraceEvent(
                    event="visit",
                    node_id=current,
                    ttl=remaining_ttl,
                    message=f"{current} recebeu a busca por {resource_id} com TTL {remaining_ttl}",
                )
            )

            if network.get_node(current).has_resource(resource_id):
                if resource_owner is None:
                    resource_owner = current
                trace.append(
                    TraceEvent(
                        event="found",
                        node_id=current,
                        ttl=remaining_ttl,
                        message=f"{current} encontrou o recurso {resource_id} com TTL {remaining_ttl}",
                    )
                )

            if remaining_ttl == 0:
                trace.append(
                    TraceEvent(
                        event="ttl_expired",
                        node_id=current,
                        ttl=remaining_ttl,
                        message=f"{current} parou porque o TTL chegou a 0",
                    )
                )
                continue

            for neighbor in network.neighbors(current):
                if neighbor == previous or neighbor in visited:
                    continue
                total_messages += 1
                involved.add(neighbor)
                next_ttl = remaining_ttl - 1
                trace.append(
                    TraceEvent(
                        event="send",
                        node_id=current,
                        ttl=remaining_ttl,
                        from_node=current,
                        to_node=neighbor,
                        message=f"{current} mandou mensagem para {neighbor}; TTL {remaining_ttl} -> {next_ttl}",
                    )
                )
                queue.append((neighbor, current, next_ttl))

        found = resource_owner is not None
        return SearchResult(
            total_messages=total_messages,
            total_nodes_involved=len(involved),
            resource_found=found,
            found=found,
            resource_owner=resource_owner,
            trace=tuple(trace),
        )
