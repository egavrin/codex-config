# Codex routing benchmark

This public benchmark compares the outcomes of two pinned coordinator profiles:
GPT-5.6 Terra Medium Fast and GPT-6 Luna High Standard. Substantive fixtures ask
each coordinator to delegate one bounded package to GPT-6 Sol Medium Standard.
When a coordinator completes directly or the runtime fails, that result remains
part of its profile's outcome. Actual root and child sessions are reported
separately from requested settings.

The 24 scored fixtures have six categories with four tasks each: direct, local,
multi-component, diagnosis, security, and read-only review. Twelve are Python,
eight TypeScript, and four CLI/configuration tasks. All code, prompts, and
external checks are synthetic and publishable. The earlier three tiny pilot
tasks and two archived real-task pairs are recorded in `calibration.json` as
calibration material only; their results are not included in a scored cycle.

The completed [2026-09-23 results](RESULTS-2026-09-23.md) include per-class
scores, completeness limits, and the decision to retain the current default.

## Layout and integrity

- `tasks.json` pins each fixture's source hash, external check hash, deterministic
  seed commit, task class, expected route, and timeout.
- `fixtures/<id>/start` is the only tree copied into an agent workspace.
  `fixtures/<id>/checks.json` stays outside that workspace, and the shared
  `acceptance.py` runs independently after Codex exits.
- A cycle gets a unique directory under ignored `artifacts/`. It contains
  isolated Git repositories, raw local logs, acceptance output, and records.
  Do not publish those logs: they can contain machine paths or task content.
- `cycle-meta.json` records hashes of benchmark profiles, prices, active
  configuration and global instructions, plus the Codex version. A resumed
  cycle refuses configuration drift.

The runner uses the installed Codex authentication and global instructions, but
passes explicit model, effort, tier, and role-file overrides. It never writes
to the active Codex configuration or to the repository's `codex/` snapshot.

## Commands

Run from the repository root with Python 3.12+ and Node.js available:

```sh
python3.12 -B -m benchmarks.routing.make_fixtures
python3.12 -B benchmarks/routing/runner.py list
python3.12 -B benchmarks/routing/runner.py self-check
python3.12 -B benchmarks/routing/runner.py dry-run
python3.12 -B benchmarks/routing/runner.py run
python3.12 -B benchmarks/routing/runner.py analyze --cycle benchmarks/routing/artifacts/<cycle>
python3.12 -B benchmarks/routing/runner.py verify --cycle benchmarks/routing/artifacts/<cycle>
```

If an acceptance rubric needs a documented correction after a cycle, use:

```sh
python3.12 -B -m benchmarks.routing.combine --non-review <cycle> --review <review-cycle> --output <new-local-directory>
```

This rechecks every saved workspace against the current checker and retains
both original and final review grades. The two-cycle procedure used for the
2026-09-23 result is documented in its report; a new prospective experiment
should freeze the checker first.

The materializer is for fixture maintenance. It regenerates `tasks.json` hashes
after a reviewed change to `make_fixtures.py` or `acceptance.py`; do not run it
during a cycle. `self-check` confirms that every seed has a working baseline
case and a failing target case. To try one case without launching the whole
matrix, pass `--task <id> --arm luna --repeats 1 --timeout 120` to `run`.

The full schedule is 24 tasks × 2 arms × 3 fresh repeats = 144 planned runs.
Run order alternates arms. The runner stops scheduling further delegated cases
after two unresolved empty collaboration waits, and stops an arm after three
consecutive runtime failures. Skipped cases make the cycle incomplete; they
are not scored as model failures.

## Measurements and decision rule

The rollout importer reads session metadata, parent links, model/effort, and the
**last cumulative thread usage** for each root and child. It does not sum
cumulative usage records. Missing telemetry stays missing. Codex rollout files
do not reliably expose the effective tier, so credit calculations distinguish
a configured-tier estimate from Standard/Fast bounds. Rates are pinned in
`prices.json` with the official source and effective date; Codex credits are
not API dollars or an observed subscription debit.

For each task and arm, quality Q is accepted repeats / all repeats. C is credits
spent across all repeats / accepted repeats; T is elapsed time across all
repeats / accepted repeats. With zero successes, cost and time receive zero
score. Each task score is 100 × (0.5 Q + 0.3 best_C/C + 0.2 best_T/T), where
best_C and best_T are the better arm's result on that same task. All 24 tasks
have equal weight; category scores are also reported. A paired bootstrap over
tasks estimates the score and quality intervals.

A default change can be recommended only after all 144 runs, no critical
acceptance defects, a positive 95% score interval, a quality lower bound no
worse than five percentage points below Terra, complete cost data, and a ranking
that survives the unknown-tier bounds. Otherwise the report keeps the current
default and names the missing evidence. It never changes the default itself.
