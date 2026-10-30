# Local commands

The launcher uses Python 3.9 or later and the `graphify` executable on `PATH`.
The installed package is `graphifyy==0.9.95` from the pinned revision in [provenance.md](provenance.md).
The launcher resolves the CLI's Python interpreter from its installed entry point.

## Public interface

```text
python3 ~/.codex/skills/graphify/scripts/graphify_local.py ACTION --root /absolute/project [--read-only] [--scoped] [--budget N] [OPERANDS]
```

| Action | Operands | Result |
| --- | --- | --- |
| `ensure` | None | Reuse a current graph or safely build an update. |
| `ensure --read-only` | None | Check the existing graph and freshness without writes. |
| `query` | One quoted question | Return relevant graph nodes and source references. |
| `path` | Two quoted node names or IDs | Return a directed dependency path. |
| `explain` | One quoted symbol or ID | Return the symbol's graph relationships. |

`--budget` applies to `query`. Its default is 1200, and its accepted range is 1 through 10000.
Queries require a fresh existing graph and never build implicitly.
All query commands block filesystem changes by the upstream Python process, including its query stamp.
Pass `--read-only` to prevent lock creation as well.

```bash
python3 ~/.codex/skills/graphify/scripts/graphify_local.py ensure --root /absolute/project
python3 ~/.codex/skills/graphify/scripts/graphify_local.py query --root /absolute/project --budget 1200 'authentication dependencies'
python3 ~/.codex/skills/graphify/scripts/graphify_local.py path --root /absolute/project 'handle_request' 'save_record'
python3 ~/.codex/skills/graphify/scripts/graphify_local.py explain --root /absolute/project 'save_record'
python3 ~/.codex/skills/graphify/scripts/graphify_local.py query --root /absolute/project --read-only 'authentication dependencies'
```

A non-Git target also requires `--scoped`.
The caller must identify a single project from the task before using that flag.
The launcher excludes `.claude/worktrees/` directories from extraction and freshness checks.
Those directories contain separate working copies. Index a required worktree as its own project root.
Other nested Git projects still cause a fallback that identifies their path relative to the selected root.
The launcher rejects unsafe roots, output symbolic links, and tracked graph output.
Graph and state reads reject symbolic links before opening them and enforce regular-file size limits.
A non-Git parent without repository markers cannot be distinguished reliably from one large project.

## Status and storage

Exit code `0` indicates success.
Exit code `2` reports a fallback or invalid arguments.
A fallback requires ordinary source search, with the reported graph limitation preserved in the answer.

The graph stays in `<project>/graphify-out/`.
The launcher records the exact root and a source-metadata fingerprint in `graphify-out/.local-state.json`.
Metadata checks include file names, sizes, modification times, change times, and relevant external Git ignore files.
State format 3 requires one rebuild of graphs from earlier fingerprint policies, including format 2.
They do not read source content or credential files.
Changes to ignored files can cause conservative refreshes.
Symlink targets and common dependency directories do not enter the fingerprint.
Files below any directory named `dist` within the project do not enter the fingerprint, consistent with the pinned scanner.
The launcher still traverses those directories to detect nested Git projects, with the other skip rules unchanged.

Builds copy the previous output to a temporary directory beside the project graph.
The CLI updates that copy, using its automatic incremental behavior.
There is no `--incremental` flag.
After validation, the launcher replaces the output directory under an exclusive lock.
A temporary `.graphify-local-backup/` retains the previous output during publication.
A later writable `ensure` recovers an interrupted publication.
A forced process termination can leave a temporary `.graphify-local-stage-*` directory for manual removal.

Git local excludes cover graph output, staging directories, and the recovery directory.
The launcher appends missing entries to Git's `info/exclude` and preserves existing text.
It does not edit `.gitignore` or `.graphifyignore`.

Locks use `<XDG_CACHE_HOME or ~/.cache>/graphify-local/locks/<SHA256-of-absolute-root>.lock`.
The directory is private to the current user.
Both shared query locks and exclusive build locks are nonblocking.
Agents must use the same launcher and cache location to share this protection.
Read-only mode opens an existing lock without creating files.
If no lock exists, read-only mode returns a fallback.

## Upstream operations

The launcher invokes these upstream operations through its environment and audit guard:

```text
graphify extract ROOT --code-only --no-cluster --no-dedup --out STAGE [credential and output exclusions]
graphify query QUESTION --budget N
graphify path FROM TO
graphify explain SYMBOL
```

Each subprocess has `GRAPHIFY_BACKEND=none`, `GRAPHIFY_NO_AUTO_REFRESH=1`, and `GRAPHIFY_QUERY_LOG_DISABLE=1`.
Provider keys and inherited `GRAPHIFY_*` options do not enter the subprocess environment.
Do not bypass the launcher for task work.
Raw query commands write a query stamp even when they do not change the graph.

The code graph omits semantic document analysis and community clustering.
Dynamic calls, unsupported syntax, and generated relationships can be incomplete.
An empty graph is valid but supplies no navigation evidence.

## Repeatable package check

```bash
python3 ~/.codex/skills/graphify/tests/workflow.py --real --evidence /absolute/evidence-directory
```

The test creates temporary project fixtures and injects CLI failures.
The `--real` option also checks the installed CLI.
The JSON evidence records source revision, script hashes, commands, inputs, and expected and observed exit codes.
