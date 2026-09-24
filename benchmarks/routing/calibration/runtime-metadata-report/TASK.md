# Add opt-in observed runtime metadata reporting

Extend the deployment-token-report tool with an opt-in
`--include-runtime-metadata` JSON mode that reports structured execution
metadata observed in session records for the main session and every included
child session.

Required behavior:

- Without the new flag, preserve the existing six-column Markdown output
  byte-for-byte and preserve the existing schema-version-1 JSON shape and
  values.
- With `--include-runtime-metadata --format json`, emit schema version 2. Keep
  all existing top-level fields and token rows unchanged, and add a `sessions`
  array with one object per included root or descendant session.
- Each session object contains exactly `session_id`, `agent`, `task`, `model`,
  `reasoning_effort`, and `service_tier`. Use `main agent` and a null task for
  the root; use the observed role and task for children.
- Read `model`, `reasoning_effort`, and `service_tier` only from structured
  session metadata. Preserve explicit strings. Represent absent or null values
  as null; never infer a tier or other value from prose, task names, model names,
  profiles, or local configuration.
- Preserve heterogeneous metadata for separate sessions sharing the same role
  or task path rather than silently merging it. Sort `sessions`
  deterministically by session timestamp and then session ID.
- Preserve deployment-window selection, ancestry traversal, guardian exclusion,
  role quantities, token totals, warning behavior, and incomplete trailing
  record handling. Ignore unknown metadata fields without losing known values.
- Continue reading message prose only for the existing exact deployment-marker
  boundary. Metadata-like prose must not affect the new fields.
- Update the packaged skill contract, explanatory architecture documentation,
  and deterministic tests. Use Python's standard library only.

Do not change orchestration routes, agent models, lifecycle mutation behavior,
or the default report format.

Run:

```sh
python3.12 -B scripts/test_deployment_token_report.py -q
python3.12 -B scripts/test_workflow_runtime.py -q
```
