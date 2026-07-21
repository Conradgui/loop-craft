# Loop Craft Core Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build the first deterministic Loop Craft Core path from an accepted Behavior Contract plus Loop Semantic IR to a validated target Skill, Evidence Package, Build Manifest, Source Map, and drift report.

**Architecture:** Keep all production code inside the installable loop-craft Skill under scripts/loopcraft_core. Validate a language-neutral JSON definition, compile it deterministically into Final Execution IR, then fan out in parallel to the Codex Skill Adapter and Evidence Packager. Tests import and exercise the exact code that will ship inside the Skill.

**Tech Stack:** Python 3.12+ reference implementation, Python standard library, jsonschema 4.x, pytest 8/9, JSON Schema Draft 2020-12, Codex Skill folder format.

---

## Scope

This plan implements only the approved Core vertical slice:

~~~text
Accepted Definition
→ Schema Validation
→ Semantic Validation
→ Deterministic Compiler
→ Final Execution IR
├─ Codex Skill Adapter
├─ Evidence Packager
└─ Build Manifest + Source Map + Drift Verification
~~~

It does not implement the three conversational entries, Runtime execution, Execution Override, Subloop execution, Registry, Library Edition, publication, or multi-platform adapters.

The input contract in this plan is the explicit core-slice-v0.1 implementation Profile. It accepts exactly one Loop and intentionally omits full Semantic IR fields such as state, risk, maturity, extensions, and Runtime policy. Passing this slice proves the shared compiler path only; it must not be reported as complete 0..n Loop or complete Semantic IR support.

## Execution Prerequisites

These actions are not performed while writing this plan. Before implementation, present them as an operation list and obtain approval:

1. Initialize the Loopcraft开发 directory as a Git repository.
2. Decide whether to rename the current local folder from loopcraft to Loopcraft开发; do not rename it implicitly.
3. Create an isolated implementation branch or worktree.
4. Confirm use of the existing environment: Python 3.13, pytest 9.0.3, and jsonschema 4.26.0, compatible with the Python 3.12+ target.
5. Do not clone, vendor, or install external repositories unless a separate copy/install list is approved.

## File Map

~~~text
pyproject.toml
loop-craft/
├─ SKILL.md
├─ agents/openai.yaml
├─ references/core-build.md
└─ scripts/
   ├─ build_loop.py
   └─ loopcraft_core/
      ├─ __init__.py
      ├─ canonical.py
      ├─ validation.py
      ├─ compiler.py
      ├─ pipeline.py
      ├─ kernel/
      │  ├─ __init__.py
      │  └─ schemas/accepted-definition.schema.json
      ├─ adapters/
      │  ├─ __init__.py
      │  └─ codex_skill.py
      └─ evidence/
         ├─ __init__.py
         └─ package.py
tests/
├─ conftest.py
├─ fixtures/accepted-definition.valid.json
├─ unit/
│  ├─ test_canonical.py
│  ├─ test_validation.py
│  ├─ test_compiler.py
│  ├─ test_codex_skill_adapter.py
│  ├─ test_evidence_package.py
│  └─ test_drift.py
└─ integration/
   ├─ test_build_pipeline.py
   └─ test_loop_craft_skill.py
docs/records/2026-07-20-core-vertical-slice-execution.md
~~~

Ownership:

- canonical.py owns byte-stable JSON and SHA-256.
- validation.py owns Schema and Semantic issues.
- compiler.py owns Final Execution IR and compiler Source Map.
- codex_skill.py owns target Skill projection.
- package.py owns Evidence Package and Build Manifest.
- pipeline.py owns sequencing and output isolation.
- build_loop.py is a thin CLI with no domain logic.
- tests import code directly from loop-craft/scripts; there is no duplicate src package.

## Spec Coverage Boundary

This plan implements the deterministic subset of the approved Spec: the product/Core packaging boundary, Accepted Definition schema, semantic validation, Semantic IR to Execution IR compilation, Codex Skill projection, Evidence Package isolation, Build Manifest, Source Map, and drift verification.

The following approved Spec areas are intentionally reserved for separate plans:

- Three entry integration, Candidate extraction, Clarification, and Review Gate: entry-integration plan.
- Definition/Profile/Instance/Run execution state, Capability binding, approvals, Retry, Resume, and Subloop runtime behavior: controlled-runtime plan.
- Typed Execution Override and migration policy: execution-override plan.
- Runtime, Presentation, and additional Packaging Adapters: adapter-conformance plan.
- Importer, Registry, maturity evidence, publication, and Library Edition: lifecycle-and-library plan.

### Task 1: Test Harness and Canonical Serialization

**Files:**
- Create: pyproject.toml
- Create: tests/conftest.py
- Create: tests/unit/test_canonical.py
- Create: loop-craft/scripts/loopcraft_core/__init__.py
- Create: loop-craft/scripts/loopcraft_core/canonical.py

- [ ] **Step 1: Create configuration and the failing test**

~~~toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "loopcraft-development"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["jsonschema>=4.23,<5"]

[project.optional-dependencies]
dev = ["pytest>=8,<10"]

[tool.setuptools]
packages = []

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
~~~

~~~python
# tests/conftest.py
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "loop-craft" / "scripts"))
~~~

~~~python
# tests/unit/test_canonical.py
from loopcraft_core.canonical import canonical_json_bytes, sha256_digest


def test_canonical_json_is_order_independent() -> None:
    left = {"b": 2, "a": {"y": 1, "x": "值"}}
    right = {"a": {"x": "值", "y": 1}, "b": 2}

    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert sha256_digest(left) == sha256_digest(right)


def test_canonical_json_rejects_nan() -> None:
    try:
        canonical_json_bytes({"score": float("nan")})
    except ValueError as error:
        assert "JSON compliant" in str(error)
    else:
        raise AssertionError("NaN must not be accepted")
~~~

- [ ] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_canonical.py -v
~~~

Expected: ModuleNotFoundError for loopcraft_core or loopcraft_core.canonical.

- [ ] **Step 3: Add the minimal implementation**

~~~python
# loop-craft/scripts/loopcraft_core/__init__.py
"""Deterministic Loop Craft Core implementation."""

__version__ = "0.1.0"
~~~

~~~python
# loop-craft/scripts/loopcraft_core/canonical.py
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"Value is not JSON compliant: {error}") from error
    return encoded.encode("utf-8")


