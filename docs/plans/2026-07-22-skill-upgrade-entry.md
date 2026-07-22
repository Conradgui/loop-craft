# Skill Upgrade Entry Walking Skeleton

## Objective

Connect the second Loop Craft input entry: inspect an existing Agent Skill,
apply the Phase 1 Loopability workflow, return a four-verdict Decision Record,
and route only the current Core-compatible subset to the existing build path.

## Scope

- Reuse Phase 1 contract recovery, observed/inferred labels, Loopability Gate,
  four verdicts, finding IDs, approval, and preservation rules.
- Keep Assessment read-only by default.
- Build only a single `loop_first_skill` whose approved contract fits
  `core-slice-v0.1` and does not require preserving arbitrary scripts, assets,
  or linked external resources.
- Stop at `Assessment only` for `keep_as_skill`, `embedded_loop`,
  `split_into_loops`, unsupported multi-loop cases, or material evidence gaps.

## Explicitly Deferred

Preserving arbitrary existing Skill packages in the deterministic Adapter,
multiple Loop IR, Runtime, Override, Conversation Distiller, Library Edition,
publication, scheduling, and real forward behavioral experiments.

## Delivery Checks

- `loop-craft/SKILL.md` exposes the route and truthful boundary.
- `loop-craft/references/upgrade-skill.md` contains the migrated workflow and
  the Core compatibility gate.
- Existing Core build path remains unchanged and is referenced, not duplicated.
- Dashboard and project records identify this as the active mainline.
