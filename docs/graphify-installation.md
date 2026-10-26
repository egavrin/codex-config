# Shared Graphify installation

Graphify supports local code discovery in Codex and ordinary Claude Code sessions.
The installed distribution is `graphifyy==0.9.95` from revision `92741d162b2094ffc2fed58cfbd8ee823e9da62c`.
The [source lock](graphify-source-lock.json) records dependencies, source hashes, and adapted file hashes.

## Installation and restoration

The shared source lives at `~/.codex/skills/graphify`.
Claude uses the owned link `~/.claude/skills/graphify` to that same directory.
Codex supports `$graphify`. Ordinary Claude sessions support `/graphify`.
Both hosts can select the skill automatically for relevant discovery tasks.

To restore this installation:

1. Preserve any existing skill with the same name.
2. Copy `codex/skills/graphify` to `~/.codex/skills/graphify`.
3. Install the pinned package with a supported Python interpreter.

```sh
uv tool install --python python3.12 'graphifyy @ git+https://github.com/Graphify-Labs/graphify@92741d162b2094ffc2fed58cfbd8ee823e9da62c'
python3 ~/.codex/skills/claude-collab/scripts/bridge.py sync-skills
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/graphify
```

The `sync-skills` action maintains links only. It makes no Claude model request.
Preserve independent Claude skills when names conflict.
Keep the Graphify discovery section in global Codex and personal Claude instructions.
Start new sessions after installation.

The installation used Homebrew Python 3.12 for the isolated uv tool environment.
The launcher itself supports Python 3.9 or later.
The dependency inventory records this installation. It is not a dependency lock for every future platform.

## Operation

Read the [skill](../codex/skills/graphify/SKILL.md) and [command reference](../codex/skills/graphify/references/commands.md) before task use.
The launcher provides `ensure`, `query`, `path`, and `explain`.
It stores each project graph in `graphify-out/`.
It adds Git local excludes and preserves tracked ignore files.
Shared queries and exclusive updates use nonblocking OS locks.
A busy graph causes ordinary source search without a retry loop.

The initial profile uses local code-only extraction without community clustering.
It selects no model backend and loads no API keys.
The launcher blocks upstream network requests and query writes through a Python audit guard.
It disables automatic skill replacement and excludes recognized credential paths.
It starts no hooks, watcher, or MCP service.
The package supplies a `graphify-mcp` executable, but this installation does not register it.

In Plan Mode or a read-only task, every command requires `--read-only`.
That mode uses existing graphs and locks without creating either.
Missing or stale material causes direct source search.
Global model settings, authentication, billing, and agent routes remain unchanged.

## Verification on 2026-10-26

**Structural checks:** The skill validator, YAML metadata, local references, shared link, and upstream license hashes passed.
The metadata enables implicit invocation and includes `$graphify` in its default prompt.
Global Codex configuration and personal Claude settings match their original bytes.
The global instruction changes contain only the bounded discovery section.

**Workflow checks:** Black-box tests passed with a substitute CLI and the installed upstream CLI.
They cover initial extraction, graph reuse, source additions, edits, and deletions.
They cover two projects, query actions, stale data, malformed data, and extraction failure.
They verify read-only behavior, lock contention, output exclusion, and preservation of the previous valid graph.
Audit traps confirm that graph and state symlinks do not open their targets.

To repeat the package workflow:

```sh
python3 ~/.codex/skills/graphify/tests/workflow.py --real --evidence /absolute/private-evidence
```

**Host checks:** Fresh, nonpersistent sessions received a temporary four-file Python project.
Neither positive prompt named the Graphify skill.
Both hosts selected it and returned `submit_order → place_order → persist_order` with source references.
Both hosts skipped Graphify for a tiny replacement at a known location.
All fixture source hashes stayed unchanged.

Codex used `gpt-6.1-sol` with High reasoning. Its service tier was not exposed.
Claude reported `claude-opus-5-5` through the existing subscription login.
The Claude test limited available tools and disabled external MCP servers.
One compound Bash command failed the test's permission filter. A subsequent allowed command completed the graph query.
This was a harness permission result, not a Graphify extraction failure.
The Codex test created a temporary trusted-project entry. Acceptance removed that entry and verified the original configuration hash.

The [verification summary](graphify-verification.json) contains sanitized results and the exact test prompts.
Private workflow output, host events, fixture files, and installation evidence remain under `~/.codex/verification/graphify-install-20261026`.
Raw host events, credential files, graph caches, and temporary trust entries stay outside this snapshot.
No commit or push forms part of this update.

## Limits

The worktree fix on 2026-10-26 excludes `.claude/worktrees/` from extraction and freshness checks.
Other nested repositories still require separate scope.
Existing state format 1 requires a graph update before reuse.
Black-box regression checks cover linked worktrees, nested Git markers, excluded source changes, and separate worktree indexing.
Film Studio's actual root and freshness scan also pass. Acceptance did not build a Film Studio graph.
The fix evidence stays under `~/.codex/verification/graphify-worktree-fix-20261026`.

Graph relationships can omit dynamic calls, unsupported syntax, and generated behavior.
Source code and runtime checks remain authoritative.
The initial code-only profile omits semantic document analysis and community clustering.
Metadata changes can cause conservative refreshes, including changes to ignored files.

The audit guard is an in-process control for the pinned Python CLI, not an operating-system sandbox.
Credential path filters cannot identify secrets embedded in ordinary source files.
Noncooperating programs do not observe the launcher's locks.
The host checks establish behavior for two small prompts, not universal automatic selection or performance gains.
No production repository was indexed during installation.
