"""Informed random walk search algorithm."""

from __future__ import annotations

import random

import networkx as nx

from src.algorithms import SearchResult, TraceEvent
from src.network.network import P2PNetwork


class InformedRandomWalk:
    """Random walk that prefers cached paths to known resource owners."""

    name = "informed_random_walk"

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._resource_cache: dict[str, set[str]] = {}

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Run informed random walk from a source node."""

        involved: set[str] = {node_id}
        total_messages = 0
        resource_owner: str | None = None
        trace: list[TraceEvent] = []

        def walk(current: str, remaining_ttl: int, path: tuple[str, ...]) -> bool:
            nonlocal resource_owner, total_messages

            self._learn_from_node(network, current)
            trace.append(
                TraceEvent(
                    event="visit",
                    node_id=current,
                    ttl=remaining_ttl,
                    message=f"{current} visitou a busca informada por {resource_id} com TTL {remaining_ttl}",
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

            for neighbor in self._ordered_candidates(network, resource_id, candidates):
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

    def _learn_from_node(self, network: P2PNetwork, node_id: str) -> None:
        for resource in network.resources_for(node_id):
            self._resource_cache.setdefault(resource, set()).add(node_id)

    def _ordered_candidates(
        self,
        network: P2PNetwork,
        resource_id: str,
        candidates: list[str],
    ) -> list[str]:
        owners = self._resource_cache.get(resource_id, set())
        if not owners:
            shuffled = candidates.copy()
            self._rng.shuffle(shuffled)
            return shuffled

        ranked_candidates: list[tuple[int, str]] = []
        unknown_candidates: list[str] = []
        for candidate in candidates:
            distances = [
                nx.shortest_path_length(network.graph, candidate, owner)
                for owner in owners
                if network.has_node(owner)
            ]
            if distances:
                ranked_candidates.append((int(min(distances)), candidate))
            else:
                unknown_candidates.append(candidate)

        if not ranked_candidates:
            shuffled = candidates.copy()
            self._rng.shuffle(shuffled)
            return shuffled

        self._rng.shuffle(unknown_candidates)
        return [candidate for _, candidate in sorted(ranked_candidates)] + unknown_candidates
