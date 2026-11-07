---
name: untangle-codebase
description: Identify and remove evidenced structural clutter in a requested codebase scope. Use for codebase cleanup, untangling, or the required review before an agent merge.
license: MIT
---

# Untangle Codebase

Find structural friction in the requested scope. Prefer the smallest maintainable change that removes an evidenced problem.

## Scope and permissions

For an explicit cleanup, use the files, component, or broader scope the user requests. For ordinary implementation, work only within the authorized task. Preserve unrelated changes. Inspect connected callers and contracts when necessary to understand a finding.

In Plan Mode or a review-only task, report findings and proposals without editing files. This skill does not authorize a merge, commit, external action, or extra agent. Follow the active routing and verification rules.

## Find evidenced friction

Ask whether related pieces need to change together. Inspect relevant code, callers, tests, and project conventions. Git history or Graphify can provide evidence when appropriate, but neither is required.

Look for these problems:

- Hidden links, such as duplicated rules, implicit call order, and shared mutable state.
- Unnecessary coupling, such as callers that depend on volatile internals.
- Redundant wrappers, unused code, and speculative configuration with no demonstrated need.
- Special cases whose cause could be addressed by a simpler design.

Record the concrete paths, behavior, and maintenance risk for each material finding. Distinguish an observed problem from an assumption. A special case, retry, guard, test, or abstraction is not redundant by itself. Confirm its purpose and usage before removal.

Preserve behavior, public contracts, required validation, error handling, security, accessibility, and meaningful test coverage. Keep useful abstractions and explanatory comments. Do not remove or weaken tests merely to simplify code. If a structural change needs a material contract or scope decision, return it to the root.

## Before an agent merge

Before an agent performs a local or remote merge, inspect the proposed changes against the actual target branch merge base. Establish the source and target revisions from the actual merge context. For a remote merge, verify the current remote source and target revisions. If the revisions or a defensible merge base are unavailable, stop and report the limit.

Inspect the change and connected code needed to assess findings. Check for actionable structural clutter introduced by the proposed change. A finding is actionable when evidence shows a concrete maintenance or behavior risk and a useful scoped improvement. Do not block on similarity, size, style preference, or deliberate duplication alone. Explain material deliberate duplication and false positives.

Resolve actionable findings within the authorized scope and repeat affected checks. If a finding remains unresolved or its fix needs a material scope or contract decision, stop the merge and report it. If the review cannot be completed, stop the merge and report the missing evidence. Record the source revision, target revision, comparison base, checks, and dispositions. Immediately before merging, verify that the reviewed source and target revisions still match. If either changed, repeat the affected review and checks before merging.

For documentation-only changes, complete the review and state that the proposed change contains no code when evidence supports that statement. This agent rule does not change manual Git workflows or install hooks. The separate Slopo review remains required before agent-created or amended commits.

## Verify and report

Run checks appropriate to the changed behavior and existing project requirements. Do not weaken assertions or remove meaningful coverage to pass a refactor. Report material findings, changes, checks, and unresolved risks. A no-change result is valid when the scope contains no actionable friction.

## Source and adaptation

Adapted from Caldo's [untangle-codebase skill](https://github.com/caldoai/skills/blob/f3cf47774975a7d9fca45730babf4ff7ad765ada/skills/untangle-codebase/SKILL.md), revision `f3cf47774975a7d9fca45730babf4ff7ad765ada`. This adaptation limits scope, preserves permissions and tests, and adds an agent pre-merge review. [LICENSE](LICENSE) contains the upstream MIT license.
