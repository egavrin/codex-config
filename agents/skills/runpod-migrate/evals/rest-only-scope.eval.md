# Honor a REST-only scope, and name what cannot move

## Prompt

Migrate our REST v1 calls to v2. Don't touch the GraphQL — the team still depends on it
and we don't want that churn right now.

The repo has `billing.py` on REST v1 (`/billing/endpoints`) and `account.js` on GraphQL
(`myself { clientBalance }`).

## Expected behavior

Per `runpod-migrate/SKILL.md`:

1. Treats the scope as `rest` — runs the inventory with `--scope rest` and migrates only
   the REST v1 call sites.
2. Leaves `account.js` untouched. Notes that `myself` has **no REST v2 equivalent**
   anyway, so it would have stayed on GraphQL even under a full-scope migration.
3. Migrating `billing.py`, maps v1 `/billing/endpoints` (serverless spend) to
   **`/v2/billing/serverless`**, not to `/v2/billing/endpoints`, and flags this as a
   same-name-different-meaning change.
4. Handles the response-shape change: v1 returned a bare array. V2 returns
   `{records, metadata}`.

## Assertions

- No GraphQL file is edited.
- Maps `/billing/endpoints` to `/v2/billing/serverless`. Explicitly warns that `/v2/billing/endpoints` exists and returns `200` for a different product, public endpoints. An unchanged path silently reports the wrong product.
- Report that `myself` has no v2 equivalent. Do not imply incomplete migration or complete GraphQL retirement.
