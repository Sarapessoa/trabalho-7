"""P2P network abstraction built on top of NetworkX."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import networkx as nx

from src.network.node import Node


class P2PNetwork:
    """Undirected unstructured P2P network."""

    def __init__(self) -> None:
        self._graph = nx.Graph()
        self._nodes: dict[str, Node] = {}

    @property
    def graph(self) -> nx.Graph:
        """Return the underlying graph for validation and analysis."""

        return self._graph

    @property
    def node_ids(self) -> list[str]:
        """Return node identifiers in insertion order."""

        return list(self._nodes)

    def add_node(self, node: Node) -> None:
        """Add a node to the network."""

        self._nodes[node.node_id] = node
        self._graph.add_node(node.node_id)

    def add_edge(self, node_a: str, node_b: str) -> None:
        """Add an undirected edge between two existing or future nodes."""

        self._graph.add_edge(node_a, node_b)

    def get_node(self, node_id: str) -> Node:
        """Return a node by id."""

        return self._nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """Return True when the network contains the node id."""

        return node_id in self._nodes

    def neighbors(self, node_id: str) -> list[str]:
        """Return sorted neighbors for deterministic traversal."""

        return sorted(self._graph.neighbors(node_id))

    def degree(self, node_id: str) -> int:
        """Return the degree of a node."""

        return int(self._graph.degree[node_id])

    def resource_owner(self, resource_id: str) -> str | None:
        """Return the first node that stores a resource, if any."""

        for node in self._nodes.values():
            if node.has_resource(resource_id):
                return node.node_id
        return None

    def resources_for(self, node_id: str) -> frozenset[str]:
        """Return resources stored by a node."""

        return self.get_node(node_id).resources

    @classmethod
    def from_data(
        cls,
        resources: Mapping[str, Iterable[str]],
        edges: Iterable[tuple[str, str]],
    ) -> P2PNetwork:
        """Build a network from resource mapping and edges."""

        network = cls()
        for node_id, node_resources in resources.items():
            network.add_node(Node(node_id=node_id, resources=frozenset(node_resources)))
        for node_a, node_b in edges:
            network.add_edge(node_a, node_b)
        return network
