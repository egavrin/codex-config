# Source and adaptation

The upstream repository is [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify).
This package uses revision `92741d162b2094ffc2fed58cfbd8ee823e9da62c`, which reports package version `0.9.95`.
The Python distribution name is `graphifyy`; its command is `graphify`.

The source references below determine the adapted behavior:

- [graphify/skill-codex.md](https://github.com/Graphify-Labs/graphify/blob/92741d162b2094ffc2fed58cfbd8ee823e9da62c/graphify/skill-codex.md) supplies the upstream agent workflow.
- [graphify/cli.py](https://github.com/Graphify-Labs/graphify/blob/92741d162b2094ffc2fed58cfbd8ee823e9da62c/graphify/cli.py) defines extraction, automatic incremental updates, query commands, and query stamps.
- [graphify/detect.py](https://github.com/Graphify-Labs/graphify/blob/92741d162b2094ffc2fed58cfbd8ee823e9da62c/graphify/detect.py) defines source discovery and ignore rules.
- [graphify/__main__.py](https://github.com/Graphify-Labs/graphify/blob/92741d162b2094ffc2fed58cfbd8ee823e9da62c/graphify/__main__.py) defines CLI initialization and automatic skill refresh.
- [graphify/querylog.py](https://github.com/Graphify-Labs/graphify/blob/92741d162b2094ffc2fed58cfbd8ee823e9da62c/graphify/querylog.py) defines optional query logs and their disable flag.

The local skill text, launcher, and workflow tests are original adaptations for this installation.
They replace the upstream agent workflow with bounded local AST extraction and guarded graph reads.
The local launcher excludes Claude worktree copies from each parent graph and its freshness checks.
They do not copy automatic model selection, parallel agent dispatch, external hooks, or MCP activation.
The shared skill remains eligible for implicit invocation in Codex and normal model invocation in Claude.

[LICENSE](../LICENSE), [LICENSE-MIT](../LICENSE-MIT), and [NOTICE](../NOTICE) are exact copies from the pinned upstream revision.
The installation owner retains package-installation evidence outside this skill.
