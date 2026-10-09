# Bridge interface and acceptance

The helper requires Python 3.9+ (including `Path.is_relative_to`), Git, and an
installed Claude CLI supporting `--safe-mode` and `--restricted`. It uses only
Python's standard library and the existing subscription login. It never executes
selected skill scripts. CLI flags are verified from the installed help rather
than assuming online documentation matches the installed release.

```bash
python3 ~/.codex/skills/claude-collab/scripts/bridge.py doctor
python3 ~/.codex/skills/claude-collab/scripts/bridge.py sync-skills
python3 ~/.codex/skills/claude-collab/scripts/bridge.py run --mode review --packet /absolute/private/packet.json
python3 ~/.codex/skills/claude-collab/scripts/bridge.py run --mode patch --packet /absolute/private/packet.json
```

`--claude-bin /absolute/path` goes before the action when selecting a specific
installed executable or a fake executable for testing. `run --timeout SECONDS`
accepts a positive value up to 300 (default 300). A timeout terminates the helper's
process group, including descendants; it does not kill unrelated Claude sessions.
The helper never retries a request. CLI/authentication errors stop the run.

## Packet schema

UTF-8 JSON, with exactly these fields. Use absolute `project_root`; all project
paths are canonical relative paths beneath that root. For patches inside a Git
repository, use its top-level directory as the project root (subdirectory roots
are rejected to prevent Git silently skipping paths). Select a root that contains
the required project instructions and sources. Supply scoped instruction documents
rather than the entire conversation. All arrays are required; unused ones may be
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
  automatically included; absent paths permit proposed text additions.
- `project_instructions`: paths to required project instruction documents.
- `skills`: objects with `name` and optional `references` (relative to that skill's
  directory). The root selects skills. The helper reads their entire `SKILL.md`
  and recursively follows local Markdown document links. It skips executable and
  image/PDF resources; select needed text references explicitly. Required documents
  named only in prose must be included in `references`. Installed directory aliases
  are approved user skill roots. Linked
  sibling documents such as `../codebase-design/DEEPENING.md` resolve through the
  visible user skill catalogue, including trusted directory aliases. Hidden/system
  entries and aliases into plugin caches are excluded. Nested symlinks and
  references escaping the catalogue fail closed. A missing linked document requires
  narrowing or correcting the selected skill context before retrying.
- `sources`: additional read-only source paths, beyond the auto-included scope.
- `diffs`: relevant unified diffs as strings; send only scoped, necessary evidence.
- `uncertainties`: explicit questions for the companion to resolve or report.

All source and reference inputs must be UTF-8 text. The complete automatically
bundled JSON must be at most 256 KiB. The helper rejects sensitive filenames,
common credential patterns, NUL bytes, project path traversal, and nested
symlinks. Only installed user skill root aliases receive the explicit exception
described above. Manually inspect selected content too: no detector recognizes all secrets or private data.
Do not redact a required technical fact silently; report the resulting uncertainty.

Packet contents go through stdin. The CLI runs in a fresh private temporary
working directory with safe/restricted mode, empty tools, empty setting sources,
empty explicit settings and MCP configuration, slash commands disabled, a fixed
bounded system prompt, Opus, print JSON, no session persistence, plan permissions,
and one turn. Administrator-managed policy may still apply according to Claude's
CLI contract. Session isolation does not modify global settings. Child environment
uses a small allowlist for home, executable search, locale, temporary directory,
and user identity; API keys, OAuth overrides, provider configuration, proxies, and
runtime injection variables are not inherited. Keychain OAuth remains available.

## Response and applying a patch

Claude returns a JSON object with exactly `explanation` and `diff` strings inside
the CLI JSON result. Review mode requires an empty `diff`. Patch mode accepts an
empty diff when no changes are needed. Malformed results fail explicitly. Any
reported non-Opus model causes failure. The requested model is always recorded;
a CLI that omits model telemetry cannot independently prove its resolved alias.

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
match `scope` exactly. File hashes captured before the request must still match
before validation; no forced application or conflict resolution is attempted.

