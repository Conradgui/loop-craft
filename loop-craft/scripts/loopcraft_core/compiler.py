from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from .canonical import sha256_digest
from .validation import validate_definition


CYCLE_ORDER = ("observe", "choose", "act", "verify", "record", "adapt")
COMPILER_VERSION = "0.1.0"


@dataclass(frozen=True)
class CompileResult:
    final_execution_ir: dict[str, Any]
    source_map: dict[str, list[str]]


def compile_definition(definition: dict[str, Any]) -> CompileResult:
    validate_definition(definition)
    snapshot = copy.deepcopy(definition)
    contract = snapshot["behavior_contract"]
    compiled_loops: list[dict[str, Any]] = []
    source_map: dict[str, list[str]] = {
        "/schema_version": ["/schema_version"],
        "/input_profile": ["/profile"],
        "/definition_digest": [""],
        "/identity": ["/behavior_contract/identity"],
        "/purpose": ["/behavior_contract/purpose"],
        "/applicability": ["/behavior_contract/applicability"],
        "/interface": ["/behavior_contract/interface"],
        "/authority": ["/behavior_contract/authority"],
        "/capabilities": ["/behavior_contract/capabilities"],
    }

    for loop_index, loop in enumerate(snapshot["loops"]):
        nodes: list[dict[str, str]] = []
        cycle_path = f"/loops/{loop_index}/cycle"
        output_loop_path = f"/loops/{loop_index}"

        for node_index, node_id in enumerate(CYCLE_ORDER):
            next_id = CYCLE_ORDER[(node_index + 1) % len(CYCLE_ORDER)]
            nodes.append(
                {
                    "id": node_id,
                    "instruction": loop["cycle"][node_id],
                    "next": next_id,
                }
            )
            output_node_path = f"{output_loop_path}/nodes/{node_index}"
            source_map[f"{output_node_path}/id"] = [f"{cycle_path}/{node_id}"]
            source_map[f"{output_node_path}/instruction"] = [
                f"{cycle_path}/{node_id}"
            ]
            source_map[f"{output_node_path}/next"] = [f"{cycle_path}/{next_id}"]

        compiled_loops.append(
            {
                "id": loop["id"],
                "entrypoint": CYCLE_ORDER[0],
                "nodes": nodes,
                "terminal_mapping": loop["terminal_states"],
                "invariants": loop["invariants"],
            }
        )
        source_map[f"{output_loop_path}/id"] = [f"/loops/{loop_index}/id"]
        source_map[f"{output_loop_path}/entrypoint"] = [
            f"{cycle_path}/{CYCLE_ORDER[0]}"
        ]
        source_map[f"{output_loop_path}/terminal_mapping"] = [
            f"/loops/{loop_index}/terminal_states"
        ]
        source_map[f"{output_loop_path}/invariants"] = [
            f"/loops/{loop_index}/invariants"
        ]

    final_execution_ir = {
        "schema_version": snapshot["schema_version"],
        "compiler_version": COMPILER_VERSION,
        "input_profile": snapshot["profile"],
        "definition_digest": sha256_digest(snapshot),
        "identity": contract["identity"],
        "purpose": contract["purpose"],
        "applicability": contract["applicability"],
        "interface": contract["interface"],
        "authority": contract["authority"],
        "capabilities": contract["capabilities"],
        "loops": compiled_loops,
    }
    return CompileResult(final_execution_ir, source_map)
