# Claude routing audit, 2026-10-21

The audit supports removal of automatic Claude implementation routing.
The saved configuration now uses native model-aware delegation.
Claude remains available only after an explicit user request.

## Sources and method

The audit covers October 15–21, through 10:36 Europe/Moscow.
Sources are local Codex conversation records and retained bridge status files.
It identifies 139 distinct helper operations by artifact ID.
The 49 model requests are confirmed requests, not proof of complete retention of every session.
Missing or truncated records can hide additional requests.
Final summaries take precedence over progress events.
Fake CLI fixtures and duplicate mentions are excluded.

The conversation records recover 87 operations whose temporary directories are absent.
Of those operations, 31 are model requests, 48 are preflights, and eight are doctor checks.
The retained status files supply another 52 operations: 18 model requests, 28 preflights, and six doctor checks.
These source groups overlap in conversation mentions, but each artifact ID counts once.

For recovered summaries, the actual command identifies preflight operations.
A complete packet with a final model result identifies a model request.
The recorded encoded mode size distinguishes `patch` from `review`: seven and eight bytes, respectively.
Authentication-only checks have no bundled packet and count as doctor operations.
The classification agrees with all 50 retained statuses that also have recovered conversation summaries.
The saved operation inventory records each classification and its available source.

## Model outcomes

| Mode | Requests | Bridge success | Rejected diff | Cancelled | Explicit total timeout |
| --- | ---: | ---: | ---: | ---: | ---: |
| Patch | 35 | 23 | 9 | 2 | 1 |
| Review | 14 | 14 | 0 | 0 | 0 |
| Total | 49 | 37 | 9 | 2 | 1 |

Bridge success does not establish product acceptance or prove that a patch was applied.
The helper permits an empty diff.
All six successful recent patch requests record nonempty changed paths.
The historical success summaries do not retain that detail.
Completed patch responses exclude cancellation and timeout: nine of 32 were rejected, or 28.1%.
Across all 35 patch requests, 23 report bridge success, or 65.7%.

| Moscow date | Model requests |
| --- | ---: |
| 2026-10-15 | 14 |
| 2026-10-16 | 16 |
| 2026-10-17 | 1 |
| 2026-10-18 | 0 recorded |
| 2026-10-19 | 5 |
| 2026-10-20 | 9 |
| 2026-10-21, through 10:36 | 4 |

## Recent complete telemetry

October 19–21 has 18 requests with retained status records.
Twelve are patch requests: six pass validation, five fail validation, and one is cancelled.
All six review requests complete successfully.
Five of 11 completed patch responses fail validation, or 45.5%.
Film Studio has six patch requests: one pass, four rejected diffs, and one cancellation.
Four of its five completed patch responses fail validation, or 80%.
All three patch requests on October 21 fail validation.
Conversation records and native session metadata confirm their subsequent Astra High handoffs.
This proves additional native implementation work, not a complete rewrite of every idea or source change.

The 18 retained requests consume 6,129.201 seconds of elapsed request time.
The five rejected patches consume 2,973.574 seconds: 49 minutes and 33.574 seconds.
That is 48.5% of the recorded request time.
These measurements exclude packet preparation, native implementation, and acceptance work.
The earlier requests lack complete retained duration and usage data.

The 17 completed recent requests report 722,139 output tokens.
The five rejected patches report 376,869 output tokens, or 52.2% of that total.
Reported output usage can include reasoning and does not measure visible patch size.
Token telemetry and CLI cost estimates do not establish subscription charges or quota consumption percentages.
The cancelled request has no final usage data.

## Failure evidence

Across the week, two diffs have invalid file headers and two have invalid hunk counts.
Five more diffs fail `git apply --check --whitespace=error`.
Those generic errors do not preserve the exact Git diagnostic.
They do not establish whether context, whitespace, or another application condition caused each rejection.
The bridge checks source baselines before this Git check and reports stale baselines separately.
None of these nine failures is classified as a stale baseline.

All five recent rejected-patch requests exit the Claude CLI with code zero.
Thus the recent failures concern returned patch artifacts, not CLI crashes or recorded usage limits.
The restricted companion has no tools and cannot run Git against the supplied source.
It returns a diff that Codex validates after generation.
This design leaves format and application errors visible only after the request completes.
It does not establish that the underlying model cannot implement the task.

## Other helper operations

The 76 preflights include 23 local validation failures.
The 14 doctor checks include three subscription-authentication failures.
These checks are excluded from the 49 model requests.
They add preparation overhead but have no measured model usage in this audit.

## Routing change and verification

Automatic primary, fallback, and review routes now exclude Claude.
Sol owns Direct work and delegates substantial packages to one Astra High owner.
Astra Extra High remains conditional on evidence from High Astra.
Codex owns integration and acceptance.
The companion skill has `policy.allow_implicit_invocation: false`.
Explicit manual requests retain subscription authentication and all existing request and patch checks.

The change preserves model IDs, reasoning, service tiers, context windows, permissions, and named native experiments.
The shared skill links remain intact.
The bridge implementation, tests, authentication, and billing settings are unchanged by this task.
The repository snapshot mirrors the targeted changes.
No commit or push was requested for this audit.

Both skill copies pass `quick_validate.py`.
The 55 saved structural and preservation assertions pass.
TOML and YAML parse, local skill links resolve, and native route requirements agree.
This task makes no new Claude request and starts no subagent.
The runtime must load the revised developer instructions in a fresh Codex session.
Existing sessions can retain earlier instructions.

## Reproduce

Run `python3 audit.py` in this evidence directory to recompute the aggregate statistics.
`operations.json` contains the sanitized source inventory.
`validation.json` records the structural checks.
`changes.diff` isolates changes made by this task from earlier worktree edits.
`extract.py` and `count_launches.py` preserve the collection procedure.
They use the original private scratch directory for intermediate outputs.
Raw conversations, packets, model reasoning, and credentials are not copied into this report.
