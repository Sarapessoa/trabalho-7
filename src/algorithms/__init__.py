"""Search algorithms for unstructured P2P networks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.network.network import P2PNetwork


@dataclass(frozen=True)
class TraceEvent:
    """One observable step performed during a search."""

    event: str
    node_id: str
    ttl: int
    message: str
    from_node: str | None = None
    to_node: str | None = None


@dataclass(frozen=True)
class SearchResult:
    """Metrics collected from one search execution."""

    total_messages: int
    total_nodes_involved: int
    resource_found: bool
    found: bool
    resource_owner: str | None
    trace: tuple[TraceEvent, ...] = ()


class SearchAlgorithm(Protocol):
    """Contract implemented by all search algorithms."""

    name: str

    def search(self, network: P2PNetwork, node_id: str, resource_id: str, ttl: int) -> SearchResult:
        """Execute a resource search from a starting node."""
