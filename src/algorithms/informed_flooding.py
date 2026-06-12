"""Informed flooding search algorithm."""

from __future__ import annotations

import networkx as nx

from src.algorithms import SearchResult, TraceEvent
from src.algorithms.flooding import Flooding
from src.network.network import P2PNetwork


class InformedFlooding:
    """Flooding variant that uses a learned resource cache."""

    name = "informed_flooding"

    def __init__(self) -> None:
        self._resource_cache: dict[str, set[str]] = {}
        self._fallback = Flooding()

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run informed flooding, using cached owners when available."""

        self._learn_from_node(network, node_id)
        cached_owner = self._best_cached_owner(network, node_id, resource_id, ttl)
        if cached_owner is not None:
            path = nx.shortest_path(network.graph, node_id, cached_owner)
            trace: list[TraceEvent] = [
                TraceEvent(
                    event="start",
                    node_id=node_id,
                    ttl=ttl,
                    message=f"{node_id} iniciou a busca informada por {resource_id} com TTL {ttl}",
                )
            ]
            for path_node in path:
                self._learn_from_node(network, path_node)
            remaining_ttl = ttl
            for current, next_node in zip(path, path[1:]):
                trace.append(
                    TraceEvent(
                        event="visit",
                        node_id=current,
                        ttl=remaining_ttl,
                        message=f"{current} recebeu a busca informada por {resource_id} com TTL {remaining_ttl}",
                    )
                )
                trace.append(
                    TraceEvent(
                        event="send",
                        node_id=current,
                        ttl=remaining_ttl,
                        from_node=current,
                        to_node=next_node,
                        message=f"{current} usou cache e mandou para {next_node}; TTL {remaining_ttl} -> {remaining_ttl - 1}",
                    )
                )
                remaining_ttl -= 1
            trace.append(
                TraceEvent(
                    event="visit",
                    node_id=cached_owner,
                    ttl=remaining_ttl,
                    message=f"{cached_owner} recebeu a busca informada por {resource_id} com TTL {remaining_ttl}",
                )
            )
            trace.append(
                TraceEvent(
                    event="found",
                    node_id=cached_owner,
                    ttl=remaining_ttl,
                    message=f"{cached_owner} encontrou o recurso {resource_id} via cache com TTL {remaining_ttl}",
                )
            )
            return SearchResult(
                total_messages=max(0, len(path) - 1),
                total_nodes_involved=len(set(path)),
                resource_found=True,
                found=True,
                resource_owner=cached_owner,
                trace=tuple(trace),
            )

        result = self._fallback.search(network, node_id, resource_id, ttl)
        for node in network.node_ids:
            self._learn_from_node(network, node)
        return result

    def _learn_from_node(self, network: P2PNetwork, node_id: str) -> None:
        for resource in network.resources_for(node_id):
            self._resource_cache.setdefault(resource, set()).add(node_id)

    def _best_cached_owner(
        self,
        network: P2PNetwork,
        node_id: str,
        resource_id: str,
        ttl: int,
    ) -> str | None:
        owners = self._resource_cache.get(resource_id, set())
        reachable: list[tuple[int, str]] = []
        for owner in owners:
            if not network.has_node(owner):
                continue
            distance = nx.shortest_path_length(network.graph, node_id, owner)
            if distance <= ttl:
                reachable.append((int(distance), owner))
        if not reachable:
            return None
        return sorted(reachable)[0][1]
