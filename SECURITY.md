# Security Policy

## Supported versions

Security fixes are considered for the current `0.4.x` line. Older development snapshots are
not supported. The repository may document later versions before a formal Release exists; the
[Releases page](https://github.com/Conradgui/loop-craft/releases) is the authoritative list of
published versions.

## Report a vulnerability privately

Do not open a public Issue for a suspected vulnerability. Use GitHub's
[private vulnerability reporting form](https://github.com/Conradgui/loop-craft/security/advisories/new)
and include:

- the affected Loop Craft version or commit;
- the entry route and selected Adapter;
- the smallest safe reproduction;
- the expected and observed authority or data boundary;
- whether generated Artifact or Evidence content is involved;
- a suggested remediation, when available.

Remove secrets, raw private conversations, credentials, personal data, absolute local paths and
unrelated Evidence before submitting. A synthetic reproduction is preferred.

The maintainer will make a best-effort acknowledgement within seven days, assess severity and
coordinate disclosure through the private advisory. Remediation timing depends on impact and
available maintainer capacity; this is not a guaranteed service-level agreement.

## Security boundary

Loop Craft is a local Agent Skill and deterministic build chain. When explicitly approved, it
can read scoped source material, write a new local Artifact and Evidence Package, and execute
the selected local validator. It does not provide authentication, sandboxing, secrets storage,
remote execution, publishing or a Runtime permission system.

A security report is appropriate when Loop Craft unexpectedly crosses an approved filesystem or
authority boundary, leaks excluded source material into an Artifact, accepts tampered Evidence,
weakens a stop/approval condition, or makes an unsupported compatibility claim. General feature
requests and ordinary classification disagreements belong in the public Issue tracker after all
sensitive material is removed.
