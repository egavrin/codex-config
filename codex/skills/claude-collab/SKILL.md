---
name: claude-collab
description: "Call a subscription-authenticated Claude Opus High companion for explicit requests or the named normal policy completion review. Supply bounded context and shared skills. Codex owns acceptance. Other automatic routing is excluded."
---

# Claude Collab

Use this skill for explicit Claude requests, `$claude-collab`, or the completion review authorized by `PROFILE: TERRA_SOL_CLAUDE_REVIEW`.
Automatic skill selection remains disabled with `allow_implicit_invocation: false`.
The named policy supplies standing authorization only for that review. It does not authorize automatic Claude implementation.
Read the Claude completion review section in `~/.codex/AGENTS.md` when that policy applies.
Named experiments remain exempt unless the user explicitly changes the experiment.
Task size, Codex quota, and a native failure do not authorize a Claude request.
Ordinary work follows the routes and completion gate in `AGENTS.md`.

For an explicit request, use Claude Opus with High effort for a bounded implementation or review package.
Codex owns scope, integration, patch application, tests, and final acceptance.
The companion is an external CLI request, not a native child agent.
Report the manual route as `<effective-root>-claude`, separately from root model, reasoning, and observable service tier.
Do not label it a native Sol–Astra benchmark.
Named opt-in orchestration experiments remain authoritative.

If Claude cannot complete the explicit request, stop it and report the concrete reason.
Preserve completed evidence.
If authorized work remains, use the applicable native route with root-owned acceptance.
The completion reviewer may run synchronously while Sol pauses edits. No other native owner may work concurrently.
High effort is a quality choice, not a claim of lower latency.
Do not poll quota or invent subscription usage figures.

Use one request per package. After an invalid response, an invalid patch, or a
report of missing context, you may send one focused repair request. A later root repair can use that same remaining allowance.
Use two calls total per package, including its repair. Include the
concrete evidence, such as `failure_stage`, `failure_reason`, and the unmet
criterion. Also include the current source. If the failure is a stale baseline,
examine the intervening edits before you prepare that repair. Do not force a patch
or a rebase. Preserve completed work and send only the changed facts that the
repair needs.

If authentication, quota, or inactivity stops the request, stop. If the repair is
not successful, also stop. Then, follow the failure policy above. The helper never
retries automatically. Avoid reciprocal review loops and repeated calls without a
concrete unmet criterion.

Except for the named completion review, never run a Claude companion and a native child concurrently on the same task.
For that exception, Sol pauses edits and waits synchronously. No native nesting or recursive bridge call is permitted.
In Plan Mode,
use only read-only review. Do not request implementation or apply a patch.

## Normal completion review

After code and focused self-check, Sol builds the current nine-field packet and runs preflight before the review request.
Use review mode with Opus High and require an empty `diff`.
Check findings against the code and task evidence.
Fix confirmed relevant findings within scope. Reject unsupported or out-of-scope findings with reasons.
Escalate material scope or contract decisions to the root. Rerun affected deterministic checks.
Do not request another review merely because Sol fixed review findings.
The root owns final acceptance.
If authentication, quota, CLI, or inactivity prevents review, stop that request and preserve evidence.
Continue authorized implementation and checks with explicit `review_unavailable` and `failure_stage` disclosure.
Never claim that an unavailable review passed. Correct local preflight errors before a model request.
The retry allowance above applies across the whole package. It does not reset after root repair.

## Prepare and invoke

Read [the packet and command reference](references/bridge.md) before the first
request. Use the standard-library helper at `scripts/bridge.py`. It exposes
`doctor`, `sync-skills`, `preflight --mode review|patch --packet FILE`, and
`run --mode review|patch --packet FILE`.

Before each request, run `preflight` with the same mode and packet. Preflight does
the complete bundle validation of `run`, but it calls no CLI and synchronizes no
skills. If preflight fails, correct the packet locally. Use the reported field and
index in `diagnostic`, `failure_reason`, and the section sizes in `packet_size`.
Typical causes are an incorrect path, a missing Ponytail level, and an oversized
bundle. `run` validates the current inputs again before the model request.

Keep the mandatory policies and the scope. If the bundle is too large, divide the
work into coherent packages. Do not remove required context. While Claude works,
do not edit the scope files. Independent root work may use other paths. The input
packet keeps its nine fields, and the response keeps `explanation` and `diff`.

Select relevant skills and required related documents yourself. The helper bundles
each selected skill's complete `SKILL.md`, linked local documents, and explicitly
selected references. It also reads scoped source files and project instruction
files. Claude may report missing material. It cannot fetch more context. Examine
the packet for unnecessary sensitive information before sending it.

Do not include
credentials, a full conversation, bulk logs, or unrelated private material. The
helper's sensitive-content check is a backstop, not a perfect detector.

