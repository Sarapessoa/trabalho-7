"""Node representation for the P2P network."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    """Represents a peer with a set of locally available resources."""

    node_id: str
    resources: frozenset[str] = field(default_factory=frozenset)

    def has_resource(self, resource_id: str) -> bool:
        """Return True when the node stores the requested resource."""

        return resource_id in self.resources