def sha256_digest(value: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return f"sha256:{digest}"
~~~

- [ ] **Step 4: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_canonical.py -v
~~~

Expected: 2 passed.

- [ ] **Step 5: Commit**

~~~powershell
git add pyproject.toml tests/conftest.py tests/unit/test_canonical.py loop-craft/scripts/loopcraft_core
git commit -m "test: establish deterministic core serialization"
~~~

### Task 2: Accepted Definition Schema Validation

**Files:**
- Create: loop-craft/scripts/loopcraft_core/kernel/__init__.py
- Create: loop-craft/scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json
- Create: loop-craft/scripts/loopcraft_core/validation.py
- Create: tests/fixtures/accepted-definition.valid.json
- Create: tests/unit/test_validation.py

- [ ] **Step 1: Add the valid fixture**

~~~json
{
  "schema_version": "0.1.0",
  "profile": "core-slice-v0.1",
  "behavior_contract": {
    "identity": {
      "id": "skill-polish-loop",
      "name": "Skill Polish Loop",
      "version": "0.1.0",
      "description": "Improve an existing Agent Skill through bounded evidence-driven repairs."
    },
    "purpose": {
      "outcome": "make the target Skill satisfy its approved behavior contract and validation gates"
    },
    "applicability": {
      "use_when": [
        "an existing Agent Skill needs iterative improvement based on fresh validation evidence"
      ],
      "do_not_use_when": [
        "the request is a single deterministic edit"
      ]
    },
    "interface": {
      "inputs": ["skill_path"],
      "outputs": ["updated_skill", "validation_report"]
    },
    "authority": {
      "allowed": ["read_target", "edit_target", "run_local_validation"],
      "approval_required": ["publish", "modify_outside_target"],
      "forbidden": ["send_external_message"]
    },
    "capabilities": {
      "required": ["filesystem.read", "filesystem.write", "validation.execute"],
      "optional": ["git.diff"]
    }
  },
  "loops": [
    {
      "id": "skill-polish",
      "cycle": {
        "observe": "Read the current Skill and the latest validation evidence.",
        "choose": "Select one material in-scope failure.",
        "act": "Apply one bounded repair.",
        "verify": "Run the approved targeted validation.",
        "record": "Record the repair, evidence, and remaining failures.",
        "adapt": "Use the new evidence to select the next action or stop."
      },
      "terminal_states": {
        "success": "All approved acceptance checks pass.",
        "clean_no_op": "No material failure exists.",
        "blocked": "Required evidence or capability is unavailable.",
        "stagnated": "Fresh evidence no longer changes the next action.",
        "exhausted": "The approved budget is exhausted."
      },
      "invariants": [
        "Preserve unrelated user work.",
        "Do not publish without approval."
      ]
    }
  ]
}
~~~

- [ ] **Step 2: Write failing validation tests**

~~~python
# tests/unit/test_validation.py
import copy
import json
from pathlib import Path

import pytest

from loopcraft_core.validation import DefinitionValidationError, validate_definition

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "accepted-definition.valid.json"


def load_valid() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_valid_definition_passes_validation() -> None:
    validate_definition(load_valid())


def test_missing_behavior_contract_is_rejected() -> None:
    candidate = copy.deepcopy(load_valid())
    candidate.pop("behavior_contract")

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert captured.value.issues[0].code == "schema"
    assert captured.value.issues[0].path == ""


@pytest.mark.parametrize("loop_count", [0, 2])
def test_core_slice_requires_exactly_one_loop(loop_count: int) -> None:
    candidate = copy.deepcopy(load_valid())
    source_loop = copy.deepcopy(candidate["loops"][0])
    candidate["loops"] = [copy.deepcopy(source_loop) for _ in range(loop_count)]

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert any(issue.path == "/loops" for issue in captured.value.issues)
~~~

- [ ] **Step 3: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_validation.py -v
~~~

Expected: import failure because loopcraft_core.validation does not exist.

- [ ] **Step 4: Add the complete initial schema**

~~~json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://loopcraft.local/schemas/accepted-definition.schema.json",
  "title": "Loop Craft Accepted Definition",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "profile", "behavior_contract", "loops"],
  "properties": {
    "schema_version": {"const": "0.1.0"},
    "profile": {"const": "core-slice-v0.1"},
    "behavior_contract": {
      "type": "object",
      "additionalProperties": false,
      "required": ["identity", "purpose", "applicability", "interface", "authority", "capabilities"],
      "properties": {
        "identity": {
          "type": "object",
          "additionalProperties": false,
          "required": ["id", "name", "version", "description"],
          "properties": {
            "id": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
            "name": {"type": "string", "minLength": 1},
            "version": {"type": "string", "pattern": "^0\\.[0-9]+\\.[0-9]+$"},
            "description": {"type": "string", "minLength": 1}
          }
        },
        "purpose": {
          "type": "object",
          "additionalProperties": false,
          "required": ["outcome"],
          "properties": {"outcome": {"type": "string", "minLength": 1}}
        },
        "applicability": {
          "type": "object",
          "additionalProperties": false,
          "required": ["use_when", "do_not_use_when"],
          "properties": {
            "use_when": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
            "do_not_use_when": {"type": "array", "items": {"type": "string", "minLength": 1}}
          }
        },
        "interface": {
          "type": "object",
          "additionalProperties": false,
          "required": ["inputs", "outputs"],
          "properties": {
            "inputs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true},
            "outputs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": true}
          }
        },
        "authority": {
          "type": "object",
          "additionalProperties": false,
          "required": ["allowed", "approval_required", "forbidden"],
          "properties": {
            "allowed": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
            "approval_required": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
            "forbidden": {"type": "array", "items": {"type": "string"}, "uniqueItems": true}
          }
        },
        "capabilities": {
          "type": "object",
          "additionalProperties": false,
          "required": ["required", "optional"],
          "properties": {
            "required": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
            "optional": {"type": "array", "items": {"type": "string"}, "uniqueItems": true}
          }
        }
      }
    },
    "loops": {
      "type": "array",
      "minItems": 1,
      "maxItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "cycle", "terminal_states", "invariants"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
          "cycle": {
            "type": "object",
            "additionalProperties": false,
            "required": ["observe", "choose", "act", "verify", "record", "adapt"],
            "properties": {
              "observe": {"type": "string", "minLength": 1},
              "choose": {"type": "string", "minLength": 1},
              "act": {"type": "string", "minLength": 1},
              "verify": {"type": "string", "minLength": 1},
              "record": {"type": "string", "minLength": 1},
              "adapt": {"type": "string", "minLength": 1}
            }
          },
          "terminal_states": {
            "type": "object",
            "additionalProperties": false,
            "required": ["success", "clean_no_op", "blocked", "stagnated", "exhausted"],
            "properties": {
              "success": {"type": "string", "minLength": 1},
              "clean_no_op": {"type": "string", "minLength": 1},
              "blocked": {"type": "string", "minLength": 1},
              "stagnated": {"type": "string", "minLength": 1},
              "exhausted": {"type": "string", "minLength": 1}
            }
          },
          "invariants": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}
        }
      }
    }
  }
}
~~~

- [ ] **Step 5: Implement structured schema validation**

~~~python
# loop-craft/scripts/loopcraft_core/kernel/__init__.py
"""Platform-independent Loop Craft contracts and schemas."""
~~~

~~~python
# loop-craft/scripts/loopcraft_core/validation.py
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


class DefinitionValidationError(ValueError):
    def __init__(self, issues: tuple[ValidationIssue, ...]) -> None:
        self.issues = issues
        summary = "; ".join(f"{item.code} {item.path}: {item.message}" for item in issues)
        super().__init__(summary)


SCHEMA_PATH = Path(__file__).resolve().parent / "kernel" / "schemas" / "accepted-definition.schema.json"


def _json_pointer(parts: list[Any]) -> str:
    if not parts:
        return ""
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped)


def schema_issues(definition: dict[str, Any]) -> tuple[ValidationIssue, ...]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(definition),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    return tuple(
        ValidationIssue("schema", _json_pointer(list(error.absolute_path)), error.message)
        for error in errors
    )


def validate_definition(definition: dict[str, Any]) -> None:
    issues = schema_issues(definition)
    if issues:
        raise DefinitionValidationError(issues)
~~~

- [ ] **Step 6: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_validation.py -v
~~~

Expected: all Task 2 validation tests pass, including the original valid and invalid cases plus the hardening regressions.

**Quality hardening amendment:** Before accepting this task, validation must also
reject non-canonical JSON values (including isolated Unicode surrogates), control
characters that can bypass slug/version boundaries, blank or whitespace-only
free-text and authority/capability items, and Skill IDs longer than 64 characters.
Validation issue paths use RFC 6901 JSON Pointers, so the document root is the
empty string. Add regression tests for these boundaries and keep the one-Loop
Profile unchanged.

- [ ] **Step 7: Commit**

~~~powershell
git add loop-craft/scripts/loopcraft_core/kernel loop-craft/scripts/loopcraft_core/validation.py tests/fixtures tests/unit/test_validation.py
git commit -m "feat: validate accepted loop definitions"
~~~

### Task 3: Semantic Validation

