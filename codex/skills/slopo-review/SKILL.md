---
name: slopo-review
description: Review Git changes for new code duplication with local Slopo embeddings. Required before every agent-created or agent-amended commit. Also use for an explicit Slopo review.
license: AGPL-3.0-or-later
---

# Slopo review

Run this review before every commit that the agent creates or amends, including documentation-only commits.
The review uses the pinned Slopo CLI and local Ollama embeddings.
Manual Git commands and Git hooks remain unchanged.
This skill does not authorize a commit that the user has not requested or otherwise authorized.

In Plan Mode, inspect existing evidence and explain the procedure only.
Do not create files, index code, generate embeddings, or commit in Plan Mode.
For a review-only request, report findings without source edits or a commit.

## Procedure

1. Read [the local workflow](references/workflow.md) before execution.
2. Establish the exact repository or worktree, intended commit paths, and comparison base.
3. Check that every staged path matches its working copy, including additions and deletions.
4. If partial staging differs, stop and report the affected paths.
5. Preserve the index, unrelated changes, existing configuration, databases, and preexisting Ollama servers.
6. Check the pinned model digest before each database reuse.
7. Initialize a missing database with explicit `index` and `embed` commands.
8. Run native `slopo --config ABSOLUTE_CONFIG agent-review --config-version=1 --base BASE` with the required local environment.
9. Classify every reported similarity that affects the intended commit.
10. Complete the commit gate below, then stop only the Ollama server that this invocation started.

Slopo compares the full working tree and untracked files against the base.
It does not limit review to staged changes.
Read nearby code and callers only when needed to judge a finding.
Judge findings material to the intended commit and preserve unrelated dirty files.
Do not create a staged snapshot system.

## Commit gate

A successful CLI exit confirms execution, not the absence of actionable duplication.
A similarity is actionable when new duplication creates a concrete maintenance or behavior risk within the intended change.
Shared syntax or similar embeddings alone do not establish that risk.

- Block the commit after a failed check or unresolved actionable new duplication.
- Resolve actionable duplication with the smallest safe change inside the authorized scope.
- When a change expands scope or changes a contract, request the user's decision.
- Explain deliberate duplication and false positives with a concrete reason.
- Do not suppress findings merely to obtain a clean report.
- Run the review again after relevant source changes, staging changes, or index updates.
- Confirm that the reviewed Git state still matches immediately before the commit.

Record the repository, base, Git state, exact commands, exit codes, findings, dispositions, and coverage limits before the commit.
Store private evidence in the worktree's Slopo state directory.
For documentation-only commits, run the review and report whether indexed code changed.
Report “no indexed-code changes” only when the observed index and diff support that result.

The final summary identifies affected paths, the duplicated responsibility, its concrete risk, and its disposition.
Summarize deliberate duplication and false positives briefly.
Do not present similarity clusters as confirmed defects.

## Limits and source

Slopo omits unsupported languages and can skip parse errors.
The default filters omit functions below 20 AST nodes, blocks below 60 AST nodes, and bodies above 10,000 characters.
A clean report does not prove complete coverage or correctness.
Report relevant omissions and parser warnings.

[Source and model pins](references/source-and-model.md) records the upstream revision, license, model digest, and adaptation.
[Black-box workflow checks](tests/workflow.py) exercise the installed CLI with synthetic local embeddings.
Read the test instructions in the source reference before a verification run.
