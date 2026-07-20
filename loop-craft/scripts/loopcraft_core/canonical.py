import hashlib
import json


def canonical_json_bytes(value):
    try:
        serialized = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Value is not JSON compliant: {exc}") from exc

    return serialized.encode("utf-8")


def sha256_digest(value):
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return f"sha256:{digest}"
