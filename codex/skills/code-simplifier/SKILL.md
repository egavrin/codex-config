---
name: code-simplifier
description: "Simplify recently changed or explicitly scoped code so it is easier to read and maintain. Preserve behavior. Use for code cleanup and focused improvements during implementation or refactoring."
license: Apache-2.0
---

# Code Simplifier

Make code clearer within the current task. Preserve its behavior. Prefer a structure that is easy to understand over fewer lines.

## Scope and operating mode

Work on code changed in the current task. An explicit user request for a file, component, or broader scope takes precedence. Use the available diff and task context to identify relevant sections. A file-level diff gives no permission to rewrite the complete file. Preserve pre-existing user changes and keep refinements within the requested
scope.

During authorized implementation or refactoring, make useful improvements. A separate cleanup request is not required. When the task is analysis-only or the
session is in Plan Mode, inspect and propose changes without editing files.
Follow the active routing instructions. This skill does not select a model or spawn agents.

## Refinement criteria

- Preserve observable behavior, outputs, public interfaces, error handling, and
  meaningful side effects. Keep evaluation order and asynchronous behavior intact
  when restructuring expressions or control flow.
- Follow applicable `AGENTS.md` instructions, formatter and linter configuration,
  and the conventions in nearby code. Module syntax, import order, function style, type annotations, and React patterns depend on the project. Do not impose JavaScript conventions on other languages. Do not change conventions merely for personal preference.
- Reduce needless nesting, duplicated work, and abstractions that obscure the
  logic. Use descriptive names and group closely related operations when that
  makes the code easier to follow.
- Prefer readable conditionals to nested ternaries or dense one-liners. Keep useful boundaries, abstractions, and comments that explain intent or constraints. Remove a comment only when it adds no information beyond the code.
- Avoid clever transformations, merging unrelated concerns, and speculative
  generalization. Leave clear code alone. If a refinement makes a behavior or
  interface change, omit it from the simplification and report it separately.

## Verification and delivery

Inspect the diff for accidental scope expansion and behavior changes. Run existing
focused checks appropriate to the affected workflow and follow the project's
verification requirements. Do not rewrite tests or weaken assertions to make a
refinement pass. If behavior preservation is uncertain, keep the original
structure until there is enough evidence to justify the change.

Report only meaningful improvements, actual checks and results, remaining uncertainty, and checks that you could not perform. A no-change
result is valid when the scoped code is already clear.

## Source and adaptation

Adapted for Codex from Anthropic's
[code-simplifier agent](https://github.com/anthropics/claude-plugins-official/blob/ceb9b72b4c4c20ad39efce780edd0aabe80ebce3/plugins/code-simplifier/agents/code-simplifier.md),
source revision `ceb9b72b4c4c20ad39efce780edd0aabe80ebce3`.

This adaptation replaces the provider-specific agent configuration with a Codex
skill, uses project instructions and language conventions, and makes scope,
planning mode, and verification explicit. The upstream Apache-2.0 license is
included in `LICENSE`, taken from the plugin's license revision
`aecd4c852f10b466245f18383fa6aad8c0b10d57`.
