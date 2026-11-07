---
name: state-machine-review
description: Inspect code changes for defects in explicit and implicit state machines. Use during changes to stateful behavior and for requested lifecycle, pull request, or pre-push reviews.
---

# State Machine Review

Inspect the requested changes for concrete defects in explicit and implicit state machines. State can span flags, callbacks, coroutines, persisted records, UI state, jobs, and external services.

## Scope and mode

During an authorized code change, screen the changed behavior for affected stateful lifecycles. Apply the checks below when a lifecycle can be affected. Fix confirmed defects within the authorized task and follow the active ownership and verification rules.

For an explicit review, use the requested commit range, files, or diff. Review-only work does not authorize edits, commits, or pushes. In Plan Mode, analyze and propose changes without editing files.

For a pull request, compare the PR head with the target branch merge base when available. For a pre-push review, inspect the actual refs and revisions provided. Review relevant refs separately, including branch creation, deletion, and force pushes. For a new branch, use an explicitly provided base or a justified target-branch merge base and state the choice.

If actual push refs are unavailable, do not claim to know exactly what will be pushed. Use the configured upstream or another defensible comparison base and state the choice. If no defensible base exists, ask for one or report the limitation. Include uncommitted or untracked changes only when the user requests them or they are explicitly in scope.

## Trace affected lifecycles

Prioritize lifecycles whose behavior or invariants can be affected. Read enough connected code to identify entry points, transitions, persistence, callers, background work, external effects, and existing tests. Do not audit unrelated repository areas.

For each relevant lifecycle, identify the states, including implicit and persisted states. Identify transition events, responsible code, invariants, and ownership of state and resources. Examine what happens after errors, cancellation, process termination, and restart.

## Examine failure paths

When applicable, examine:

- Concurrent or repeated events, races, stale results, and ordering assumptions.
- Cancellation, timeouts, cleanup, and work that continues after its owner is gone.
- Retries, duplicate delivery, idempotency, and partial or uncertain external effects.
- Process death, persistence boundaries, recovery, and incompatible stored states.
- Invalid or contradictory flags and missing or unreachable transitions.
- UI state that differs from actual work or persisted data.
- Version changes, migration, and backward compatibility.

Use tests, targeted inspection, or a small reproduction when feasible and permitted. Treat a defect as confirmed only when evidence supports its execution path. Do not assume exactly-once effects or successful rollback without evidence.

## Findings and verification

For a review, list actionable findings first, ordered by severity. Give each finding a concise title and precise file and line references. Describe the triggering events and state transitions. State the expected and observed or code-supported behavior and its impact. Give a test or reproduction for the issue. Separate confirmed defects from plausible but unverified risks.

For implementation, follow the task's validation requirements and report material fixes, results, and remaining risks. For either mode, summarize the inspected scope, checks actually run, and important limits. When a review finds no actionable issues, say so without claiming that the code is defect-free or that every state machine was found.
