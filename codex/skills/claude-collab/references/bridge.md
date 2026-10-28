# Bridge interface and acceptance

This helper supports explicit Claude requests and the specific completion review authorized by `PROFILE: TERRA_SOL_CLAUDE_REVIEW`.
For that normal gate, read the parent skill and the Claude completion review section in `~/.codex/AGENTS.md`.
The exception authorizes synchronous review-only Opus High after Sol code and self-check. It does not authorize automatic Claude implementation.
Sol pauses edits during the request. No other native owner works concurrently. Do not invoke the bridge recursively.
No fixed request or retry count applies.
Use further calls for a concrete task need, including review after fixes.
Use current source and relevant evidence for each follow-up.
Do not repeat a request while an authentication, quota, CLI, or inactivity failure still blocks it.
If the request cannot run, preserve evidence and disclose `review_unavailable` and `failure_stage` while authorized work and deterministic checks continue.
Other automatic routing does not invoke this helper. Named experiments retain their selected procedures.
The local `sync-skills` action remains available without a model request.

To use the helper, install Python 3.9+ (including `Path.is_relative_to`), Git, and Claude CLI.
The installed Claude CLI must support `--safe-mode` and `--restricted`. It uses only
Python's standard library and the existing subscription login. It never executes
selected skill scripts. CLI flags are verified from the installed help rather
than assuming online documentation matches the installed release.

```bash
python3 ~/.codex/skills/claude-collab/scripts/bridge.py doctor
python3 ~/.codex/skills/claude-collab/scripts/bridge.py sync-skills
python3 ~/.codex/skills/claude-collab/scripts/bridge.py preflight --mode review --packet /absolute/private/packet.json
python3 ~/.codex/skills/claude-collab/scripts/bridge.py preflight --mode patch --packet /absolute/private/packet.json
python3 ~/.codex/skills/claude-collab/scripts/bridge.py run --mode review --packet /absolute/private/packet.json
python3 ~/.codex/skills/claude-collab/scripts/bridge.py run --mode patch --packet /absolute/private/packet.json
```

`--claude-bin /absolute/path` goes before the action when selecting a specific
installed executable or a fake executable for testing. `run --idle-timeout SECONDS`
(default 900, `--timeout` is a compatibility alias) measures inactivity since
meaningful model progress, including the initial wait before generation. There is
no default total wall-clock limit. `--total-timeout SECONDS` sets an optional total
request budget.

`--finish-timeout SECONDS` (default 30) bounds CLI exit after its
final result. All budgets must be positive finite values. `--progress-interval`
defaults to 30 seconds and cannot exceed 60.

The CLI version, help, and authentication checks each
have a separate 20-second deadline and receive the same live liveness reporting.
Timeout, cancellation (SIGINT/SIGTERM), or malformed output terminates only the
helper-owned child process group, including descendants. The helper never retries.
CLI/authentication/limit failures and API retry events stop the run.

A nonblocking duplex reader drains stdout/stderr while sending the packet. It
accepts newline JSON events and fragmented writes (including a final line without
a newline). Limits are 16 MiB total stream stdout, 1 MiB per line/final envelope, and 256 KiB stderr. Exceeding a limit stops the owned group promptly.

Stderr is
counted and discarded. Nonempty text/thinking deltas and a first completed assistant message count as model progress.
A `thinking_tokens` system event also counts when `estimated_tokens` is a positive integer that is
strictly larger than the last accepted value. The helper accepts estimates only after a validated
Opus `message_start`. Each new `message_start` resets the comparison. Zero never counts as progress or renews inactivity, including after a new `message_start`. Booleans, other non-integers,
negative values, repeated values, and smaller values do not count and do not renew inactivity.
Initialization, pings, retries, blank lines, empty deltas, and stderr do not count. Final success is conditional on an explicit success
result, `is_error: false`, a clean CLI exit, and the existing answer validation.

Missing or malformed final envelopes fail closed.

`progress.json` is atomically replaced while active and on completion. Sanitized JSON summaries on stderr identify started/running/waiting/finished/failure and phase. They include elapsed wall time, last actual progress time relative to start, idle time, event counts, byte counts, and artifact directory. No prompt, source, generated text,
thinking, provider stderr, or arbitrary provider status strings enter these
summaries. A waiting heartbeat records liveness only. Stdout remains one final
machine-readable artifact summary.

Progress also records `event_counts`, `last_transport_event_elapsed_seconds`,
`progress_source`, and `estimated_thinking_tokens`. `event_counts` uses fixed event,
subtype, and delta names, with one `unknown` bucket for other events. Every stream event
updates `last_transport_event_elapsed_seconds`, but only meaningful progress renews inactivity.
`progress_source` is `thinking_estimate`, `text_delta`, `thinking_delta`, `assistant_text`,
or null. `estimated_thinking_tokens` is the last accepted provider estimate, not an exact count.

