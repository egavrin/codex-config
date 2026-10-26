# Personal writing instructions

Use English for user responses, agent messages, and new technical documents.
An explicit request for another output language takes precedence.
Read and apply the shared writing profile and its software terminology.
Preserve exact identifiers, commands, quotations, and required product text.
The language profile does not change permissions, task scope, or agent routing.

@../.codex/skills/writing-for-agents/references/controlled-english.md
@../.codex/skills/writing-for-agents/references/software-terms.md

# Ponytail compatibility

Ponytail solution preferences do not replace the shared writing or engineering policy.
@../.codex/ponytail-policy.md

## Graphify code discovery

For architecture, dependency tracing, or substantial repository discovery, use the shared `graphify` skill when appropriate.
Read `~/.codex/skills/graphify/SKILL.md` before its first use.
For a small edit at a known location, use focused source searches directly.
Graphify does not change routing, permissions, or Plan Mode.

## Mandatory Slopo commit review

Before creating or amending any Git commit, follow `~/.codex/skills/slopo-review/SKILL.md`.
Complete the review and resolve blocking findings before committing.
This requirement includes documentation-only commits.
It does not authorize commits or change Plan Mode, Git hooks, or manual workflows.
