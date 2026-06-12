"""Human-readable reports for search executions."""

from __future__ import annotations

from src.algorithms import SearchResult


def format_search_result(result: SearchResult) -> str:
    """Format metrics and trace events for human inspection."""

    lines = [
        "Resultado:",
        f"total_messages: {result.total_messages}",
        f"total_nodes_involved: {result.total_nodes_involved}",
        f"resource_found: {result.resource_found}",
        f"resource_owner: {result.resource_owner}",
        "",
        "Passo a passo:",
    ]
    lines.extend(f"- {event.message}" for event in result.trace)
    return "\n".join(lines)
