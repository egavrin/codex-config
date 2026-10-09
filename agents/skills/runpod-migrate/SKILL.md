---
name: runpod-migrate
description: "Migrate code from the Runpod GraphQL API or REST v1 to REST v2. Inventory API versions, revise call sites, identify breaking changes, and test behavior. Use for requests to move to v2, explain v2 changes, or identify the Runpod API in existing code. For infrastructure management, use runpod-mcp or runpodctl."
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/runpod-migrate/scripts/rp_api_inventory.py:*), Bash(rg:*)
metadata:
  compatibility: Linux, macOS, Windows
  user-invocable: true
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Migrate to Runpod REST v2

Moves a codebase off the **GraphQL API** (`api.runpod.io/graphql`) and **REST v1**
(`rest.runpod.io/v1`) onto **REST v2** (`api.runpod.io/v2`).

At step 6, give the user one line for each benefit below. Match each benefit to their actual code. Do not recite them now:

- **See stock before you rent** — `GET /v2/catalog/gpus?include=AVAILABILITY&product=POD`. v1 had no
  catalog at all, so every capacity retry loop was blind.
- **Endpoints return their own job URLs** — `requestUrls.run`, no more string-building.
- **Real lifecycle states** — `PROVISIONING`/`STARTING`/`ERROR` and an `actions` list, so
  wait-loops fail fast instead of timing out.
- **Mistakes fail loudly** — unknown request fields are rejected by name, with structured
  errors and honest status codes.

The full set, organized as *if their code does X → v2 offers Y*:
**[reference/unlocks.md](reference/unlocks.md)** — open it at step 6.

## Before you touch any code

**Infer the scope, state it, and move** — do not open with a questionnaire:

| The user says | Scope |
| --- | --- |
| "migrate to v2" / nothing specific | `all` — REST v1 **and** GraphQL |
| "just the REST stuff", "leave GraphQL alone" | `rest` — REST v1 only |
| "get us off GraphQL" | `graphql` — GraphQL only |

The table resolves every phrasing, so scope is not the thing to interrupt for. State the matching row and continue. **Ask the necessary question later, at step 3**, if the inventory shows dependence on a removed v2 capability. That one
is a real fork and you cannot answer it for them.

Some things **have no v2 equivalent and must stay on GraphQL regardless of scope**:
account/billing identity (`myself`), secrets, spot/interruptible pods, cluster
create/delete. A "full" migration still leaves those calls in place. Tell the user at the start, before the final report.

**Never rewrite the serverless job API.** `https://api.runpod.ai/v2/<endpointId>/run`,
`/runsync`, `/status`, `/stream`, `/cancel` is a *different API* that happens to have
`v2` in its path. It is unchanged and out of scope. The inventory reports it separately
so you do not touch it.

## The workflow

### 1. Inventory — never migrate what you have not counted

The scanner ships **beside this file**, in the installed skill directory — not in the
user's repo. Resolve its path first. Your working directory is their project:

```bash
# 1. Claude Code plugin installs expose the plugin root:
SCAN="$CLAUDE_PLUGIN_ROOT/skills/runpod-migrate/scripts/rp_api_inventory.py"
# 2. Otherwise substitute the directory you loaded this SKILL.md from — you know it:
[ -f "$SCAN" ] || SCAN="<directory containing this SKILL.md>/scripts/rp_api_inventory.py"
# 3. Last resort, search the usual install roots:
[ -f "$SCAN" ] || SCAN=$(find ~/.claude ~/.agents ~/.codex ~/.config -name rp_api_inventory.py 2>/dev/null | head -1)
python3 "$SCAN" --help >/dev/null || echo "scanner not found — resolve it before continuing"
```

Then, from the root of the user's repository:

```bash
python3 "$SCAN" . > runpod-api-inventory.md
python3 "$SCAN" . --json > runpod-api-inventory.json   # if you want to drive edits from it
python3 "$SCAN" . --scope rest                          # REST-only migrations
```

`runpod-api-inventory.md` goes into the user's repository. Report this file. Remove it or add it to gitignore before final delivery.

Stdlib-only Python, no install. It groups each call site by API generation. Groups include GraphQL, REST v1, v1/GraphQL field names, existing REST v2, serverless job API, and SDK/CLI wrappers. It also suggests a file-by-file order.

**Show the inventory table before any edits.** Users often do not know their API version. An earlier agent might have selected it without a record. "3 files on v1, 2 on GraphQL, 1 already on v2, 2 on the job API — leave those
alone" is often the single most useful output of this whole skill.

