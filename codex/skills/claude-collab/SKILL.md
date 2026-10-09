---
name: claude-collab
description: "Share substantial bounded coding or review work with a Claude Opus High CLI companion that uses subscription authentication. Supply shared global skills and explicit context. Codex owns acceptance. Select this skill automatically for suitable independent work. Keep tiny tasks in Codex."
---

# Claude Collab

For ordinary substantial work with a useful independent package, select Claude Opus as the primary external owner. Use explicit High effort. The package may contain bounded implementation or review. Codex owns scope, integration,
patch application, tests, and final acceptance. Keep tiny questions and local edits
in Codex. The companion is an external CLI request, not a native child agent.

Report the route as `<effective-root>-claude`, separately from actual root model,
reasoning, and observable service tier. Do not label it a Sol–Astra benchmark.
Named opt-in orchestration experiments remain authoritative. If Claude is unavailable, limited, stalled, or cannot complete the bounded package, stop the request.

Then, use the existing native model-aware fallback (Astra High via `astra_executor_high` for a Sol root). Record the
concrete fallback reason and preserve completed evidence. Never run both owners
concurrently.

High effort is a quality choice, not a claim of lower latency.

At the beginning of a task, examine available Codex quota once with the app's usage
limits tool. If any available window has 20% or less remaining, favor a larger
independent Claude package. Unknown quota remains unknown. Do not invent exact
Claude quota or poll quota during the task. Balance useful ownership rather than
splitting mechanically by lines or equal token counts.

Use one request per package and at most one focused repair or missing-context
follow-up. Preserve completed work and send only the changed facts needed for the
follow-up. Stop immediately on authentication or usage-limit errors. Avoid reciprocal
review loops and repeated calls without a concrete unmet criterion.

Never run a
Claude companion and a native child concurrently on the same task. In Plan Mode,
use only read-only review. Do not request implementation or apply a patch.

## Prepare and invoke

Read [the packet and command reference](references/bridge.md) before the first
request. Use the standard-library helper at `scripts/bridge.py`. It exposes
`doctor`, `sync-skills`, and `run --mode review|patch --packet FILE`.

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