Use only the existing `claude.ai` subscription login. This workflow is an explicit exception to generic API-key loading. Never read `~/.env`, credential files, or secret values. Never add API fallback, modify authentication, change billing, or enable Extra Usage. The helper examines authentication in the same sanitized child
environment used for the request and fails closed unless it reports `claude.ai`
and `firstParty`. Subscription selection cannot turn off account overages already
enabled by the user.

Reported cost estimates are not subscription charges.

Every request uses explicit `--model opus --effort high`, no tools, fresh
nonpersistent print mode, and one turn. Stream events supervise progress. The
default watchdog stops after 15 minutes without meaningful model progress. Healthy
progress has no default total wall-clock cap. An explicit optional total budget
can bound a package. The helper emits sanitized progress every 30 seconds and writes it to private `progress.json`.

Nonempty text or thinking deltas and a first completed assistant message count as model progress.
Strictly increasing positive thinking-token estimates also count after a validated Opus `message_start`.
Status records `cli_version` and, on failure, the
fixed codes `failure_stage` and `failure_reason`. Use these codes to select a repair or the fallback.

While you supervise a request, send meaningful status to the user within 60 seconds. Heartbeats prove helper liveness only and
do not renew inactivity. Never infer oversized context from a wall timeout alone. Safe/restricted mode
suppresses custom hooks, MCP, installed plugins, skills, and ambient instructions for that
invocation.

The CLI can report its two recognized built-in plugins. These do
not grant tools or expand packet scope. Shared skills are passed explicitly in the packet.

This does not
disable skills in ordinary Claude sessions or grant a skill power to expand scope.
**When Claude receives this skill as context, do not invoke the bridge recursively.**

## Accept the result

Review the private artifact paths printed by the helper. A successful patch result
means that path, baseline, and `git apply --check` validation passed. Nothing has
been applied. Read the explanation and diff.

Make sure that the scope and behavior match the task. Immediately before application, compare the recorded baselines with the current files. From the recorded project root, run `git apply --check`, then `git apply`.

Do not
force stale or conflicting patches. Review the resulting diff and run proportionate
project checks. Keep provider limitations distinct from product defects.

For reviews, inspect whether findings cite the supplied evidence and answer the
acceptance criteria. Missing context is a finding, not permission to inspect more
files. Completion is conditional on Codex acceptance, the relevant checks, and disclosure
of unresolved criteria and material risk.

## Shared library

`sync-skills` creates per-directory symlinks from `~/.claude/skills` to visible
user skills under `~/.codex/skills`. Run it after installing new user skills. `run`
also syncs before sending a request. It includes installed user directory aliases, excludes hidden/system entries and
plugin-cache roots, and preserves independent entries.

Bundled sibling references
may resolve only to approved visible user skill roots. Nested symlinks remain
rejected. Only exact links recorded in its ownership manifest
can be removed as stale. Resolve reported conflicts explicitly without overwriting
user entries.

Codex invokes `$skill-name`. Ordinary Claude uses `/skill-name`.
Use a separate native session's local `/skills` listing to examine native discovery. Bridge safe mode intentionally disables discovery for that request.

## Shared language policy

Every request includes the full controlled English profile, rule map, and software term list from `writing-for-agents`.
The helper adds `communication_policy` to the generated bundle. The input packet schema stays unchanged.
If a policy document is absent, the helper stops before the model request.
The complete encoded bundle, including this policy, must fit within the existing 256 KiB limit.
The policy changes prose only.

It adds no permission or scope.


## Ponytail plugin context

The installed Ponytail plugin supplies instructions in ordinary Codex and Claude sessions.
The restricted companion does not execute its hooks or scripts.
Read [the source registry](references/ponytail-source.json) for its pinned identity.
Select applicable plugin instructions through the existing skills array.

Use the plain names ponytail, ponytail-review, ponytail-audit, ponytail-debt, ponytail-gain, or ponytail-help.
The helper reads only registered, hashed documents from the pinned checkout.
It keeps this catalogue separate from shared user-skill synchronization.
A selected name that also exists as a user skill causes a conflict.
Resolve that conflict without replacing user files.

For an active core mode, select ponytail and state its level on a separate objective line:
Ponytail level: full
Use lite or ultra when that is the active level.
With off, omit the core skill.
If the current level is unknown, report that gap and omit the core skill.

Select a one-shot skill only for the applicable requested task.
Review, audit, debt, gain, and help remain independent of the core mode.
The helper includes ~/.codex/ponytail-policy.md with selected plugin material.
Missing policy, source changes, or unregistered instruction references stop the request.
README and benchmark navigation links authorize no additional reads.
All included text counts toward the existing 256 KiB limit.

Ponytail preferences do not change scope, Plan Mode, tools, authentication, routing, supervision, or acceptance.