**Files:**
- Modify: loop-craft/scripts/loopcraft_core/validation.py
- Modify: tests/unit/test_validation.py

- [ ] **Step 1: Add failing semantic and ordering tests**

~~~python
@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("allowed", "approval_required"),
        ("allowed", "forbidden"),
        ("approval_required", "forbidden"),
    ],
)
def test_authority_categories_must_not_overlap(left: str, right: str) -> None:
    candidate = copy.deepcopy(load_valid())
    authority = candidate["behavior_contract"]["authority"]
    conflict = authority[left][0]
    authority[right].append(conflict)

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    overlap_issues = [
        issue for issue in captured.value.issues
        if issue.code == "authority_overlap"
    ]
    assert len(overlap_issues) == 1
    assert overlap_issues[0].path == "/behavior_contract/authority"


def test_non_canonical_authority_overlap_is_reported_before_semantics() -> None:
    candidate = copy.deepcopy(load_valid())
    authority = candidate["behavior_contract"]["authority"]
    authority["allowed"].append("\ud800")
    authority["forbidden"].append("\ud800")

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert captured.value.issues[0].code == "non_canonical_json"
    assert captured.value.issues[0].path == ""
~~~

- [ ] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_validation.py -v
~~~

Expected: the authority-overlap cases fail before semantic validation exists; the combined surrogate + overlap regression fails until canonical validation runs before semantic formatting.

- [ ] **Step 3: Implement semantic validation**

Add before validate_definition:

~~~python
def semantic_issues(definition: dict[str, Any]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    authority = definition["behavior_contract"]["authority"]
    categories = {
        name: set(authority[name])
        for name in ("allowed", "approval_required", "forbidden")
    }
    for left, right in (
        ("allowed", "approval_required"),
        ("allowed", "forbidden"),
        ("approval_required", "forbidden"),
    ):
        overlap = sorted(categories[left] & categories[right])
        if overlap:
            issues.append(
                ValidationIssue(
                    "authority_overlap",
                    "/behavior_contract/authority",
                    f"{left} and {right} overlap: {', '.join(overlap)}",
                )
            )
    return tuple(issues)
~~~

Keep the current Profile boundary explicit: `core-slice-v0.1` accepts exactly one Loop, so this task does not add a `duplicate_loop_id` semantic rule.

Replace validate_definition so the validation layers run in this fixed order:

~~~python
def validate_definition(definition: dict[str, Any]) -> None:
    issues = schema_issues(definition)
    if issues:
        raise DefinitionValidationError(issues)

    try:
        canonical_json_bytes(definition)
    except ValueError as exc:
        raise DefinitionValidationError(
            (
                ValidationIssue(
                    code="non_canonical_json",
                    path="",
                    message=str(exc),
                ),
            )
        ) from exc

    issues = semantic_issues(definition)
    if issues:
        raise DefinitionValidationError(issues)
~~~

- [ ] **Step 4: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_validation.py -v
python -m pytest tests/unit/test_validation.py tests/unit/test_canonical.py -q
python -m pytest -q
~~~

Expected: all validation tests pass, including all three authority category pairs, the surrogate + authority overlap ordering regression, and the Task 2 hardening regressions. The combined validation + canonical run and the full current suite must both report 25 passed.

- [ ] **Step 5: Commit implementation and review fix**

~~~powershell
git add loop-craft/scripts/loopcraft_core/validation.py tests/unit/test_validation.py
git commit -m "feat: reject contradictory authority semantics"

# If review finds semantic validation preceding canonical validation:
git add loop-craft/scripts/loopcraft_core/validation.py tests/unit/test_validation.py
git commit -m "fix: validate canonical input before semantic checks"
~~~

### Task 4: Deterministic Compiler and Source Map

**Task 4 预检修订（执行门槛）：**

- 用递归字典键重排证明等价 Accepted Definition 产生相同的 Final Execution IR canonical bytes/digest、`definition_digest` 和 Source Map canonical bytes；不能只比较普通 Python 字典相等。
- `compile_definition` 必须先执行既有 validation，再读取和投影输入；验证通过后使用 `deepcopy` 隔离输入快照，调用方后续修改嵌套字段不得改变编译结果。
- Source Map 必须覆盖根 `definition_digest`、Schema/Profile、Behavior Contract、Loop id/entrypoint、node id/instruction/next、terminal mapping 和 invariants。
- `compiler_version` 是编译器生成元数据，不来自 Semantic IR，因此不得伪造 source mapping。Task 4 不实现 Adapter、Evidence、Runtime 或 Pipeline。

**Files:**
- Create: loop-craft/scripts/loopcraft_core/compiler.py
- Create: tests/unit/test_compiler.py

- [ ] **Step 1: Write failing compiler tests**

~~~python
# tests/unit/test_compiler.py
import json
from pathlib import Path
from typing import Any

import pytest

from loopcraft_core.canonical import canonical_json_bytes, sha256_digest
from loopcraft_core.compiler import compile_definition
from loopcraft_core.validation import DefinitionValidationError

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)
CYCLE_ORDER = ("observe", "choose", "act", "verify", "record", "adapt")


def load_valid() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def reverse_mapping_order(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: reverse_mapping_order(item)
            for key, item in reversed(tuple(value.items()))
        }
    if isinstance(value, list):
        return [reverse_mapping_order(item) for item in value]
    return value


def test_compiler_is_canonically_deterministic_for_equivalent_definitions() -> None:
    definition = load_valid()
    reordered_definition = reverse_mapping_order(definition)

    first = compile_definition(definition)
    second = compile_definition(reordered_definition)

    assert canonical_json_bytes(first.final_execution_ir) == canonical_json_bytes(
        second.final_execution_ir
    )
    assert sha256_digest(first.final_execution_ir) == sha256_digest(
        second.final_execution_ir
    )
    assert first.final_execution_ir["definition_digest"] == second.final_execution_ir[
        "definition_digest"
    ]
    assert canonical_json_bytes(first.source_map) == canonical_json_bytes(
        second.source_map
    )


def test_compiler_maps_cycle_in_fixed_order() -> None:
    result = compile_definition(load_valid())
    nodes = result.final_execution_ir["loops"][0]["nodes"]

    assert [node["id"] for node in nodes] == list(CYCLE_ORDER)
    assert [node["next"] for node in nodes] == [
        "choose",
        "act",
        "verify",
        "record",
        "adapt",
        "observe",
    ]


def test_source_map_covers_all_critical_core_slice_fields() -> None:
    result = compile_definition(load_valid())
    source_map = result.source_map

    assert source_map["/schema_version"] == ["/schema_version"]
    assert source_map["/input_profile"] == ["/profile"]
    assert source_map["/definition_digest"] == [""]
    for field in (
        "identity",
        "purpose",
        "applicability",
        "interface",
        "authority",
        "capabilities",
    ):
        assert source_map[f"/{field}"] == [f"/behavior_contract/{field}"]

    assert source_map["/loops/0/id"] == ["/loops/0/id"]
    assert source_map["/loops/0/entrypoint"] == ["/loops/0/cycle/observe"]
    for node_index, node_id in enumerate(CYCLE_ORDER):
        next_id = CYCLE_ORDER[(node_index + 1) % len(CYCLE_ORDER)]
        output_path = f"/loops/0/nodes/{node_index}"
        assert source_map[f"{output_path}/id"] == [
            f"/loops/0/cycle/{node_id}"
        ]
        assert source_map[f"{output_path}/instruction"] == [
            f"/loops/0/cycle/{node_id}"
        ]
        assert source_map[f"{output_path}/next"] == [
            f"/loops/0/cycle/{next_id}"
        ]

    assert source_map["/loops/0/terminal_mapping"] == [
        "/loops/0/terminal_states"
    ]
    assert source_map["/loops/0/invariants"] == ["/loops/0/invariants"]
    assert "/compiler_version" not in source_map


