import math

import pytest

from loopcraft_core.canonical import canonical_json_bytes, sha256_digest


def test_canonical_json_and_digest_are_independent_of_mapping_key_order():
    first = {"beta": 2, "alpha": 1, "nested": {"z": False, "a": "value"}}
    second = {"nested": {"a": "value", "z": False}, "alpha": 1, "beta": 2}

    assert canonical_json_bytes(first) == (
        '{"alpha":1,"beta":2,"nested":{"a":"value","z":false}}'.encode("utf-8")
    )
    assert sha256_digest(first) == (
        "sha256:ec5c951a4e39b29b0b18c9fe8577facabc069f96ab62ae7851ebffefe253d3e7"
    )
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert sha256_digest(first) == sha256_digest(second)


def test_canonical_json_uses_exact_unicode_wire_format_and_digest():
    payload = {"z": 2, "a": "值"}

    assert canonical_json_bytes(payload) == '{"a":"值","z":2}'.encode("utf-8")
    assert sha256_digest(payload) == (
        "sha256:3a3487c67187dea60f65acb01536f67d77a0a650f5afacd7ca59f516cb38d661"
    )


def test_canonical_json_rejects_nan_as_not_json_compliant():
    with pytest.raises(ValueError, match="JSON compliant"):
        canonical_json_bytes({"value": math.nan})


def test_canonical_json_rejects_unpaired_surrogate_as_not_json_compliant():
    with pytest.raises(ValueError, match="JSON compliant"):
        canonical_json_bytes({"value": "\ud800"})