A private `claude-collab-*` temporary directory is printed on success or failure.
It contains `status.json`, `sync.json` when relevant, and, on success,
`response.json` plus `patch.diff` when nonempty. A schema-validated,
secret-checked response is saved before applicability validation, so an invalid
patch remains diagnosable in `response.json`; `status.json` explicitly records
`status: failure`, `patch_validation: failed`, and `applied: false`. Such a response
is not an accepted patch. Malformed or secret-containing responses are not saved.

Status records the helper hash,
packet hash and size, scope baseline SHA-256 values (`null` for absent files),
project root, command without packet contents, requested/reported models, numeric
usage when supplied, cost estimate when supplied, duration, result, and applied=false.
Raw failed provider output and the assembled packet are not retained. Errors are
sanitized. Artifacts have user-only permissions; preserve needed evidence and
remove only the generated directory when finished.

Immediately before applying, verify every `baseline_sha256` entry in `status.json`
against the project file (and verify that paths have not become symlinks). Absent
files must remain absent. Then, from `project_root`:

```bash
git apply --check --whitespace=error /absolute/artifact/patch.diff
git apply --whitespace=error /absolute/artifact/patch.diff
```

This separate Codex step is intentional: the bridge does not mutate project files.
Codex reviews the final diff, runs proportionate checks, and records acceptance.

## Repeatable fake and real smoke checks

The black-box fake executable suite covers review and patch success, text add/delete,
malformed JSON, auth mismatch before request, rate-limit errors, process-group
timeout, stale/conflicting/escaping/binary/mode-changing patches, standard unified patches,
retained safe failure evidence, secrets, installed skill aliases, approved sibling
documents, nested symlinks,
reference escape, environment/tool restrictions, explicit bundles, and safe shared
skill synchronization. It never sends a real request:

```bash
python3 ~/.codex/skills/claude-collab/scripts/test_bridge.py
```

For a narrow implementation smoke use `--case review`; `--case repair` exercises
the alias, sibling-document, unified-diff, and failure-evidence regressions. The printed private
`report.json` records helper revision hash, commands, input hashes, expected and
observed results, and saved per-case evidence. The root owns the full suite.

For two real Opus acceptance requests, create a private temporary Git repository
with `greeting.txt` containing `helo\n` and save the example packet above with its
real absolute project root. First request review with acceptance criterion
“Identify the misspelling and propose hello; do not edit.” Read the explanation.
For the second request, update objective to “Replace helo with hello in greeting.txt;
return the unified diff” and criterion to “greeting.txt contains exactly hello
followed by one newline.” Use patch mode, inspect and separately apply the checked
patch, and verify exact bytes. Record both helper artifact directories and exact
inputs. These are two real subscription requests, not part of the fake suite.
Never send them automatically when installing or validating the helper.

For native shared-skill discovery, start a normal interactive Claude session and
use its local `/skills` listing, then exit before submitting a model prompt. Confirm
shared skill names appear. This check is separate from the safe-mode bridge,
which deliberately disables native discovery and transmits explicit bundles.

## Ownership and provenance

The private ownership manifest is `.state/links.json` beneath this new skill.
The destination link points to the catalogue entry, preserving an installed root
alias as a shared single source without modifying its original target.
Synchronization removes only stale links whose exact path and target match a
manifest entry; it never adopts ownership of existing matching links, deletes
unmanaged links, or overwrites independent files/directories. Conflicts are recorded
and make synchronization fail. Native skills remain a shared single source.

The helper is an original implementation. Workflow inspiration was supplied from
`jiangzichuan618/claude-code-collab` at
`da9293c1b157ed836d4219fee2282ec967aa308f`, `sendbird/cc-plugin-codex` at
`19e565151f35b328a5b9433df351bd8f3818fdc7`, and the reverse-direction
`openai/codex-plugin-cc` at `db52e28f4d9ded852ab3942cea316258ae4ef346`.
No upstream implementation or prose was copied.
