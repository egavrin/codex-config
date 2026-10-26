# Mandatory Slopo commit review

Codex and ordinary Claude sessions must review each proposed commit with Slopo.
The rule includes amendments and documentation-only commits.
Manual Git workflows and existing hooks remain unchanged.
The rule is an agent instruction, not a Git hook.

## Installation

The installed CLI is Slopo 0.9.0 from revision `cb63e8ee4c27d40f47999c96e75b18bd5816b249`.
The [source lock](slopo-source-lock.json) records the pinned source, dependencies, skill hashes, and model digest.
The distribution uses an isolated uv environment with Python 3.12.

```sh
uv tool install --python python3.12 'slopo @ git+https://github.com/rafal-qa/slopo@cb63e8ee4c27d40f47999c96e75b18bd5816b249'
OLLAMA_HOST=127.0.0.1:11434 ollama pull unclemusclez/jina-embeddings-v2-base-code:latest
```

The model requires a running local Ollama server for download and inference.
The installation starts a temporary server when no local server is available.
It binds to `127.0.0.1:11434` and disables Ollama cloud features.
It stops only the server that this installation started.
It does not install a background service or change login items.

Copy the [shared skill](../codex/skills/slopo-review/SKILL.md) to `~/.codex/skills/slopo-review` when restoring this snapshot.
Preserve an existing independent skill with the same name.
Run the existing bridge's `sync-skills` action to create the owned Claude link.
That action makes no Claude model request.
Start fresh Codex and Claude sessions to load the persistent instructions.

The skill supports `$slopo-review` in Codex and `/slopo-review` in Claude.
Its Codex metadata permits automatic selection.
Global instructions make the pre-commit step mandatory.

## Runtime boundaries

Use the bundled configuration template and upstream CLI commands.
There is no replacement launcher or analysis engine.
The local model returns 768-dimensional vectors.
Its resolved digest is `9fe680d4d58b475099d91e0d08a1eaea6cef087b0a0770f4165581a7e366afec`.

State stays in a private `slopo/` directory under the selected worktree's absolute Git directory.
Project configuration files, tracked ignore files, and user changes stay intact.
The configuration excludes credentials, dependencies, generated outputs, Git metadata, and nested agent worktree copies.
Tests remain eligible for analysis.

Every Slopo process uses `PYTHON_DOTENV_DISABLED=1`.
It loads no API keys and has no cloud fallback.
Embedding requests use the loopback endpoint only.
Global Codex models, routing, authentication, billing, and hook settings remain unchanged.

## Commit decisions

The review covers working-tree changes against a Git base, including indexed untracked code.
It is not a staged-snapshot review.
When a staged path differs from its working copy, the agent stops without changing either version.
Unrelated dirty files do not expand the task or justify unrelated fixes.

A failed check blocks the commit.
Unresolved, actionable duplication introduced by the commit also blocks it.
The agent examines reported code before classifying the finding.
False positives and deliberate duplication require a brief explanation.
A material scope or contract change returns to the user for a decision.

Normal commits use `HEAD` as the comparison base.
Amendments use the amended commit's parent.
An initial commit uses Git's empty tree.
The agent repeats the review after relevant changes and records the reviewed Git state.
Plan Mode permits proposals only, without indexing, embeddings, or commits.

## Verification and limits

Verification results are recorded in [slopo-verification.json](slopo-verification.json).
Private output and repeatable host checks stay under `~/.codex/verification/slopo-install-20261026`.
The snapshot excludes databases, reports, raw host events, credentials, and model weights.
No commit or push forms part of this installation.

Slopo supplies similarity candidates, not proof of unnecessary duplication.
Unsupported syntax, parser failures, and code below or above upstream size limits can leave coverage gaps.
The agent must report material gaps without claiming complete analysis.
Initial indexing and embedding can take longer than incremental review.
The checks do not establish general reliability or performance savings.
