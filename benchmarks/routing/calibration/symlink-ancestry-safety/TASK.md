# Harden lifecycle mutation containment

The lifecycle runtime promises conservative ownership and transaction-wide
rollback, but a mutation can currently traverse a symlink located above an
already-existing target parent. Harden the mutation boundary so lifecycle work
never reads, creates, replaces, deletes, backs up, or cleans content through an
existing symlink anywhere in a target's owned path ancestry.

Required behavior:

- Reject unsafe ancestry before any live target changes, even when an unsafe
  target appears after valid targets in the same operation plan.
- Never create, alter, or remove content outside the intended project or
  Codex-home ownership roots.
- Cover create, replace, delete, backup, and cleanup behavior consistently.
- Preserve original bytes and file modes on failure, and leave no transaction
  temporary files or newly created directories behind.
- Preserve successful behavior for ordinary directory trees, existing
  install/update/enable/disable/personalize/remove semantics, unrelated user
  content, and structured CLI error reporting.
- Keep behavior portable. Tests may skip symlink-specific cases only when the
  platform genuinely cannot create symlinks.
- Add deterministic regression coverage and update the lifecycle architecture
  documentation to describe the verified boundary accurately.

Do not change orchestration routes, agent models, release contents, or unrelated
product behavior. Use Python's standard library only.

Run:

```sh
python3.12 -B -m unittest -v scripts.test_workflow_runtime.TransactionTests
python3.12 -B scripts/test_workflow_runtime.py -q
python3.12 -B scripts/test_deployment_token_report.py -q
```