def test_compiler_result_does_not_alias_the_input_definition() -> None:
    definition = load_valid()
    result = compile_definition(definition)
    original_ir_bytes = canonical_json_bytes(result.final_execution_ir)
    original_ir_digest = sha256_digest(result.final_execution_ir)
    original_source_map_bytes = canonical_json_bytes(result.source_map)
    original_definition_digest = result.final_execution_ir["definition_digest"]

    definition["behavior_contract"]["identity"]["name"] = "Changed"
    definition["behavior_contract"]["capabilities"]["required"].append(
        "network.write"
    )
    definition["loops"][0]["terminal_states"]["success"] = "Changed"
    definition["loops"][0]["invariants"].append("Changed")

    assert canonical_json_bytes(result.final_execution_ir) == original_ir_bytes
    assert canonical_json_bytes(result.source_map) == original_source_map_bytes
    assert result.final_execution_ir["definition_digest"] == original_definition_digest
    assert sha256_digest(result.final_execution_ir) == original_ir_digest


def test_compiler_validates_before_projecting_the_definition() -> None:
    definition = load_valid()
    definition.pop("behavior_contract")

    with pytest.raises(DefinitionValidationError):
        compile_definition(definition)
~~~

- [ ] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_compiler.py -v
~~~

Expected: import failure because loopcraft_core.compiler does not exist.

- [ ] **Step 3: Implement the compiler**

~~~python
# loop-craft/scripts/loopcraft_core/compiler.py
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
            source_map[f"{output_node_path}/next"] = [
                f"{cycle_path}/{next_id}"
            ]

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
~~~

- [ ] **Step 4: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_compiler.py -v
~~~

Expected: 5 passed.

- [ ] **Step 5: Commit**

~~~powershell
git add loop-craft/scripts/loopcraft_core/compiler.py tests/unit/test_compiler.py
git commit -m "feat: compile accepted definitions deterministically"
~~~

### Task 5: Codex Skill Adapter

**Task 5 预检修订（执行门槛）：**

- Adapter 只负责把 Final Execution IR 投影为目标 Codex Skill；产物限定为 `SKILL.md`、`agents/openai.yaml` 和 `references/final-execution-ir.json`。Evidence Package、Runtime、Loop Library 和 Library Edition 不属于本任务。
- 所有进入 Markdown 正文的自由文本必须编码为单行 JSON string literal，使换行、标题、列表等内容保持为数据，不能改变 Markdown 结构。frontmatter description 仍单独执行 quoted YAML、`<`/`>` 移除和 1024 字符限制。JSON literal 保留 `<...>` 不等于通用 HTML sanitization。
- `directory_digest` 必须按 POSIX 相对路径排序，并以 `8-byte big-endian path length + path bytes + 8-byte big-endian content length + content bytes` 更新 SHA-256；不得再用 NUL delimiter 作为边界。
- coarse `SKILL.md#workflow` Source Map 必须覆盖每个 Loop 的 `id`、`entrypoint`、`nodes`、`terminal_mapping` 和 `invariants`，同时保留逐字段细粒度映射。
- 生成的 Skill 必须明确 terminal stop rule：任一 terminal condition 满足时立即停止，terminal outcome 优先于任何 node 的 `Next` 转移。
- 本任务验收矩阵固定为 8 个 Adapter 单元测试；Task 5 仍不得扩大为 Evidence、Pipeline 或阶段出口验收。

**Files:**
- Create: loop-craft/scripts/loopcraft_core/adapters/__init__.py
- Create: loop-craft/scripts/loopcraft_core/adapters/codex_skill.py
- Create: tests/unit/test_codex_skill_adapter.py

- [ ] **Step 1: Write the eight failing adapter tests**

~~~python
# tests/unit/test_codex_skill_adapter.py
import json
from pathlib import Path

from loopcraft_core.adapters.codex_skill import render_codex_skill
from loopcraft_core.compiler import compile_definition

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "accepted-definition.valid.json"


