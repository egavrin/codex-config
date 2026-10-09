---
name: writing-for-agents
description: Create or revise agent-facing skills, AGENTS.md, and linked instruction documents for clear triggers, usable structure, and checkable completion criteria.
---

# Writing for Agents

Write instructions that help an agent take the intended actions and recognize
completion. Preserve the document's purpose, the user's requirements, and the
applicable instruction hierarchy. Use this reference for agent-facing documents;
ordinary correspondence does not need this workflow.

## Scope and mode

Work on the documents the user asks to create, revise, or review. Reading an
`AGENTS.md` file as task guidance does not authorize rewriting it. In Plan Mode
or a review-only task, present proposed text and findings in chat. Edit files
when the requested task includes those edits and the active mode permits writes.
Follow existing authorization and routing; this skill adds no delegation scheme.

When authoring a skill, read [SKILL-MECHANICS.md](SKILL-MECHANICS.md) for Codex
discovery and invocation. Use the bundled `skill-creator` for current packaging
requirements and validation; this skill supplies writing criteria.

## Preserve the requirements

Before revising, identify the audience, intended outcomes, trigger conditions,
material constraints, exceptions, and verification requirements. Inspect the
relevant source and active instructions before replacing wording. Keep unresolved
ambiguities visible; resolve those that would materially change behavior.

Compare the revision with those requirements before delivery. Shortening is
useful only when meaning and operational reliability survive. Preserve security,
permission, scope, compatibility, and completion requirements even when they are
lengthy. Report a conflicting or stale requirement rather than silently removing
it because it is inconvenient.

## Write useful context pointers

A context pointer names material outside the loaded instructions and states when
to read it: a skill description or a conditional link to a reference.

- Put the capability and important trigger conditions first.
- Name distinct cases once rather than repeating synonyms for the same case.
- Identify the target and the decision or task it supports. Use concrete,
  resolvable paths or links.
- Keep essential requirements visible. Move conditional detail behind a pointer
  only when the instruction still makes clear when that detail is required.

Discovery depends on the pointer and the host's skill mechanism; phrasing cannot
guarantee invocation. Validate important triggers with realistic requests when
their reliability matters.

## Organize the information

Distinguish ordered actions from reference material. Keep common actions and
constraints in the entrypoint; place substantial branch-specific guidance in
linked references read only when relevant. A reference-only document is valid
when the task needs criteria rather than a fixed recipe.

Keep a concept's definition, rules, and exceptions together. Give each requirement
one authoritative home; link to it instead of maintaining parallel copies.
Split a document only when a distinct audience, invocation, or branch warrants
the extra file. A linked file does not itself reset the agent's context.
Use handoffs only when the task and active routing already justify them.

Balance the material loaded for the agent with what a human must find and
maintain. Reduce unnecessary context, while retaining the choices and information
the user needs to exercise judgment.

## Make completion observable

For each meaningful action, state how to recognize completion: a checked
artifact, accounted-for change, passed validation, or explicitly reported
limitation. Match the criterion to the requested scope and risk. Avoid vague
gates such as "understand the system" and arbitrary exhaustive work beyond the
task. Keep essential criteria visible rather than hiding them behind later steps.

## Choose precise language and prune

Use familiar terms with clear meanings. A short recurring label can replace
repeated explanations only when it retains the distinctions the agent needs.
Prefer a direct statement of the desired action; retain explicit prohibitions
when they express necessary guardrails. No word, slogan, or formulation guarantees
model behavior.

Remove duplication, unrelated exposition, and demonstrably redundant guidance.
Reference cheaply discoverable repository facts rather than maintaining stale
copies, unless an inline fact is necessary for safe or understandable execution.
Keep unwritten conventions, rationale, and non-obvious pitfalls that change
decisions. Preserve a rule when its necessity is uncertain; avoid turning a
single example or failure into a universal restriction.

Validate relevant links and the document's format, then review representative
cases for lost requirements, ambiguous triggers, and premature completion.
Report the meaningful changes, checks actually performed, and remaining limits.

## Source and adaptation

Adapted for Codex from Matt Pocock's
[writing-for-agents](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL.md),
revision `b0618bc436ad893b3c5e84e55fba86586d34a404`.
This local adaptation uses Codex invocation settings, preserves task and mode
boundaries, and treats writing heuristics as guidance rather than guarantees.
The original MIT license and copyright notice are included in [LICENSE](LICENSE).