#### What it detects, and what it cannot

It is regex line-scanning, but the classification is what makes it usable — plain
`grep -r runpod` gets two things actively wrong:

- **`api.runpod.ai/v2` vs `api.runpod.io/v2`.** One letter apart. `.ai` is the serverless
  job API and must not be touched. `.io` is the control plane you are migrating to.
  Grepping for `v2` tells you the codebase is "already migrated" when it is not.
- **Some names are valid in both versions.** `/pods` is a v1 and v2 path. `["pods"]` unwraps a v2 envelope. `idleTimeout` is top-level in v1 and nested under `workers` in v2. The scanner suppresses a hit when the same line carries v2 context, so it reports
  work that remains rather than every occurrence of a word.

The scanner searches **field names and URLs**. A file can use `p["costPerHr"]` from a wrapper without "runpod", a URL, an import, or an operation name. A v2 rename can silently break that consumer.

Four things it genuinely cannot resolve. Examine them by hand, every time:

| Blind spot | How to close it |
| --- | --- |
| **Base URL lives in config**, not code (`settings.yaml`, `.env`, a ConfigMap, Terraform) | The scanner does read those files, so the URL surfaces — but the *call sites* using it are elsewhere. Grep for whoever reads that config key. |
| **Paths assembled by a helper** — `_url("pods", pod_id, "stop")` | Reported under *possible indirect call sites*. Advisory, because `resp.json()["pods"]` looks identical. Open each one. |
| **SDK wrappers** (`import runpod`) | The API generation is a property of the installed *version*, not the code. Examine `requirements.txt` / lockfile and the SDK's own release notes. |
| **Generated clients** | The OpenAPI/GraphQL document is the real source. Regenerate from the v2 spec instead of editing generated files. |

Then read the code the scanner flagged. It finds call sites. It does not understand your
wrappers. Trace who calls them — a renamed response field like `costPerHr → cost` breaks
every caller, not just the request builder. This is the one step where a code-graph or
LSP index earns its keep, if one is already available.

### 2. Brief the breaking changes — before the diff, not after

Read **[reference/breaking-changes.md](reference/breaking-changes.md)** and tell the
user which ones actually apply to *their* code. Two classes, and the second is the one
they are afraid of:

1. **Renames and moves produce visible errors.** v2 rejects unknown request fields with `422` and lists their names. Thus, a missed rename cannot silently reach production.
2. **Same name, different meaning** causes silent errors. A passing test suite does not prove correct meaning.
   The reference lists all changes.

   Two changes are especially material.
   `flashboot` changed from boolean to a three-value enum.
   v1 `/billing/endpoints` reports serverless spend, which moved to v2 `/billing/serverless`.
   v2 `/billing/endpoints` reports public endpoints, a *different product*.

   It returns `200` with a correct total for that product, not the caller's intended product.

### 3. Plan, split into required vs cleanup

Write the plan down before editing, and keep these buckets separate all the way through
to the final summary:

- **Required** — it does not work on v2 without this.
- **Cleanup** — it works either way, but v2 lets you delete code (custom job URLs,
  custom availability retry, polling loops that can now be SSE).
- **The user must decide how to replace removed capabilities.** Examples include spot/interruptible pods, savings plans, `dockerEntrypoint`, placement constraints (`countryCodes`, `minRAMPerGPU`, …), pod `reset`, and per-pod GPU fallback. Read [breaking-changes.md](reference/breaking-changes.md) Class 3. Do not rely on memory because v2 additions remove items from that category. CUDA pinning,
  `templateId` and CPU endpoint writes all used to be here and are not any more.

