import math

import pytest

from loopcraft_core.canonical import canonical_json_bytes, sha256_digest


def test_canonical_json_and_digest_are_independent_of_mapping_key_order():
    first = {"beta": 2, "alpha": 1, "nested": {"z": False, "a": "value"}}
    second = {"nested": {"a": "value", "z": False}, "alpha": 1, "beta": 2}

    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert sha256_digest(first) == sha256_digest(second)


def test_canonical_json_rejects_nan_as_not_json_compliant():
    with pytest.raises(ValueError, match="JSON compliant"):
        canonical_json_bytes({"value": math.nan})
