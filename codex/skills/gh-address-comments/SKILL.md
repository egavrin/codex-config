---
name: gh-address-comments
description: "Address review/issue comments on the open GitHub PR for the current branch with the gh CLI. First, do a check of gh authentication. If authentication is absent, ask the user to authenticate."
metadata:
  short-description: Address comments in a GitHub PR review
---

# PR Comment Handler

Find the open PR for the current branch. Address its comments with gh CLI. Run all `gh` commands with elevated network access.

First, authenticate `gh` (for example, run `gh auth login` once). Then, run `gh auth status` with escalated permissions (include workflow/repo scopes). This check shows that access is available for `gh` commands. If sandboxing blocks `gh auth status`, run it again with `sandbox_permissions=require_escalated`.

## 1) Inspect comments needing attention
- Run scripts/fetch_comments.py. It prints all comments and review threads on the PR.

## 2) Ask the user for clarification
- Number all review threads and comments. For each item, summarize the required fix.
- Ask the user which numbered comments should be addressed

## 3) If user chooses comments
- Apply fixes for the selected comments

Notes:
- If gh encounters authentication or rate issues during work, ask the user to authenticate again with `gh auth login`. Then, retry.