def test_adapter_generates_clean_complete_skill(tmp_path: Path) -> None:
    definition = json.loads(FIXTURE.read_text(encoding="utf-8"))
    compiled = compile_definition(definition)
    result = render_codex_skill(compiled, tmp_path)

    files = sorted(
        path.relative_to(result.skill_dir).as_posix()
        for path in result.skill_dir.rglob("*")
        if path.is_file()
    )
    assert files == [
        "SKILL.md",
        "agents/openai.yaml",
        "references/final-execution-ir.json",
    ]

    skill_text = (result.skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "name: skill-polish-loop" in skill_text
    assert "Use when an existing Agent Skill" in skill_text
    assert "Loopy" not in skill_text
    assert "Loop Library" not in skill_text
    assert result.source_map["SKILL.md#workflow"] == [
        "/loops/0/nodes",
        "/loops/0/terminal_mapping",
    ]


def test_adapter_is_deterministic_for_equivalent_terminal_key_order(tmp_path: Path) -> None:
    definition = json.loads(FIXTURE.read_text(encoding="utf-8"))
    reordered = json.loads(FIXTURE.read_text(encoding="utf-8"))
    terminal_states = reordered["loops"][0]["terminal_states"]
    reordered["loops"][0]["terminal_states"] = dict(reversed(list(terminal_states.items())))

    first = render_codex_skill(compile_definition(definition), tmp_path / "first")
    second = render_codex_skill(compile_definition(reordered), tmp_path / "second")

    assert first.artifact_digest == second.artifact_digest
    assert (first.skill_dir / "SKILL.md").read_bytes() == (
        second.skill_dir / "SKILL.md"
    ).read_bytes()


def test_adapter_quotes_and_preserves_rich_applicability_metadata(tmp_path: Path) -> None:
    definition = json.loads(FIXTURE.read_text(encoding="utf-8"))
    definition["behavior_contract"]["applicability"]["use_when"] = [
        "an input: value <must> be checked"
    ]
    definition["behavior_contract"]["applicability"]["do_not_use_when"] = [
        "the request is already complete"
    ]

    result = render_codex_skill(
        compile_definition(definition), tmp_path / "rich-applicability"
    )
    skill_text = (result.skill_dir / "SKILL.md").read_text(encoding="utf-8")

    assert 'description: "Use when an input: value must be checked"' in skill_text
    assert "an input: value <must> be checked" in skill_text
    assert "the request is already complete" in skill_text
    assert result.source_map["SKILL.md#applicability"] == [
        "/applicability/use_when/0",
        "/applicability/do_not_use_when/0",
    ]
    assert result.source_map["SKILL.md#authority"] == ["/authority"]
    assert result.source_map["SKILL.md#capabilities"] == ["/capabilities"]
    assert result.source_map["SKILL.md#invariants"] == ["/loops/0/invariants"]
~~~

The eight-test matrix must cover:

1. Only the three clean target Skill files are emitted; all projected fields and the terminal stop rule are present.
2. Frontmatter is quoted/bounded while rich applicability text is preserved in the body.
3. Multiline Markdown injection payloads remain single-line JSON literals and do not create headings or list items.
4. Adapter Source Map deep-copies the compiler map and covers coarse plus fine-grained projections, including workflow `id`/`entrypoint`/`nodes`/`terminal_mapping`/`invariants`.
5. Recursively reordered input objects produce byte-identical Skill files and the same artifact digest.
6. Directory digest matches sorted POSIX relative paths and file bytes with length-prefixed framing.
7. A fixture that collides under the old NUL-delimited framing does not collide under `directory_digest`.
8. `agents/openai.yaml` contains only deterministic interface values.

- [ ] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_codex_skill_adapter.py -v
~~~

Expected: import failure because the adapter module does not exist.

- [ ] **Step 3: Implement target Skill rendering and the hardened Adapter boundary**

The implementation must satisfy the Task 5 preflight contract above. In particular, render body free text through a shared single-line JSON literal helper, generate coarse and fine Source Map entries, apply the explicit terminal stop rule, and frame directory digest inputs with 8-byte big-endian lengths. The code below is the initial structure; the eight-test matrix is authoritative where the initial structure is incomplete.

~~~python
# loop-craft/scripts/loopcraft_core/adapters/__init__.py
"""Final Execution IR output adapters."""
~~~

~~~python
# loop-craft/scripts/loopcraft_core/adapters/codex_skill.py
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from ..canonical import canonical_json_bytes
from ..compiler import CompileResult


@dataclass(frozen=True)
class SkillArtifact:
    skill_dir: Path
    artifact_digest: str
    source_map: dict[str, list[str]]


def directory_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    files = sorted(
        (path.relative_to(root).as_posix(), path)
        for path in root.rglob("*")
        if path.is_file()
    )
    for relative_path, path in files:
        path_bytes = relative_path.encode("utf-8")
        content = path.read_bytes()
        hasher.update(len(path_bytes).to_bytes(8, "big"))
        hasher.update(path_bytes)
        hasher.update(len(content).to_bytes(8, "big"))
        hasher.update(content)
    return f"sha256:{hasher.hexdigest()}"


def _description(use_when: str) -> str:
    value = use_when.strip().rstrip(".")
    value = value if value.lower().startswith("use when ") else f"Use when {value}"
    return value.replace("<", "").replace(">", "")[:1024].rstrip()


def _markdown_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_codex_skill(compiled: CompileResult, artifact_root: Path) -> SkillArtifact:
    execution = compiled.final_execution_ir
    identity = execution["identity"]
    skill_dir = artifact_root / identity["id"]
    references = skill_dir / "references"
    agents = skill_dir / "agents"
    references.mkdir(parents=True, exist_ok=False)
    agents.mkdir(parents=True, exist_ok=False)

    workflow: list[str] = []
    for loop in execution["loops"]:
        workflow.extend([f"## {loop['id']}", ""])
        for index, node in enumerate(loop["nodes"], start=1):
            workflow.append(
                f"{index}. **{node['id'].title()}:** "
                + _markdown_literal(node["instruction"])
            )
        workflow.extend(
            [
                "",
                "Stop immediately when any terminal condition is met; the terminal outcome takes precedence over every node's Next transition.",
                "",
                "Stop according to these outcomes:",
            ]
        )
        for name in sorted(loop["terminal_mapping"]):
            condition = _markdown_literal(loop["terminal_mapping"][name])
            workflow.append(f"- **{name}:** {condition}")
        workflow.append("")

    applicability = execution["applicability"]
    applicability_lines = ["## Applicability", "", "Use when:"]
    applicability_lines.extend(f"- {item}" for item in applicability["use_when"])
    if applicability["do_not_use_when"]:
        applicability_lines.extend(["", "Do not use when:"])
        applicability_lines.extend(
            f"- {item}" for item in applicability["do_not_use_when"]
        )

    authority = execution["authority"]
    authority_lines = [
        "## Authority",
        "",
        f"- Allowed: {', '.join(authority['allowed']) or 'none'}",
        f"- Approval required: {', '.join(authority['approval_required']) or 'none'}",
        f"- Forbidden: {', '.join(authority['forbidden']) or 'none'}",
    ]

    capabilities = execution["capabilities"]
    capability_lines = [
        "## Capabilities",
        "",
        f"- Required: {', '.join(capabilities['required']) or 'none'}",
        f"- Optional: {', '.join(capabilities['optional']) or 'none'}",
    ]

    invariant_lines = ["## Invariants", ""]
    for loop in execution["loops"]:
        invariant_lines.extend(f"- {item}" for item in loop["invariants"])

    skill_text = "\n".join(
        [
            "---",
            f"name: {identity['id']}",
            "description: "
            + json.dumps(
                _description(execution["applicability"]["use_when"][0]),
                ensure_ascii=False,
            ),
            "---",
            "",
            f"# {identity['name']}",
            "",
            identity["description"],
            "",
            *applicability_lines,
            "",
            *workflow,
            *authority_lines,
            "",
            *capability_lines,
            "",
            *invariant_lines,
            "Read references/final-execution-ir.json when exact machine-readable execution details are required.",
            "",
        ]
    )
    (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")

    default_prompt = "Use $" + identity["id"] + " to " + execution["purpose"]["outcome"] + "."
    openai_yaml = "\n".join(
        [
            "interface:",
            f"  display_name: {json.dumps(identity['name'], ensure_ascii=False)}",
            "  short_description: " + json.dumps(identity["description"][:64], ensure_ascii=False),
            "  default_prompt: " + json.dumps(default_prompt, ensure_ascii=False),
            "",
        ]
    )
    (agents / "openai.yaml").write_text(openai_yaml, encoding="utf-8")
    (references / "final-execution-ir.json").write_bytes(
        canonical_json_bytes(execution) + b"\n"
    )

    adapter_map = dict(compiled.source_map)
    adapter_map.update(
        {
            "SKILL.md#description": ["/applicability/use_when/0"],
            "SKILL.md#applicability": [
                *[
                    f"/applicability/use_when/{index}"
                    for index, _ in enumerate(execution["applicability"]["use_when"])
                ],
                *[
                    f"/applicability/do_not_use_when/{index}"
                    for index, _ in enumerate(
                        execution["applicability"]["do_not_use_when"]
                    )
                ],
            ],
            "SKILL.md#workflow": [
                f"/loops/{index}/{field}"
                for index, _ in enumerate(execution["loops"])
                for field in (
                    "id",
                    "entrypoint",
                    "nodes",
                    "terminal_mapping",
                    "invariants",
                )
            ],
            "SKILL.md#authority": ["/authority"],
            "SKILL.md#capabilities": ["/capabilities"],
            "SKILL.md#invariants": [
                f"/loops/{index}/invariants"
                for index, _ in enumerate(execution["loops"])
            ],
            "agents/openai.yaml#display_name": ["/identity/name"],
            "agents/openai.yaml#short_description": ["/identity/description"],
            "agents/openai.yaml#default_prompt": ["/purpose/outcome"],
        }
    )
    return SkillArtifact(skill_dir, directory_digest(skill_dir), adapter_map)
~~~

- [ ] **Step 4: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_codex_skill_adapter.py -v
~~~

Expected: 8 passed.

- [ ] **Step 5: Run the official structural validator**

Run after generating the fixture into build/adapter-check:

~~~powershell
python -c "import json,sys; from pathlib import Path; sys.path.insert(0,'loop-craft/scripts'); from loopcraft_core.compiler import compile_definition; from loopcraft_core.adapters.codex_skill import render_codex_skill; data=json.loads(Path('tests/fixtures/accepted-definition.valid.json').read_text(encoding='utf-8')); render_codex_skill(compile_definition(data), Path('build/adapter-check'))"
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" build/adapter-check/skill-polish-loop
~~~

Expected: validator exits 0.

- [ ] **Step 6: Commit**

~~~powershell
git add loop-craft/scripts/loopcraft_core/adapters tests/unit/test_codex_skill_adapter.py
git commit -m "feat: render target Codex Skills from execution IR"
~~~

### Task 6: Evidence Package and Build Manifest

**Task 6 预检修订（执行门槛）：**

- Evidence Package 与 artifact 必须物理隔离；`evidence_dir` 不得与 artifact 目录相同，也不得互为祖先/后代。
- 固定输出五份 canonical JSON + LF：Accepted Definition、Final Execution IR、Source Map、Validation Report 和 Build Manifest。
- Manifest 必须绑定 definition、完整 core semantic subset、Final Execution IR、Profile、Adapter 与当前 artifact digest，并明确 `override_mode: none`、`override_digest: null`。
- 写入前必须拒绝 definition/Execution IR、artifact/Execution IR、当前 artifact digest 错配和目录关系冲突；所有拒绝都必须发生在 `mkdir` 前，不能留下 Evidence 目录。
- 本任务验收矩阵固定为 6 个 Evidence 单元测试；Evidence Package 不扩大为 Pipeline、双构建、drift 或阶段出口验收。

**Files:**
- Create: loop-craft/scripts/loopcraft_core/evidence/__init__.py
- Create: loop-craft/scripts/loopcraft_core/evidence/package.py
- Create: tests/unit/test_evidence_package.py

- [x] **Step 1: Write the six failing Evidence Package tests**

~~~python
# tests/unit/test_evidence_package.py
import json
from pathlib import Path

from loopcraft_core.adapters.codex_skill import render_codex_skill
from loopcraft_core.canonical import sha256_digest
from loopcraft_core.compiler import compile_definition
from loopcraft_core.evidence.package import package_evidence

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "accepted-definition.valid.json"


def test_evidence_is_separate_and_manifest_binds_artifact(tmp_path: Path) -> None:
    definition = json.loads(FIXTURE.read_text(encoding="utf-8"))
    compiled = compile_definition(definition)
    artifact = render_codex_skill(compiled, tmp_path / "artifact")

    result = package_evidence(
        definition=definition,
        compiled=compiled,
        artifact=artifact,
        evidence_dir=tmp_path / "evidence",
    )

    assert result.evidence_dir != artifact.skill_dir
    manifest = json.loads(
        (result.evidence_dir / "build-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["artifact_digest"] == artifact.artifact_digest
    assert manifest["definition_digest"] == compiled.final_execution_ir["definition_digest"]
    assert manifest["semantic_ir_digest"].startswith("sha256:")
    assert manifest["semantic_ir_digest"] == sha256_digest(
        {
            "schema_version": definition["schema_version"],
            "profile": definition["profile"],
            "behavior_contract": definition["behavior_contract"],
            "loops": definition["loops"],
        }
    )
    assert manifest["override_mode"] == "none"
    assert manifest["override_digest"] is None
    assert sorted(path.name for path in result.evidence_dir.iterdir()) == [
        "accepted-definition.json",
        "build-manifest.json",
        "final-execution-ir.json",
        "source-map.json",
        "validation-report.json",
    ]
~~~

The six-test matrix must cover:

1. Evidence 与 artifact 物理隔离，五份文件均为 canonical JSON + LF，Manifest 完整绑定当前构建。
2. `EvidenceResult` 为 frozen result object。
3. definition 与 compiled Execution IR 不一致时，在创建 Evidence 目录前拒绝。
4. artifact 内嵌 Execution IR 与 compiled Execution IR 不一致时，在创建 Evidence 目录前拒绝。
5. Evidence 与 artifact 目录相同或互为祖先/后代时，在创建 Evidence 目录前拒绝。
6. artifact 当前内容摘要与 Adapter 返回摘要不一致时，在创建 Evidence 目录前拒绝。

- [x] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_evidence_package.py -v
~~~

Recorded RED: 初始 TDD 为 import failure；审查加固的四类 mismatch/path 测试均为 `DID NOT RAISE ValueError`。

- [x] **Step 3: Implement the Evidence Packager and hardened preflight**

The implementation must satisfy the Task 6 preflight contract above. Validate all cross-object digests and resolved directory relationships before `mkdir`; the six-test matrix is authoritative.

~~~python
# loop-craft/scripts/loopcraft_core/evidence/__init__.py
"""Audit and rebuild evidence packaging."""
~~~

~~~python
# loop-craft/scripts/loopcraft_core/evidence/package.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.codex_skill import SkillArtifact, directory_digest
from ..canonical import canonical_json_bytes, sha256_digest
from ..compiler import CompileResult


@dataclass(frozen=True)
class EvidenceResult:
    evidence_dir: Path
    manifest: dict[str, Any]


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _validate_inputs(
    *,
    definition: dict[str, Any],
    compiled: CompileResult,
    artifact: SkillArtifact,
    evidence_dir: Path,
) -> None:
    execution_ir = compiled.final_execution_ir
    if execution_ir.get("definition_digest") != sha256_digest(definition):
        raise ValueError("definition does not match compiled execution IR")

    artifact_dir = artifact.skill_dir.resolve()
    resolved_evidence_dir = evidence_dir.resolve()
    if (
        resolved_evidence_dir == artifact_dir
        or resolved_evidence_dir in artifact_dir.parents
        or artifact_dir in resolved_evidence_dir.parents
    ):
        raise ValueError(
            "evidence directory must be physically separate from artifact"
        )

    execution_ir_path = artifact.skill_dir / "references" / "final-execution-ir.json"
    try:
        artifact_execution_ir = execution_ir_path.read_bytes()
    except OSError as exc:
        raise ValueError("artifact execution IR reference is unavailable") from exc
    if artifact_execution_ir != canonical_json_bytes(execution_ir) + b"\n":
        raise ValueError("artifact execution IR does not match compiled execution IR")

    if directory_digest(artifact.skill_dir) != artifact.artifact_digest:
        raise ValueError("artifact digest does not match current artifact contents")


def package_evidence(
    *,
    definition: dict[str, Any],
    compiled: CompileResult,
    artifact: SkillArtifact,
    evidence_dir: Path,
) -> EvidenceResult:
    _validate_inputs(
        definition=definition,
        compiled=compiled,
        artifact=artifact,
        evidence_dir=evidence_dir,
    )
    evidence_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": "0.1.0",
        "definition_digest": sha256_digest(definition),
        "semantic_ir_digest": sha256_digest(
            {
                "schema_version": definition["schema_version"],
                "profile": definition["profile"],
                "behavior_contract": definition["behavior_contract"],
                "loops": definition["loops"],
            }
        ),
        "execution_ir_digest": sha256_digest(compiled.final_execution_ir),
        "override_mode": "none",
        "override_digest": None,
        "compiler_version": compiled.final_execution_ir["compiler_version"],
        "adapter": "codex-skill",
        "adapter_version": "0.1.0",
        "profile_digest": sha256_digest(
            {"platform": "codex", "profile_version": "0.1.0"}
        ),
        "artifact_digest": artifact.artifact_digest,
    }
    validation_report = {
        "schema_validation": "passed",
        "semantic_validation": "passed",
        "accepted_definition": True,
    }

    _write_json(evidence_dir / "accepted-definition.json", definition)
    _write_json(
        evidence_dir / "final-execution-ir.json",
        compiled.final_execution_ir,
    )
    _write_json(evidence_dir / "source-map.json", artifact.source_map)
    _write_json(evidence_dir / "validation-report.json", validation_report)
    _write_json(evidence_dir / "build-manifest.json", manifest)
    return EvidenceResult(evidence_dir, manifest)
~~~

- [x] **Step 4: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_evidence_package.py -v
~~~

Expected: 6 passed.

- [x] **Step 5: Commit implementation and review hardening**

~~~powershell
git add loop-craft/scripts/loopcraft_core/evidence tests/unit/test_evidence_package.py
git commit -m "feat: package auditable build evidence"
~~~

Recorded commits: `826f285` (`feat: package auditable build evidence`) and `475b2a4` (`fix: reject inconsistent evidence inputs`).

### Task 7: End-to-End Pipeline and CLI

**Task 7 预检修订（执行门槛）：**

- Pipeline 必须在 `output_root.parent` 内创建 `TemporaryDirectory`，按 Adapter → Evidence 顺序构建，只在全部成功后用 `staging_root.replace(output_root)` 提交正式输出。
- 非法定义和 Adapter 失败不得留下正式 output；已被 dangling symlink 占用的输出路径不得被覆盖，占用判断必须使用 `output_root.exists() or output_root.is_symlink()`。
- 两次构建必须产生 byte-identical 文件树和相同 Manifest；目标输出固定包含 artifact 3 文件、Evidence 5 文件。
- 本任务 CLI 仅接受 `definition`、`output` 两个位置参数；drift/verify 子命令属于 Task 8。
- 本任务验收矩阵固定为 4 个 Pipeline integration tests 加一次真实 CLI smoke；不得扩大为强杀、非本地文件系统原子性或阶段出口验收。

**Files:**
- Create: loop-craft/scripts/loopcraft_core/pipeline.py
- Create: loop-craft/scripts/build_loop.py
- Create: tests/integration/test_build_pipeline.py

- [x] **Step 1: Write the four failing integration tests**

~~~python
# tests/integration/test_build_pipeline.py
import json
from pathlib import Path

import pytest

from loopcraft_core.pipeline import build_definition

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "accepted-definition.valid.json"


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_pipeline_builds_identical_outputs(tmp_path: Path) -> None:
    first = build_definition(FIXTURE, tmp_path / "first")
    second = build_definition(FIXTURE, tmp_path / "second")

    assert first.manifest == second.manifest
    assert file_snapshot(first.output_root) == file_snapshot(second.output_root)
    assert first.artifact_dir.parent.name == "artifact"
    assert first.evidence_dir.name == "evidence"


def test_invalid_input_leaves_no_partial_output(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"schema_version": "0.1.0"}), encoding="utf-8")
    output = tmp_path / "failed-build"

    with pytest.raises(ValueError):
        build_definition(invalid, output)

    assert not output.exists()


def test_adapter_failure_cleans_staging_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import loopcraft_core.pipeline as pipeline

    def fail_adapter(*args: object, **kwargs: object) -> None:
        raise RuntimeError("adapter failed")

    monkeypatch.setattr(pipeline, "render_codex_skill", fail_adapter)
    output = tmp_path / "adapter-failure"

    with pytest.raises(RuntimeError, match="adapter failed"):
        pipeline.build_definition(FIXTURE, output)

    assert not output.exists()
~~~

The four-test matrix must cover deterministic dual builds, invalid definition cleanup, Adapter failure cleanup, and dangling output symlink preservation.

- [x] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/integration/test_build_pipeline.py -v
~~~

Recorded RED: 初始 TDD 为 `ModuleNotFoundError`（`loopcraft_core.pipeline`）；dangling symlink 回归在最终 `replace` 处触发 `PermissionError: [WinError 5]`。

- [x] **Step 3: Implement pipeline sequencing and occupied-path hardening**

~~~python
# loop-craft/scripts/loopcraft_core/pipeline.py
from __future__ import annotations

from dataclasses import dataclass
import json
import tempfile
from pathlib import Path
from typing import Any

from .adapters.codex_skill import render_codex_skill
from .compiler import compile_definition
from .evidence.package import package_evidence
from .validation import validate_definition


@dataclass(frozen=True)
class BuildResult:
    output_root: Path
    artifact_dir: Path
    evidence_dir: Path
    manifest: dict[str, Any]


def build_definition(definition_path: Path, output_root: Path) -> BuildResult:
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    validate_definition(definition)
    compiled = compile_definition(definition)

    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(f"Output already exists: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        dir=output_root.parent,
        prefix=f".{output_root.name}.",
    ) as temporary:
        staging_root = Path(temporary) / "output"
        artifact = render_codex_skill(compiled, staging_root / "artifact")
        evidence = package_evidence(
            definition=definition,
            compiled=compiled,
            artifact=artifact,
            evidence_dir=staging_root / "evidence",
        )
        staging_root.replace(output_root)

    return BuildResult(
        output_root,
        output_root / "artifact" / artifact.skill_dir.name,
        output_root / "evidence",
        evidence.manifest,
    )
~~~

- [x] **Step 4: Add a thin build CLI**

~~~python
# loop-craft/scripts/build_loop.py
from __future__ import annotations

import argparse
from pathlib import Path

from loopcraft_core.pipeline import build_definition


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Loop Skill and Evidence Package."
    )
    parser.add_argument("definition", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_definition(args.definition, args.output)
    print(f"Artifact: {result.artifact_dir}")
    print(f"Evidence: {result.evidence_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
~~~

- [x] **Step 5: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/integration/test_build_pipeline.py -v
~~~

Expected: 4 passed.

- [x] **Step 6: Exercise the CLI**

Run:

~~~powershell
python loop-craft/scripts/build_loop.py tests/fixtures/accepted-definition.valid.json build/core-slice
~~~

Expected: exits 0 and prints artifact and evidence paths.

- [x] **Step 7: Commit implementation and security hardening**

~~~powershell
git add loop-craft/scripts/build_loop.py loop-craft/scripts/loopcraft_core/pipeline.py tests/integration/test_build_pipeline.py
git commit -m "feat: build Skill and evidence in one deterministic pipeline"
~~~

Recorded commits: `8253c24` (`feat: build Skill and evidence in one deterministic pipeline`) and `6d295ab` (`fix: preserve occupied output paths`).

### Task 8: Build Drift Verification

**Files:**
- Modify: loop-craft/scripts/loopcraft_core/pipeline.py
- Replace: loop-craft/scripts/build_loop.py
- Create: tests/unit/test_drift.py

- [ ] **Step 1: Write the failing drift test**

~~~python
# tests/unit/test_drift.py
from pathlib import Path

from loopcraft_core.pipeline import build_definition, verify_build

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "accepted-definition.valid.json"


def test_drift_is_reported_without_overwriting_artifact(tmp_path: Path) -> None:
    result = build_definition(FIXTURE, tmp_path / "build")
    skill_file = result.artifact_dir / "SKILL.md"
    modified = skill_file.read_text(encoding="utf-8") + "\nmanual edit\n"
    skill_file.write_text(modified, encoding="utf-8")

    report = verify_build(result.output_root)

    assert report["status"] == "drifted"
    assert report["expected_artifact_digest"] != report["actual_artifact_digest"]
    assert skill_file.read_text(encoding="utf-8") == modified
~~~

- [ ] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/unit/test_drift.py -v
~~~

Expected: import failure because verify_build does not exist.

- [ ] **Step 3: Implement non-mutating drift verification**

Append to pipeline.py:

~~~python
def verify_build(output_root: Path) -> dict[str, str]:
    from .adapters.codex_skill import directory_digest

    manifest_path = output_root / "evidence" / "build-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact_dirs = [
        path for path in (output_root / "artifact").iterdir()
        if path.is_dir()
    ]
    if len(artifact_dirs) != 1:
        raise ValueError("Expected exactly one generated Skill directory")

    actual = directory_digest(artifact_dirs[0])
    expected = manifest["artifact_digest"]
    return {
        "status": "clean" if actual == expected else "drifted",
        "expected_artifact_digest": expected,
        "actual_artifact_digest": actual,
    }
~~~

- [ ] **Step 4: Replace the CLI with build and verify subcommands**

~~~python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from loopcraft_core.pipeline import build_definition, verify_build


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and verify Loop artifacts."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    build = subcommands.add_parser("build")
    build.add_argument("definition", type=Path)
    build.add_argument("output", type=Path)

    verify = subcommands.add_parser("verify")
    verify.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "build":
        result = build_definition(args.definition, args.output)
        print(f"Artifact: {result.artifact_dir}")
        print(f"Evidence: {result.evidence_dir}")
        return 0

    report = verify_build(args.output)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
~~~

- [ ] **Step 5: Update the Task 7 CLI invocation**

Use:

~~~powershell
python loop-craft/scripts/build_loop.py build tests/fixtures/accepted-definition.valid.json build/core-slice
~~~

- [ ] **Step 6: Verify GREEN**

Run:

~~~powershell
python -m pytest tests/unit/test_drift.py tests/integration/test_build_pipeline.py -v
~~~

Expected: 4 passed (one drift test and the three pipeline tests).

- [ ] **Step 7: Verify clean and drifted CLI behavior**

Run:

~~~powershell
python loop-craft/scripts/build_loop.py build tests/fixtures/accepted-definition.valid.json build/drift-check
python loop-craft/scripts/build_loop.py verify build/drift-check
Add-Content build/drift-check/artifact/skill-polish-loop/SKILL.md "manual edit"
python loop-craft/scripts/build_loop.py verify build/drift-check
~~~

Expected: first verify exits 0 with status clean; second verify exits 1 with status drifted and leaves the modified file unchanged.

- [ ] **Step 8: Commit**

~~~powershell
git add loop-craft/scripts tests/unit/test_drift.py tests/integration/test_build_pipeline.py
git commit -m "feat: report generated artifact drift"
~~~

### Task 9: Package the Core Slice as Loop Craft

**Files:**
- Create: loop-craft/SKILL.md
- Create: loop-craft/agents/openai.yaml
- Create: loop-craft/references/core-build.md
- Create: tests/integration/test_loop_craft_skill.py

- [ ] **Step 1: Write the failing product Skill tests**

~~~python
# tests/integration/test_loop_craft_skill.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "loop-craft"


def test_loop_craft_contains_core_and_no_dev_docs() -> None:
    assert (SKILL / "SKILL.md").is_file()
    assert (SKILL / "agents" / "openai.yaml").is_file()
    assert (SKILL / "references" / "core-build.md").is_file()
    assert (SKILL / "scripts" / "build_loop.py").is_file()
    assert (SKILL / "scripts" / "loopcraft_core").is_dir()
    assert not (SKILL / "README.md").exists()
    assert not (SKILL / "tests").exists()


def test_product_skill_does_not_claim_unimplemented_entries() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "accepted Behavior Contract" in text
    assert "conversation history" not in text
    assert "Loop Library" not in text
    assert "Loopy" not in text
~~~

- [ ] **Step 2: Verify RED**

Run:

~~~powershell
python -m pytest tests/integration/test_loop_craft_skill.py -v
~~~

Expected: tests fail because product Skill metadata does not exist.

- [ ] **Step 3: Create the minimal truthful SKILL.md**

~~~markdown
---
name: loop-craft
description: Use when an approved Behavior Contract and Loop Semantic IR must be validated and compiled into a target Agent Skill with a separate evidence package.
---

# Loop Craft

Compile an accepted Behavior Contract and Loop Semantic IR through the deterministic Loop Craft Core.

## Core build

Read references/core-build.md, then use scripts/build_loop.py to validate, build, and verify the generated artifact.

Do not claim support for conversational entry routes, Runtime execution, publication, or scheduling until those capabilities are implemented and tested.
~~~

- [ ] **Step 4: Create agents/openai.yaml**

~~~yaml
interface:
  display_name: "Loop Craft"
  short_description: "Compile validated Loop Skills and evidence packages"
  default_prompt: "Use $loop-craft to compile an accepted Loop definition into a target Skill and evidence package."
~~~

- [ ] **Step 5: Create references/core-build.md**

~~~~markdown
# Core Build

Use only an accepted JSON definition matching scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json.

Build:

~~~powershell
python scripts/build_loop.py build <definition.json> <new-output-directory>
~~~

The output directory contains two siblings:

- artifact/: the clean target Skill.
- evidence/: the accepted definition, Final Execution IR, Source Map, validation report, and Build Manifest.

Verify drift without modifying the artifact:

~~~powershell
python scripts/build_loop.py verify <output-directory>
~~~

A clean build exits 0. A drifted artifact exits 1 and remains unchanged.
~~~~

- [ ] **Step 6: Run product tests and official validation**

Run:

~~~powershell
python -m pytest tests/integration/test_loop_craft_skill.py -v
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" loop-craft
~~~

Expected: 2 tests pass and the validator exits 0.

- [ ] **Step 7: Commit**

~~~powershell
git add loop-craft/SKILL.md loop-craft/agents/openai.yaml loop-craft/references/core-build.md tests/integration/test_loop_craft_skill.py
git commit -m "feat: package the core slice as Loop Craft"
~~~

### Task 10: Full Verification and Execution Record

**Files:**
- Create after all checks pass: docs/records/2026-07-20-core-vertical-slice-execution.md
- Verify: all files from Tasks 1-9

- [ ] **Step 1: Run the complete test suite**

Run:

~~~powershell
python -m pytest -q
~~~

Expected: all tests pass with no warnings emitted by project code.

- [ ] **Step 2: Build two independent outputs**

Run:

~~~powershell
python loop-craft/scripts/build_loop.py build tests/fixtures/accepted-definition.valid.json build/final-a
python loop-craft/scripts/build_loop.py build tests/fixtures/accepted-definition.valid.json build/final-b
~~~

Expected: both commands exit 0.

- [ ] **Step 3: Validate product and generated Skills**

Run:

~~~powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" loop-craft
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" build/final-a/artifact/skill-polish-loop
~~~

Expected: both validators exit 0.

- [ ] **Step 4: Verify determinism and clean drift status**

Run:

~~~powershell
python loop-craft/scripts/build_loop.py verify build/final-a
python loop-craft/scripts/build_loop.py verify build/final-b
python -c "from pathlib import Path; import hashlib; snap=lambda root:{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}; assert snap(Path('build/final-a')) == snap(Path('build/final-b'))"
~~~

Expected: both reports are clean and the comparison exits 0.

- [ ] **Step 5: Scan generated artifacts for forbidden residue**

Run:

~~~powershell
rg -n -i "loopy|loop library" build/final-a/artifact
if ($LASTEXITCODE -eq 1) { exit 0 }
exit $LASTEXITCODE
~~~

Expected: no matches and final exit code 0.

- [ ] **Step 6: Create the execution record only after all checks pass**

~~~markdown
# Core Vertical Slice Execution Record

> Date: 2026-07-20
> Scope: Accepted Definition to target Skill and Evidence Package

## Commands

- python -m pytest -q
- quick_validate.py on loop-craft
- quick_validate.py on the generated target Skill
- build_loop.py verify on two independent builds
- SHA-256 comparison across both output trees
- residue scan for Loopy and Loop Library in the generated artifact

## Result

All listed commands exited successfully. The two builds were byte-identical, both drift checks reported clean, both Skill folders passed structural validation, and the generated artifact contained no Loopy or Loop Library residue.

## Evidence

- build/final-a/evidence/build-manifest.json
- build/final-a/evidence/source-map.json
- build/final-a/evidence/validation-report.json
- build/final-b/evidence/build-manifest.json

## Boundary

This record supports only the Core vertical slice. It does not claim the three input entries, Runtime, Override, Subloop execution, Library Edition, publication, or scheduling are implemented.
~~~

If any command fails, do not create the record. Fix the corresponding task and rerun the affected gate first.

- [ ] **Step 7: Final commit**

~~~powershell
git add pyproject.toml loop-craft tests docs/records/2026-07-20-core-vertical-slice-execution.md
git commit -m "test: verify the Loop Craft core vertical slice"
~~~

## Plan Self-Review Checklist

- Every production function is introduced after a failing test.
- Tests import the exact code shipped under loop-craft/scripts.
- The generated Skill and Evidence Package are siblings, not nested.
- The compiler owns semantic-to-execution mapping; the Adapter owns platform projection.
- Evidence consumes the artifact digest and Source Map, not the target Skill as a semantic source.
- No task creates Runtime, Library, Registry, Subloop execution, or conversational entry code.
- The product SKILL.md states only the capability implemented by this slice.
- The execution record is written only after observing all passing commands.
