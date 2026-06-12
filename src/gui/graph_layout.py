"""Helpers for drawing P2P networks in the graphical interface."""

from __future__ import annotations

from collections.abc import Mapping


Point = tuple[float, float]


def edge_key(node_a: str, node_b: str) -> tuple[str, str]:
    """Return a stable key for an undirected edge."""

    left, right = sorted((node_a, node_b))
    return left, right


def scale_positions(
    positions: Mapping[str, Point],
    width: int,
    height: int,
    margin: int = 48,
) -> dict[str, Point]:
    """Scale normalized graph positions to canvas coordinates."""

    if not positions:
        return {}

    min_x = min(point[0] for point in positions.values())
    max_x = max(point[0] for point in positions.values())
    min_y = min(point[1] for point in positions.values())
    max_y = max(point[1] for point in positions.values())
    span_x = max(max_x - min_x, 1.0)
    span_y = max(max_y - min_y, 1.0)
    drawable_width = max(width - (2 * margin), 1)
    drawable_height = max(height - (2 * margin), 1)

    return {
        node_id: (
            margin + ((point[0] - min_x) / span_x) * drawable_width,
            margin + ((point[1] - min_y) / span_y) * drawable_height,
        )
        for node_id, point in positions.items()
    }