**Stop and ask before writing code in that third bucket** — but bring the replacement
with you. Some of these have a working rebuild and some genuinely have nothing, and the
difference decides what you are asking. If an alternative implementation exists, show it and ask the question that changes it. For `countryCodes`, use [catalog filter + `dataCenterIds` + a placement assert](reference/breaking-changes.md#replacing-countrycodes-and-the-rest-of-the-placement-constraints). Ask whether the restriction is a preference or a compliance requirement. For per-pod GPU fallback, show [an availability-ordered loop](reference/breaking-changes.md#replacing-the-gpu-fallback-list-pods-only).

Where nothing exists, the options are
accept the behavior change, keep that call on v1/GraphQL, or redesign around it, and only
the user can pick.

Do not describe removal as a dead end when an alternative implementation exists. That can cause unnecessary retention of a v1 call. Never remove the field with a `# no v2 equivalent` comment. That silently changes infrastructure behavior. This category exists to prevent that failure. If the bucket is empty, say
so — that is reassuring and takes one line.

### 4. Migrate, one file per commit

Use the scanner's suggested order, with fewest call sites first. **Exception: migrate a shared transport helper before its consumers**, regardless of count. The scanner orders by call-site count and cannot inspect imports. Thus, it can place a consumer before the module that supplies its client. Migrating a consumer
first means writing against an interface you are about to change.

Per file:

- Map paths and fields with **[reference/rest-v1-to-v2.md](reference/rest-v1-to-v2.md)**
  or **[reference/graphql-to-v2.md](reference/graphql-to-v2.md)**. If a field is not in
  the tables, or the API disagrees with them, examine the spec directly —
  [Ground truth](#ground-truth-check-the-spec-yourself).
- **Write new code for `gpuTypeIds` + `gpuTypePriority` on a pod. Field renames are insufficient.** A v2 pod accepts one GPU type. Replace server-side fallback with a client-side catalog loop. Working implementation:
  [breaking-changes.md → Replacing the GPU fallback list](reference/breaking-changes.md#replacing-the-gpu-fallback-list-pods-only).
  **Endpoints can operate without a loop** — `gpu.pools` is already a list and workers land on
  whichever listed pool has capacity.
- **Always request availability on catalog reads — with `product`.** Any
  `GET /v2/catalog/gpus`, `/catalog/cpus`, or `/catalog/datacenters` this migration
  introduces gets `include=AVAILABILITY` (`GPU_AVAILABILITY`/`CPU_AVAILABILITY` for
  datacenters). Availability is the top-of-mind question for every Runpod user and the
  call costs the same. Do not omit it because the current code did not ask for it — v1
  could not.

  **`include=AVAILABILITY` alone is a `400`.** On `/catalog/gpus` and `/catalog/cpus`,
  `product` is required with it and invalid without it — `400` either way. There is no
  default, deliberately: the same GPU can be scarce for `POD` and plentiful for
  `SERVERLESS`, so the context has to be stated. Pick the one matching what you are
  creating (`POD`, `SERVERLESS`, or `CLUSTER`, CPUs take `POD` or `SERVERLESS`):

  ```
  GET /v2/catalog/gpus?include=AVAILABILITY&product=POD
  ```
- Offer the **rollback flag** (`RUNPOD_API_V1=1`) while v2 is new to them:
  **[reference/rollback-flag.md](reference/rollback-flag.md)**. Worth it for a service
  in production. Skip it for a one-off script.
- **Never change behavior and API version in the same commit** — including the
  improvements v2 makes possible. Fast failure on `status == "ERROR"` instead of timeout is an improvement for the *next* commit. If combined with migration, rollback would remove both changes. Land those in the **cleanup**
  bucket, separately.

[reference/worked-example.md](reference/worked-example.md) shows a real client's full before/after. It includes pod create with GPU fallback, endpoint create with inlined container config, and a GraphQL dashboard.

### 5. Verify against the live API

Static review is not enough. V2's validator is strict and its errors are precise.
Run again the scanner to prove the call sites are gone, then exercise the real paths:

```bash
python3 "$SCAN" . --scope rest --fail-on-legacy   # exit 1 if v1 remains
```

Two markers, and they mean different things — do not reach for the wrong one:

| Marker | Use it for |
| --- | --- |
| `rp-migrate: keep-v1` | legacy code kept **on purpose** — a `RUNPOD_API_V1` rollback branch, or a GraphQL call with no v2 equivalent. Reported under *kept on purpose*. |
| `rp-migrate: ignore` | a **false positive** on code that is already correct. Says "this isn't legacy", not "this is legacy I'm keeping". Reported under *marked false positives*. |

Both accept `line`, `start`/`end` region, or `file` scope, and both drop out of the plan
and out of `--fail-on-legacy`. Using `keep-v1` to silence a false positive records a lie
in the report — reach for `ignore` there.

**The gate can still be wrong.** Step 1's blind spots hide v1 code before migration. After migration, they can flag correct v2 code. The scanner
handles the two common cases — trailing `# was imageName` annotations, and a base URL
held in a constant (`f"{BASE}/pods"` where `BASE` is a v2 URL defined anywhere in the
file).

Beyond those — a base URL imported from another module, or built at runtime from
config — it can still misread correct code as legacy. Read the flagged lines before you trust the exit code. Mark actual false positives with `ignore`. Do not weaken the gate.

- **Reads** are free — list pods, endpoints, volumes, catalog. Make sure that you unwrap the
  new envelope (`{"pods": [...]}`, not a bare array).
- **Writes** cost money. Create → assert → delete, on the smallest thing that proves the
  shape. Never test against resources the user already has.
- Decode `422`s with the table in [reference/breaking-changes.md](reference/breaking-changes.md#reading-a-422). Include the case where a missing required field makes the validator report valid fields as "additional properties not allowed".

### 6. Summarize — this is the artifact they will actually read

Most users read the summary and not the diff. Structure it exactly like this:

```
## Required for the migration
<file:line> — what changed and why it had to

## Cleanup enabled by v2
<file:line> — what got deleted or simplified

## Behavior changes to watch
the same-name-different-meaning items that applied

## Still on GraphQL (no v2 equivalent)
myself / secrets / spot pods / clusters — and why

## Unlocks: what you can build now
tied to what this codebase already does
```

That last section is the highest-value part. Do not paste a generic feature list. Examine this user's work and difficulties, including known session context. State where v2 changes that work. "Your `wait_until_running`
loop times out on failed pods; v2's `ERROR` status lets it fail in seconds" beats "v2 has
richer status values". [reference/unlocks.md](reference/unlocks.md) is organized as
*if the code does X → v2 offers Y* for exactly this.

## Ground truth: check the spec yourself

The `reference/` mapping tables have live API verification dated **2026-08-10**. v2 changes actively. Use the tables for quick guidance, but do not treat them as authoritative. Both specs
are public and accessible without authentication:

```bash
curl -s https://api.runpod.io/v2/openapi.json  -o /tmp/rp-v2.json
curl -s https://rest.runpod.io/v1/openapi.json -o /tmp/rp-v1.json
```

**What a request body actually accepts, and what is required** (`*`). Worth running
before writing any create call — it resolves `allOf` composition, which a naive read of
the raw JSON misses:

```bash
python3 - CreateEndpointRequest <<'PY'
import json, sys
S = json.load(open("/tmp/rp-v2.json"))["components"]["schemas"]
def merge(n, acc=None):
    acc = acc if acc is not None else {"props": {}, "req": set()}
    if "$ref" in n: return merge(S[n["$ref"].split("/")[-1]], acc)
    for sub in n.get("allOf", []): merge(sub, acc)
    acc["props"].update(n.get("properties", {})); acc["req"].update(n.get("required", []))
    return acc
def kind(v):
    if "$ref" in v: return v["$ref"].split("/")[-1]
    if "allOf" in v: return kind(v["allOf"][0])
    return v.get("type", "?")
m = merge(S[sys.argv[1]])
for k, v in sorted(m["props"].items()):
    print(f"  {'*' if k in m['req'] else ' '} {k:16} {kind(v)}")
PY
```

Swap the argument for `CreatePodRequest`, `UpdatePodRequest`, `CreateTemplateRequest`, or `CreateNetworkVolumeRequest`, …

Which schemas mention a field? This is useful when a `422` names something you cannot place:

```bash
python3 -c 'import json,sys; S=json.load(open("/tmp/rp-v2.json"))["components"]["schemas"]; [print(" ",n) for n,s in S.items() if sys.argv[1] in json.dumps(s)]' flashboot
```

### Precedence when sources disagree

**observed live behavior > the spec > these tables.** The specification can be incorrect. The reference documentation identifies known differences: `timeout` has documented default `300000` ms, but returns `0`. If the live API contradicts the specification, trust the API. **Report the difference in the summary** so the user knows the documented default is unreliable.

If a `reference/` mapping no longer matches the specification, correct the call and report the difference. The verification date makes stale guidance identifiable.

For GraphQL there is no machine-readable schema (introspection is disabled), so that
side cannot be checked this way — see the caveat in
[reference/graphql-to-v2.md](reference/graphql-to-v2.md).

## Tooling notes

The inventory scanner is a **grep-class script, not a code-graph index**. It identifies API generation from URL strings and field names. It must support any language in an arbitrary customer repository. It must give every user the same result without setup.

A code-intelligence index (LSP, or an MCP graph server if one is
already running) earns its keep at a different step — step 1's *blast radius* question,
"who calls this wrapper whose response field just got renamed" — not at detection.
Use one there if it is already available. Do not stand one up just for this.

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
