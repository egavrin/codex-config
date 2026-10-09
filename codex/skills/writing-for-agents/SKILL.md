---
name: writing-for-agents
description: "Create or revise skills, AGENTS.md files, and linked instructions for agents. Define clear triggers, usable structure, and verifiable completion criteria."
---

# Writing for Agents

Use this skill to write instructions that help an agent do the intended
actions and recognize completion. Keep the purpose of the document, the
requirements of the user, and the applicable instruction hierarchy.

Use this workflow for agent-facing documents. This workflow is unnecessary for ordinary correspondence. The controlled-English profile still applies to all prose
that you write.

## Scope and mode

Work on the documents that the user asks you to create, revise, or review. When
you read an `AGENTS.md` file as task guidance, you get no permission to rewrite
it. In Plan Mode or in a review-only task, give the proposed text and the
findings in chat. Edit files when the requested task includes those edits and
writes are permitted in the active mode. Follow the current authorization and routing.
This skill adds no delegation scheme.

When you write a skill, read [SKILL-MECHANICS.md](SKILL-MECHANICS.md) for Codex
discovery and invocation. Use the bundled `skill-creator` for the current
packaging requirements and validation. This skill supplies the writing
criteria.

## Preserve the requirements

Before you revise a document, identify these items:

- The audience and the intended results.
- The trigger conditions.
- The material constraints and their exceptions.
- The verification requirements.

Examine the related source and the active instructions before you replace
wording. Keep unresolved ambiguities visible. Resolve each ambiguity that
changes behavior materially.

Before delivery, compare the revision with those requirements. A shorter text
is useful only when the meaning and the operational reliability stay the same.
Keep security, permission, scope, compatibility, and completion requirements,
also when they are long. Report a requirement that is in conflict or out of
date. Do not remove it silently because it is inconvenient.

## Write useful context pointers

A context pointer is a skill description or a conditional link to a reference.
It names material outside the loaded instructions. It also tells when to read
that material.

- Put the capability and the important trigger conditions first.
- Name each different case one time. Do not repeat synonyms for the same case.
- Identify the target and the decision or task that it supports. Use concrete
  paths or links that resolve.
- Keep essential requirements visible. Move conditional detail behind a pointer
  only when the instruction still tells when that detail is necessary for the agent.

Discovery depends on the pointer and on the skill mechanism of the host. No
wording can guarantee invocation. When the reliability of an important trigger
is material, validate the trigger with realistic requests.

## Organize the information

Keep ordered actions separate from reference material. Put the common actions
and constraints in the entry document. Put large guidance for one branch in a
linked reference that the agent reads only when that branch applies. A
reference-only document is valid when the task calls for criteria, not a fixed
procedure.

Keep the definition, the rules, and the exceptions of a concept together. Give
each requirement one authoritative location. Link to that location, and do not
keep parallel copies. Split a document only when a different audience,
invocation, or branch justifies the extra file. A linked file does not reset
the context of the agent. Use a handoff only when the task and the active
routing already justify it.

Balance the material that the agent loads against the information that a human
must find and maintain. Remove context unnecessary for the agent. Keep the
choices and the information necessary for the user to make a decision.

## Make completion observable

For each meaningful action, tell how to recognize completion. Use one of these
criteria:

- An artifact that you examined.
- A change that you account for.
- A validation that passed.
- A limit that you report explicitly.

Make the criterion agree with the requested scope and risk. Do not use vague
gates, such as "understand the system." Do not make arbitrary, exhaustive
work outside the task mandatory. Keep essential criteria visible. Do not put them behind
later steps.

## Choose precise language and prune

Use familiar terms with clear meanings. A short recurring label can replace
repeated explanations only when it keeps the distinctions necessary for the agent.
When possible, state the desired action directly. Keep explicit prohibitions
when they are necessary guardrails. No word, slogan, or wording can guarantee
the behavior of a model.

Remove duplication, unrelated explanations, and guidance that is demonstrably
redundant. Refer to repository facts that are easy to find, and do not keep
copies that can become stale. Keep an inline fact only when necessary for task understanding or safe task execution.

When unwritten conventions, rationale, or pitfalls that are not obvious change
decisions, keep them. If you are not sure that a rule is necessary, keep the
rule. Do not make one example or one failure into a universal restriction.

Validate the related links and the format of the document. Then, examine
representative cases for lost requirements, ambiguous triggers, and premature
completion. Report the meaningful changes, the checks that you actually did,
and the limits that remain.

## Use the controlled-English profile

The shared profile in
[references/controlled-english.md](references/controlled-english.md) sets the
language for agent messages, answers to the user, and generated prose. Its rule
map, [references/ste-rule-map.md](references/ste-rule-map.md), gives the status
of each writing rule. Its term list,
[references/software-terms.md](references/software-terms.md), defines the
approved software terms. The profile also applies outside this authoring
workflow.

When you write or revise an agent-facing document, apply the profile to new
prose. Do not change the meaning of a kept requirement to make it agree with
the profile. The profile controls wording only. It does not change the scope,
the mode, or the delegation limits in this skill. Other tools load these three
files by path. Keep the paths stable.

## Source and adaptation

This skill is a Codex adaptation of Matt Pocock's
[writing-for-agents](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL.md)
skill, revision `b0618bc436ad893b3c5e84e55fba86586d34a404`. This local
adaptation uses Codex invocation settings. It keeps the task and mode
boundaries. It treats the writing heuristics as guidance, not as guarantees.
[LICENSE](LICENSE) contains the original MIT license and copyright notice.
The controlled-English references are original text.

They cite ASD-STE100
Issue 9 as a private source and do not reproduce it.
