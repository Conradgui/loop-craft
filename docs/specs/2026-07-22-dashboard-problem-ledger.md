# Loop Craft Problem Ledger Dashboard Spec

> Status: Approved
> Date: 2026-07-22

## Goal

Keep the existing live dashboard, but make the current problems, resolution order,
and completion gates directly visible without overstating product progress.

## Design

- Add a main-area Problem Ledger with priority, current fact, next action, and
  observable completion condition.
- Replace the unsupported `86%` estimate with five explicit phase gates. Progress
  is the number of completed gates divided by five.
- Keep exactly one active mainline item. Validation and documentation remain
  subordinate lanes.
- Keep actual defects and delivery gaps under Risks. Move non-risk facts such as
  remote synchronization into Activity, and put accepted product boundaries under
  Known limits.
- Preserve the existing static HTML, JSON data source, five-second refresh, and
  responsive sidebar. Add no dependency or framework.

## Phase Gates

1. Core and Packaging slice is usable.
2. All three entries use the same Loopability and Packaging route.
3. Entry provenance and approval evidence is Manifest-bound.
4. Repository README, public licensing decision, and current governance documents
   are complete.
5. One real user task completes the full Skill plus Evidence path.

## Acceptance

- The dashboard shows every current Important finding from the 2026-07-22 review.
- Each problem has one next action and one observable done condition.
- The first active action is the shared Gate and From-scratch zero-Loop route.
- The dashboard does not claim a completed Demo, common three-entry route, full
  0..n support, or a fully documented public repository.
- The page continues to refresh from `status.json` every five seconds.
