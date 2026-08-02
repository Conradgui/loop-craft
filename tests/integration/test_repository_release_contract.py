from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


def test_repository_is_ready_for_a_reproducible_public_release() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in workflow
    assert "workflow_dispatch:" in workflow
    assert (
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1"
        in workflow
    )
    assert (
        "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0"
        in workflow
    )
    assert "ref: eb23656e56ea3555599a6c5278a8b5834dc56b6d" in workflow

    required_files = [
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/pull_request_template.md",
    ]
    missing = [path for path in required_files if not (ROOT / path).is_file()]
    assert missing == [], f"missing public repository contracts: {missing}"

    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "https://github.com/Conradgui/loop-craft/security/advisories/new" in security
    assert "0.4.x" in security
    assert "Evidence" in security

    bug_form = (ROOT / ".github/ISSUE_TEMPLATE/bug_report.yml").read_text(
        encoding="utf-8"
    )
    for field in (
        "Loop Craft version",
        "Entry route",
        "Selected Adapter",
        "Minimal reproduction",
        "Expected behavior",
        "Actual behavior",
        "Evidence redaction",
    ):
        assert field in bug_form

    pull_request = (ROOT / ".github/pull_request_template.md").read_text(
        encoding="utf-8"
    )
    for section in ("User impact", "Scope", "Validation", "Not run", "Boundaries"):
        assert section in pull_request

    stable_skill = "https://github.com/Conradgui/loop-craft/tree/v0.4.0/loop-craft"
    for readme_name in ("README.md", "README.zh.md"):
        readme = (ROOT / readme_name).read_text(encoding="utf-8")
        assert stable_skill in readme
        for community_path in (
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "https://github.com/Conradgui/loop-craft/issues",
            "https://github.com/Conradgui/loop-craft/pulls",
        ):
            assert community_path in readme

    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "SECURITY.md" in contributing
    assert "Do not open a public Issue" in contributing
