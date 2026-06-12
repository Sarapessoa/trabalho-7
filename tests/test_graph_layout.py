from __future__ import annotations

from src.gui.graph_layout import edge_key, scale_positions


def test_edge_key_is_stable_for_undirected_edges() -> None:
    assert edge_key("n2", "n1") == ("n1", "n2")
    assert edge_key("n1", "n2") == ("n1", "n2")


def test_scale_positions_keeps_points_inside_canvas_margin() -> None:
    scaled = scale_positions(
        positions={"n1": (-1.0, 0.0), "n2": (1.0, 2.0)},
        width=200,
        height=100,
        margin=10,
    )

    assert scaled["n1"] == (10.0, 10.0)
    assert scaled["n2"] == (190.0, 90.0)
