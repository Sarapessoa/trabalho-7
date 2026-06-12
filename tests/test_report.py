from __future__ import annotations

from src.algorithms import SearchResult, TraceEvent
from src.simulation.report import format_search_result


def test_format_search_result_includes_metrics_and_trace() -> None:
    result = SearchResult(
        total_messages=1,
        total_nodes_involved=2,
        resource_found=True,
        found=True,
        resource_owner="n2",
        trace=(
            TraceEvent(
                event="send",
                node_id="n1",
                ttl=1,
                from_node="n1",
                to_node="n2",
                message="n1 mandou mensagem para n2; TTL 1 -> 0",
            ),
        ),
    )

    output = format_search_result(result)

    assert "total_messages: 1" in output
    assert "resource_found: True" in output
    assert "- n1 mandou mensagem para n2; TTL 1 -> 0" in output
