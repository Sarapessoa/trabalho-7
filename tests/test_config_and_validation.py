from __future__ import annotations

import pytest

from src.config.loader import ConfigLoader
from src.validators.network_validator import NetworkValidator


def valid_config_data() -> dict[str, object]:
    return {
        "num_nodes": 3,
        "min_neighbors": 1,
        "max_neighbors": 2,
        "resources": {"n1": ["r1"], "n2": ["r2"], "n3": ["r3"]},
        "edges": [["n1", "n2"], ["n2", "n3"]],
    }


def test_loader_normalizes_network_config() -> None:
    config = ConfigLoader.from_dict(valid_config_data())

    assert config.num_nodes == 3
    assert config.edges == [("n1", "n2"), ("n2", "n3")]
    assert config.to_network().neighbors("n2") == ["n1", "n3"]


def test_validator_accepts_valid_connected_network() -> None:
    config = ConfigLoader.from_dict(valid_config_data())

    NetworkValidator().validate(config)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("edges", [["n1", "n1"], ["n2", "n3"]], "self-loop"),
        ("resources", {"n1": ["r1"], "n2": [], "n3": ["r3"]}, "no sem recursos"),
        ("edges", [["n1", "n2"]], "rede deve ser conectada"),
        ("max_neighbors", 1, "acima de max_neighbors"),
        ("min_neighbors", 2, "abaixo de min_neighbors"),
    ],
)
def test_validator_rejects_invalid_topologies(field: str, value: object, expected: str) -> None:
    data = valid_config_data()
    data[field] = value
    config = ConfigLoader.from_dict(data)

    with pytest.raises(ValueError, match=expected):
        NetworkValidator().validate(config)