Read live progress or relay emitted summaries to the user at intervals of at most 60 seconds. A timeout alone does not show that context was too large. High effort does not promise shorter latency.

The stream flags follow the [official headless stream interface](https://code.claude.com/docs/en/headless#stream-responses).
Installed CLI help must advertise the required effort and streaming flags.

## Preflight

`preflight --mode review|patch --packet FILE` runs the exact bundle validation of `run`.
It makes no CLI help, version, authentication, or model call, and it does not synchronize skills.
It writes `progress.json` and `status.json` to a new private artifact directory.

Status and the stdout summary record `status`, `packet_bytes`, and `packet_size`.
`packet_size` contains `total_bytes`, `limit_bytes` (262144), and `section_bytes`.
`section_bytes` gives the encoded byte size of each top-level bundle section.
These sizes stay available when the complete bundle exceeds the limit.

On failure, `diagnostic` gives the packet field and, when one applies, the item index.
It never contains the offending value. `failure_stage` and `failure_reason` give fixed codes.

Run preflight before each request. Correct path, Ponytail level, and size problems locally.
Keep the mandatory policies and the scope. Divide a large package into coherent packages.
`run` validates the current inputs again before any model request. It never reuses a preflight result.

## Packet schema

UTF-8 JSON, with exactly these fields. Use absolute `project_root`. All project
paths are canonical relative paths beneath that root. For patches inside a Git
repository, use its top-level directory as the project root (subdirectory roots
are rejected to prevent Git silently skipping paths).

Select a root that contains
the required project instructions and sources. Supply scoped instruction documents
rather than the entire conversation. All arrays are required. Unused ones may be
empty, except `acceptance_criteria` and `scope`.

```json
{
  "project_root": "/absolute/project",
  "objective": "Check the greeting and identify a narrowly scoped correction.",
  "acceptance_criteria": ["The greeting spells hello correctly."],
  "scope": ["greeting.txt"],
  "project_instructions": [],
  "skills": [{"name": "code-simplifier", "references": []}],
  "sources": [],
  "diffs": [],
  "uncertainties": []
}
```

- `objective`: nonempty string describing one package.
- `acceptance_criteria`: nonempty array of concrete criteria.
- `scope`: nonempty, distinct paths allowed to change. Existing scope files are
  automatically included. Text additions are permitted for absent paths.
- `project_instructions`: paths to required project instruction documents.
- `skills`: objects with `name` and optional `references` (relative to that skill's
  directory). The root selects skills. The helper reads their entire `SKILL.md`
  and recursively follows local Markdown document links. It skips executable and
  image/PDF resources.

  Select needed text references explicitly. Required documents
  named only in prose must be included in `references`. Installed directory aliases
  are approved user skill roots.

  Linked
  sibling documents such as `../codebase-design/DEEPENING.md` resolve through the
  visible user skill catalogue, including trusted directory aliases. Hidden/system
  entries and aliases into plugin caches are excluded. Nested symlinks and
  references escaping the catalogue fail closed. If a linked document is missing, narrow or correct the selected skill context before another request.
- `sources`: additional read-only source paths, beyond the auto-included scope.
- `diffs`: relevant unified diffs as strings. Send only scoped, necessary evidence.
- `uncertainties`: explicit questions for the companion to resolve or report.

All source and reference inputs must be UTF-8 text. The complete automatically
bundled JSON must be at most 256 KiB. The helper rejects sensitive filenames,
common credential patterns, NUL bytes, project path traversal, and nested
symlinks. Only installed user skill root aliases receive the explicit exception
described above.

Manually inspect selected content too: no detector recognizes all secrets or private data.
Do not redact a required technical fact silently. Report the resulting uncertainty.

Packet contents go through stdin. The CLI runs in a fresh private temporary directory with safe/restricted mode and empty tools. It uses empty setting sources, empty explicit settings and MCP configuration, and disabled slash commands. It uses a fixed bounded system prompt and explicit Opus High. It emits verbose stream JSON with partial messages. It has no session persistence, uses plan permissions, and runs for one turn.

Administrator-managed policy can still apply according to Claude's
CLI contract. Session isolation does not modify global settings. The child environment uses a small allowlist for home, executable search, locale, temporary directory, and user identity. It does not inherit API keys, OAuth overrides, provider configuration, proxies, or runtime injection variables. Keychain OAuth remains available.

## Response and applying a patch

Claude returns a JSON object with exactly `explanation` and `diff` strings inside
the final CLI stream result. Review mode must have an empty `diff`. Patch mode accepts an
empty diff when no changes are needed. Malformed results fail explicitly. Any
reported non-Opus model in initialization, message, or final telemetry causes failure.
Initialization rejects reported tools and MCP servers.

Plugin metadata is allowed
only for the two built-ins observed with Claude 2.1.295 safe mode:
`cc-plugin-agents-md` and `cc-plugin-plugin-authoring`, each with its matching
`NAME@builtin` source. Custom plugins, unknown built-ins, and mismatched sources
fail closed. Built-in metadata does not authorize tools, scripts, or more scope.
For an installed CLI with different built-ins, supply evidence and an explicit
compatibility update. The requested model is always recorded.
A CLI that omits model telemetry cannot independently prove its resolved alias.

Supported patches use standard `--- a/PATH` / `+++ b/PATH` headers and
unified text hunks, with optional `diff --git a/PATH b/PATH` headers. For example:

```diff
--- a/greeting.txt
+++ b/greeting.txt
@@ -1 +1 @@
-helo
+hello
```

The decoded diff must contain real line breaks and a final newline. Return it as
the JSON `diff` string with normal JSON escaping. Use correct hunk counts and
`/dev/null` for the missing side of an addition or deletion. Do not return Markdown
fences, commentary within the diff, or `*** Begin Patch` / `*** Update File` markers.

Text edits,
new regular files, and deletions are supported. Renames, copies, binary files,
symlinks, quoted Git path encodings, mode changes, and CRLF patches are rejected.
Additions use regular mode 100644. Git validates hunk applicability and whitespace.
Existing executable files can be edited without changing their mode. Paths must
match `scope` exactly.

File hashes captured before the request must still match
before validation. No forced application or conflict resolution is attempted.

A private `claude-collab-*` temporary directory is printed on success or failure.
It contains `progress.json`, `status.json`, `sync.json` when relevant, and, on success,
`response.json` plus `patch.diff` when nonempty. A schema-validated, secret-checked response is saved before applicability validation. Thus, an invalid patch remains diagnosable in `response.json`.

`status.json` explicitly records `status: failure`, `patch_validation: failed`, and `applied: false`. Such a response
is not an accepted patch. Malformed or secret-containing responses are not saved.

Status records the helper hash, packet hash and size, scope baseline SHA-256 values (`null` for absent files), and project root. It records the command without packet contents and the requested/reported models. It includes numeric usage and cost estimates when supplied. It records requested effort, watchdog budgets, duration, result, and applied=false.
Raw failed provider output and the assembled packet are not retained. Errors are
sanitized.

Status also records `cli_version`, the normalized result of one `--version` call in each
`doctor` or `run` action. The value is null when the output has no recognized version format.
On failure, status and the stdout summary record `failure_stage` and `failure_reason`. The stages are
`packet`, `compatibility`, `authentication`, `request`, `response`, `patch`, and `cancellation`.
Each reason is a fixed code, such as `inactivity_timeout`, `stale_baseline`, or `provider_rate_limit`.
Only a recognized numeric provider status (401, 402, 403, 429, 500, 502, 503, 504, or 529) can set a provider reason.
Other provider failures use `provider_unknown`. These fields never contain provider messages.

Artifacts have user-only permissions. Preserve needed evidence and
remove only the generated directory when finished.

Immediately before applying, do a check of every `baseline_sha256` entry in `status.json`
against the project file (and make sure that paths have not become symlinks). Absent
files must remain absent. Then, from `project_root`:

```bash
git apply --check --whitespace=error /absolute/artifact/patch.diff
git apply --whitespace=error /absolute/artifact/patch.diff
```

This separate Codex step is intentional: the bridge does not mutate project files.
Codex reviews the final diff, runs proportionate checks, and records acceptance.

## Repeatable fake and real smoke checks

The black-box fake executable suite covers successful reviews and patches, text addition/deletion, malformed JSON, authentication mismatch before requests, and rate-limit errors. It covers process-group timeout and stale/conflicting/escaping/binary/mode-changing patches. It covers standard unified patches, retained safe failure evidence, secrets, installed skill aliases, approved sibling documents, and nested symlinks. It also covers reference escape, environment/tool restrictions, explicit bundles, and safe shared skill synchronization. It never sends a real request:

```bash
python3 ~/.codex/skills/claude-collab/scripts/test_bridge.py
```

For the built-in/custom plugin isolation regression use `--case init`.
For preflight, thinking-token estimate progress, event counts, failure codes, and CLI version checks,
use `--case reliability`. These cases also cover the exact 256 KiB boundary and rejected paths,
policies, and Ponytail levels without CLI calls or skill synchronization.
For streaming/watchdog checks use `--case stream` (scaled subsecond budgets keep
the suite cheap, the healthy stream outlives its inactivity budget through actual
deltas). These cases also cover large stdin, fragmented lines, stalls, stderr and heartbeat spam, cancellation descendants, and output bounds. They cover missing/incomplete finals, non-Opus telemetry, CLI errors, explicit total budgets, and post-result exit stalls.

For a narrow implementation smoke use `--case review`. `--case repair` exercises
the alias, sibling-document, unified-diff, and failure-evidence regressions. The printed private
`report.json` records helper revision hash, commands, input hashes, expected and
observed results, and saved per-case evidence.

The root owns the full suite.

For two real Opus acceptance requests, create a private temporary Git repository. Put `helo\n` in `greeting.txt`. Save the example packet above with the repository's real absolute project root. First request review with acceptance criterion
“Identify the misspelling and propose hello; do not edit.” Read the explanation.
For the second request, set the objective to “Replace helo with hello in greeting.txt; return the unified diff”. Set the criterion to “greeting.txt contains exactly hello followed by one newline.” Use patch mode.

Inspect and separately apply the checked patch. Make sure that the bytes match exactly. Record both helper artifact directories and exact
inputs. These are two real subscription requests, not part of the fake suite.
Never send them automatically when installing or validating the helper.

For native shared-skill discovery, start a normal interactive Claude session. Use its local `/skills` listing. Exit before you submit a model prompt. Make sure that shared skill names appear. This check is separate from the safe-mode bridge,
which deliberately disables native discovery and transmits explicit bundles.

## Ownership and provenance

The private ownership manifest is `.state/links.json` beneath this new skill.
The destination link points to the catalogue entry, preserving an installed root
alias as a shared single source without modifying its original target.
Synchronization removes only stale links whose exact path and target match a manifest entry. It never takes ownership of existing matching links, deletes unmanaged links, or overwrites independent files/directories. Conflicts are recorded
and make synchronization fail. Native skills remain a shared single source.

The helper is an original implementation. Workflow inspiration was supplied from
`jiangzichuan618/claude-code-collab` at
`da9293c1b157ed836d4219fee2282ec967aa308f`, `sendbird/cc-plugin-codex` at
`19e565151f35b328a5b9433df351bd8f3818fdc7`, and the reverse-direction
`openai/codex-plugin-cc` at `db52e28f4d9ded852ab3942cea316258ae4ef346`.
No upstream implementation or prose was copied.

## Mandatory communication policy

The generated bundle includes `communication_policy` from the approved `writing-for-agents` catalogue root.
It contains the complete `references/controlled-english.md`, `references/ste-rule-map.md`, and `references/software-terms.md` documents.
Each document includes its path, text, and SHA-256.
Containment, symlink, and sensitive-content checks still apply.
Missing policy material stops the request before model invocation.

The input packet schema does not accept a policy override.
The complete encoded bundle remains subject to the existing 256 KiB limit, including the communication policy.
Claude must apply the policy to its explanation and generated prose.
It must preserve exact scoped source data and an explicit request for another output language.


## Selected Ponytail plugin instructions

The input schema stays unchanged.
Use plain upstream names in skills selections, such as ponytail-review.
Native host commands use the plugin namespace instead.
The helper does not discover or execute installed plugin-cache contents.

The fixed source is ~/.codex/third-party/ponytail at the revision in
[ponytail-source.json](ponytail-source.json).
The registry supplies the six allowed entry paths and document hashes.
The helper verifies the identity, containment, regular files, and hashes before a request.
A selected user/plugin name conflict fails closed.
Requests without selected Ponytail material need no plugin checkout or compatibility file.

Core selection requires one standalone objective line: Ponytail level: full, lite, or ultra.
Missing, unknown, conflicting, inline, and off levels fail for core selection.
One-shot skills do not require a core level.
With off or an unknown level, omit the core skill.

The generated bundle adds ponytail source, mode, and compatibility-policy metadata.
This metadata does not add input fields.
The policy at ~/.codex/ponytail-policy.md applies to the bundled upstream text.
The gain skill also receives the registered README and benchmark.
Their navigation links do not cause additional reads.
Instruction entry links and explicit references must remain registered.
Every document counts toward the existing packet size limit.

Run the focused fake workflows with --case ponytail.
They cover the six selections, levels, source hashes, missing material, path escapes, conflicts, and packet limits.
The full suite also includes those cases.
