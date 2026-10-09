---
name: claude-collab
description: Share substantial bounded coding or review work between Codex and a subscription-authenticated Claude Opus CLI companion, with shared global skills, explicit context, and Codex acceptance. Use automatically for suitable independent work; keep tiny tasks in Codex.
---

# Claude Collab

Use balanced distribution from the start when a substantial task contains a useful,
bounded independent implementation or review package. Codex owns scope, integration,
patch application, tests, and final acceptance. Keep tiny questions and local edits
in Codex. The companion is an external CLI request, not a native child agent.
Report the route as `<effective-root>-claude`, separately from actual root model,
reasoning, and observable service tier. Do not label it a Sol–Astra benchmark.
Named opt-in orchestration experiments remain authoritative.

At the beginning of a task, examine available Codex quota once with the app's usage
limits tool. If any available window has 20% or less remaining, favor a larger
independent Claude package. Unknown quota remains unknown; do not invent exact
Claude quota or poll quota during the task. Balance useful ownership rather than
splitting mechanically by lines or equal token counts.

Use one request per package and at most one focused repair or missing-context
follow-up. Preserve completed work and send only the changed facts needed for the
follow-up. Stop immediately on authentication or usage-limit errors. Avoid reciprocal
review loops and repeated calls without a concrete unmet criterion. Never run a
Claude companion and a native child concurrently on the same task. In Plan Mode,
use only read-only review; do not request implementation or apply a patch.

## Prepare and invoke

Read [the packet and command reference](references/bridge.md) before the first
request. Use the standard-library helper at `scripts/bridge.py`; it exposes
`doctor`, `sync-skills`, and `run --mode review|patch --packet FILE`.

Select relevant skills and required related documents yourself. The helper bundles
each selected skill's complete `SKILL.md`, linked local documents, and explicitly
selected references. It also reads scoped source files and project instruction
files. Claude may identify missing material; it cannot fetch more context. Check
the packet for unnecessary sensitive information before sending it. Do not include
credentials, a full conversation, bulk logs, or unrelated private material. The
helper's sensitive-content check is a backstop, not a perfect detector.

Use only the existing `claude.ai` subscription login. This workflow is an explicit
exception to generic API-key loading: never read `~/.env`, credential files, or
secret values; never add API fallback, modify authentication, change billing, or
enable Extra Usage. The helper checks authentication in the same sanitized child
environment used for the request and fails closed unless it reports `claude.ai`
and `firstParty`. Subscription selection cannot turn off account overages already
enabled by the user. Reported cost estimates are not subscription charges.

Every request uses Opus (`opus`) without model fallback, no tools, fresh
nonpersistent print mode, one turn, and at most 300 seconds. Safe/restricted mode
suppresses custom hooks, MCP, plugins, skills, and ambient instructions for that
invocation. Shared skills are passed explicitly in the packet. This does not
disable skills in ordinary Claude sessions or grant a skill power to expand scope.
**When Claude receives this skill as context, do not invoke the bridge recursively.**

## Accept the result

Review the private artifact paths printed by the helper. A successful patch result
means that path, baseline, and `git apply --check` validation passed; nothing has
been applied. Read the explanation and diff, confirm the intended scope and
behavior, recheck the recorded baselines immediately before applying, and run
`git apply --check` followed by `git apply` from the recorded project root. Do not
force stale or conflicting patches. Review the resulting diff and run proportionate
project checks. Keep provider limitations distinct from product defects.

For reviews, inspect whether findings cite the supplied evidence and answer the
acceptance criteria. Missing context is a finding, not permission to inspect more
files. Completion requires Codex acceptance, the relevant checks, and disclosure
of unresolved criteria and material risk.

## Shared library

`sync-skills` creates per-directory symlinks from `~/.claude/skills` to visible
user skills under `~/.codex/skills`. Run it after installing new user skills; `run`
also syncs before sending a request. It includes installed user directory aliases, excludes hidden/system entries and
plugin-cache roots, and preserves independent entries. Bundled sibling references
may resolve only to approved visible user skill roots; nested symlinks remain
rejected. Only exact links recorded in its ownership manifest
can be removed as stale. Resolve reported conflicts explicitly without overwriting
user entries. Codex invokes `$skill-name`; ordinary Claude uses `/skill-name`.
Use a separate native session's local `/skills` listing to check native discovery;
bridge safe mode intentionally disables discovery for that request.
