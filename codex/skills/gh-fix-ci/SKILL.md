---
name: "gh-fix-ci"
description: "Use when a user asks to diagnose or fix failed GitHub PR checks in GitHub Actions. Inspect checks and logs with `gh`. Summarize the failure context and propose a fix plan. Implement only after explicit approval. External providers (for example Buildkite) are outside scope. Report only their details URL."
---


# Gh Pr Checks Plan Fix

## Overview

Use gh to find failed PR checks. Fetch GitHub Actions logs for actionable failures. Summarize the failure excerpt and propose a fix plan. Implement after explicit approval.
- If a plan-oriented skill (for example `create-plan`) is available, use it. Otherwise, draft a concise plan inline. Request approval before implementation.

Prereq: authenticate with the standard GitHub CLI once (for example, run `gh auth login`), then make sure that `gh auth status` succeeds (repository + workflow scopes are typically required).

## Inputs

- `repo`: path inside the repository (default `.`)
- `pr`: PR number or URL (optional, defaults to current branch PR)
- `gh` authentication for the repository host

## Quick start

- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
- Add `--json` if you want machine-friendly output for summarization.

## Workflow

1. Do a check of gh authentication.
   - Run `gh auth status` in the repo.
   - If unauthenticated, ask the user to run `gh auth login` (ensuring repository + workflow scopes) before proceeding.
2. Resolve the PR.
   - Prefer the current branch PR: `gh pr view --json number,url`.
   - If the user provides a PR number or URL, use that directly.
3. Inspect failing checks (GitHub Actions only).
   - Preferred: run the bundled script (handles gh field drift and job-log fallbacks):
     - `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
     - Add `--json` for machine-friendly output.
   - Manual fallback:
     - `gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow`
       - If a field is rejected, run again with the available fields reported by `gh`.
     - For each failing check, extract the run id from `detailsUrl` and run:
       - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha`
       - `gh run view <run_id> --log`
     - If the run log says it is still in progress, fetch job logs directly:
       - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > "<path>"`
4. Scope non-GitHub Actions checks.
   - If `detailsUrl` is not a GitHub Actions run, label it as external and only report the URL.
   - Do not attempt Buildkite or other providers. Keep the workflow focused.
5. Summarize failures for the user.
   - Provide the failing check name, run URL (if any), and a concise log snippet.
   - Call out missing logs explicitly.
6. Create a plan.
   - Use the `create-plan` skill to draft a concise plan and request approval.
7. Implement after approval.
   - Apply the approved plan, summarize diffs/tests, and ask about opening a PR.
8. Examine status again.
   - After changes, suggest re-running the relevant tests and `gh pr checks` to make sure that the result is correct.

## Bundled Resources

### scripts/inspect_pr_checks.py

Fetch failing PR checks, pull GitHub Actions logs, and extract a failure snippet. Exits non-zero when failures remain so it can be used in automation.

Usage examples:
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "123"`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "https://github.com/org/repo/pull/123" --json`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --max-lines 200 --context 40`
