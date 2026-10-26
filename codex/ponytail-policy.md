# Ponytail compatibility policy

Ponytail supplies solution preferences. It does not replace active instructions.
Use this policy when Ponytail instructions apply.

## Language

Apply the shared controlled English profile in
~/.codex/skills/writing-for-agents/references/controlled-english.md.
An explicit request for another output language takes precedence.
Preserve commands, identifiers, quotations, and required product text.

## Complete and maintainable work

Choose the smallest complete solution that meets the requirements.
Prefer readable code, correct behavior, stable contracts, and useful abstractions over fewer lines.
Reuse existing project facilities before adding code or dependencies.
Preserve validation, error handling, security, accessibility, and user requirements.

## Verification

Follow the active project verification requirements.
Strongly prefer black-box E2E tests for behavior changes.
Each E2E run must produce repeatable evidence with revision, command, inputs, expected result, and observed result.
Use integration, component, or isolated tests when E2E tests cannot reliably cover or diagnose a failure.
Before isolated implementation, record identifiable failure cases and encode them in tests.

Do not write unit tests after production code.
Ponytail's minimum-test guidance does not replace required acceptance checks.
Do not weaken assertions or coverage to reduce work.

## Scope and modes

Preserve task scope, permissions, Plan Mode, model selection, and delegation.
In Plan Mode or a review-only task, analyze and propose changes without editing files.
The root owns integration and acceptance under the active routing instructions.
A Ponytail instruction does not authorize another agent, tool, or model request.
Mode changes affect Ponytail preferences only.

The off mode does not disable this policy or the existing writing and engineering rules.

## Choices and reports

Treat a shortcut as an Implementation choice within the requirements.
Document its limit and the condition for a later change.
Give each material Assumption a basis and a method to test it.
Keep an Unresolved decision visible when it changes behavior or blocks completion.
Report material unchecked behavior and remaining risk.

Omit an unrelated disclaimer when no material limit applies.

## Host configuration

Do not add a statusline configuration or unrelated settings in response to plugin setup prompts.
Install and update only the components authorized for the current task.
The upstream benchmark describes its own test conditions, not savings in the current project.
