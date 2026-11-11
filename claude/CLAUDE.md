# Personal writing instructions

Use English for user responses, agent messages, and new technical documents.
An explicit request for another output language takes precedence.
Read and apply the shared writing profile and its software terminology.
Preserve exact identifiers, commands, quotations, and required product text.
The language profile does not change permissions, task scope, or agent routing.

@../.codex/skills/writing-for-agents/references/controlled-english.md
@../.codex/skills/writing-for-agents/references/software-terms.md

## Default reply style

Use Caveman for chat replies from the start of every session.
Put the answer first. Keep technical details and follow the shared language rules.
If the user says `stop caveman` or `normal mode`, turn Caveman off for the current session.


@../.codex/skills/caveman/SKILL.md

# Ponytail compatibility

Ponytail solution preferences do not replace the shared writing or engineering policy.
@../.codex/ponytail-policy.md

## Telegram text delivery

When the user explicitly asks you to send text through Telegram, read `~/.codex/telegram-guide.md` before delivery.
The guide covers credentials, destinations, safe requests, and delivery results.
This reference does not authorize a message by itself.

## Graphify code discovery

For architecture, dependency tracing, or substantial repository discovery, use the shared `graphify` skill when appropriate.
Read `~/.codex/skills/graphify/SKILL.md` before its first use.
For a small edit at a known location, use focused source searches directly.
Graphify does not change routing, permissions, or Plan Mode.

## Untangle before agent merges

Before an agent performs a merge, review the proposed changes for actionable structural clutter.
Compare the source with the actual target branch merge base and inspect relevant connected code.
For a remote merge, verify the current remote source and target revisions.
Do not block on similarity, size, style, or deliberate duplication alone.
Explain material deliberate duplication and false positives.
Resolve evidenced findings within scope, or stop and report the unresolved issue.
If the review cannot be completed, stop and report the missing evidence.
Record the reviewed source and target revisions, checks, and finding dispositions.
Immediately before merging, verify both revisions and repeat affected checks if either changed.
Do not require a whole-repository refactor for this review.
This rule does not authorize a merge or change manual Git workflows.

## Mandatory Slopo commit review

Before creating or amending any Git commit, follow `~/.codex/skills/slopo-review/SKILL.md`.
Complete the review and resolve blocking findings before committing.
This requirement includes documentation-only commits.
It does not authorize commits or change Plan Mode, Git hooks, or manual workflows.
