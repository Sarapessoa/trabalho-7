from __future__ import annotations

from src.algorithms.flooding import Flooding
from src.algorithms.informed_flooding import InformedFlooding
from src.algorithms.informed_random_walk import InformedRandomWalk
from src.algorithms.random_walk import RandomWalk
from src.config.loader import ConfigLoader
from src.simulation.search_simulator import SearchSimulator


def line_network():
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


def test_flooding_finds_resource_within_ttl() -> None:
    result = Flooding().search(line_network(), "n1", "r4", ttl=3)

    assert result.resource_found is True
    assert result.found is True
    assert result.resource_owner == "n4"
    assert result.total_messages == 3
    assert result.total_nodes_involved == 4


def test_flooding_fails_when_ttl_is_too_small() -> None:
    result = Flooding().search(line_network(), "n1", "r4", ttl=2)

    assert result.resource_found is False
    assert result.resource_owner is None


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

