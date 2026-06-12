from __future__ import annotations

import random

from src.algorithms.flooding import Flooding
from src.algorithms.informed_flooding import InformedFlooding
from src.algorithms.informed_random_walk import InformedRandomWalk
from src.algorithms.random_walk import RandomWalk
from src.config.loader import ConfigLoader
from src.network.network import P2PNetwork
from src.simulation.search_simulator import SearchSimulator


def line_network() -> P2PNetwork:
    config = ConfigLoader.from_dict(
        {
            "num_nodes": 4,
            "min_neighbors": 1,
            "max_neighbors": 2,
            "resources": {
                "n1": ["r1"],
                "n2": ["r2"],
                "n3": ["r3"],
                "n4": ["r4"],
            },
            "edges": [["n1", "n2"], ["n2", "n3"], ["n3", "n4"]],
        }
    )
    return config.to_network()


def branching_network() -> P2PNetwork:
    config = ConfigLoader.from_dict(
        {
            "num_nodes": 6,
            "min_neighbors": 1,
            "max_neighbors": 3,
            "resources": {
                "n1": ["r1"],
                "n2": ["r2"],
                "n3": ["target"],
                "n4": ["r4"],
                "n5": ["r5"],
                "n6": ["r6"],
            },
            "edges": [
                ["n1", "n2"],
                ["n1", "n3"],
                ["n1", "n4"],
                ["n2", "n5"],
                ["n4", "n6"],
            ],
        }
    )
    return config.to_network()


def test_flooding_finds_resource_within_ttl() -> None:
    result = Flooding().search(line_network(), "n1", "r4", ttl=3)

    assert result.resource_found is True
    assert result.found is True
    assert result.resource_owner == "n4"
    assert result.total_messages == 3
    assert result.total_nodes_involved == 4
    assert any(event.event == "found" and event.node_id == "n4" for event in result.trace)


def test_flooding_fails_when_ttl_is_too_small() -> None:
    result = Flooding().search(line_network(), "n1", "r4", ttl=2)

    assert result.resource_found is False
    assert result.resource_owner is None


def test_flooding_continues_other_branches_after_resource_is_found() -> None:
    result = Flooding().search(branching_network(), "n1", "target", ttl=2)

    assert result.resource_found is True
    assert result.resource_owner == "n3"
    assert any(event.event == "found" and event.node_id == "n3" for event in result.trace)
    assert any(event.event == "send" and event.to_node == "n6" for event in result.trace)
    assert result.total_messages == 5


def test_flooding_ttl_one_stops_at_first_layer() -> None:
    result = Flooding().search(branching_network(), "n1", "r5", ttl=1)

    assert result.resource_found is False
    assert {event.to_node for event in result.trace if event.event == "send"} == {"n2", "n3", "n4"}


def test_random_walk_is_reproducible_with_seeded_rng() -> None:
    simulator_a = SearchSimulator(line_network(), seed=7)
    simulator_b = SearchSimulator(line_network(), seed=7)

    result_a = simulator_a.run("n1", "r4", ttl=3, algo="random_walk")
    result_b = simulator_b.run("n1", "r4", ttl=3, algo="random_walk")

    assert result_a == result_b


def test_random_walk_finds_resource_on_line() -> None:
    result = RandomWalk().search(line_network(), "n1", "r4", ttl=3)

    assert result.resource_found is True
    assert result.resource_owner == "n4"


def test_random_walk_backtracks_and_finds_resource_within_ttl() -> None:
    for seed in range(10):
        result = RandomWalk(random.Random(seed)).search(branching_network(), "n1", "target", ttl=1)

        assert result.resource_found is True
        assert result.resource_owner == "n3"
        assert result.total_messages >= 1


def test_informed_flooding_uses_cache_after_learning() -> None:
    network = line_network()
    algorithm = InformedFlooding()

    first = algorithm.search(network, "n1", "r4", ttl=3)
    second = algorithm.search(network, "n1", "r4", ttl=3)

    assert first.resource_found is True
    assert second.resource_found is True
    assert second.total_messages <= first.total_messages


def test_informed_random_walk_uses_learned_cache() -> None:
    network = line_network()
    algorithm = InformedRandomWalk()

    algorithm.search(network, "n1", "r4", ttl=3)
    result = algorithm.search(network, "n1", "r4", ttl=3)

    assert result.resource_found is True
    assert result.resource_owner == "n4"


def test_simulator_rejects_invalid_parameters() -> None:
    simulator = SearchSimulator(line_network(), seed=1)

    try:
        simulator.run("nx", "r1", ttl=1, algo="flooding")
    except ValueError as error:
        assert "node_id inexistente" in str(error)
    else:
        raise AssertionError("expected invalid node error")
