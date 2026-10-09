# runpodctl — output format, error codes, environment variables

Necessary information to parse runpodctl's output and decide what to do with a
failure. The 80% rule is in [SKILL.md](../SKILL.md#output--errors). This file is the
full surface.

**Version floor: runpodctl ≥ v2.8.0.** The coded error shape, the serverless `urls` object
and GPU pricing/per-DC availability all arrived in v2.8.0.

Older binaries (≤ v2.7.3) printed `{"error":"<message>"}` on stderr, without `code` or `status`. They did not print plaintext. They inserted the message without escaping it. A quote in the message thus produced invalid JSON. They also
dumped usage text after runtime errors. Before v2.8.0, error JSON could appear valid but lack the field used for decisions.

**Make sure that `code` is present.** JSON parsing alone does not show this. `runpodctl version` is a weak gate: it prints plaintext, and
a binary built from source reports a placeholder version regardless of the code it contains.

## Output format

JSON is the **default** — the CLI is built for agent consumption, and data goes to
**stdout**.

```bash
runpodctl pod list                    # json (default)
runpodctl pod list --output=yaml      # yaml — the only alternative
```

**There is no table format** — `json` and `yaml` are the only values. As of **v2.10.0** an
unrecognized value is a hard error before any API call, and matching is
**case-insensitive**:

```jsonc
// runpodctl gpu list --output=table   (v2.10.0+)
{"error":"invalid --output \"table\": supported formats are json and yaml","code":"usage_error"}
// exit 1, usage text on stderr
```

```bash
runpodctl gpu list --output=YAML      # v2.10.0+: real YAML (case is ignored)
```

⚠️ **This inverted in v2.10.0, so a handler has to know which binary it is on.** Through
**v2.9.0** matched the flag case-sensitively. An unknown value silently selected JSON. Both `--output=table` and `--output=YAML` returned JSON. The only safe advice was "pass lowercase `yaml` or don't pass the flag". That silence is how a table
format the CLI never had ended up documented in the first place.

On v2.10.0+, `--output=table` exits **1** with `usage_error`. A defensive `--output=json` still works. Other unsupported values now cause explicit failures instead of fallback output.

Legacy `get pod` / `get cloud` commands print a human-readable table on stdout and ignore `--output`. See [plaintext gaps](#plaintext-gaps). Thus, a table from the legacy `get pod`/`get cloud` paths identifies the legacy command. It does not show the requested output format.

## Error format

Errors go to **stderr** as a single flat JSON object, and the exit code is
**non-zero**, so stdout parses as data.

```jsonc
{"error":"failed to get endpoint: endpoint not found","code":"not_found","status":404}
```

| field | notes |
| --- | --- |
| `error` | human-readable message, unwrapped on the REST path. A GraphQL HTTP failure without an extractable message returns the raw body, which can itself be JSON. Never parse this field in either case. |
| `code` | stable, lowercase, present on every JSON error (see [plaintext gaps](#plaintext-gaps)) |
| `status` | HTTP status — only when the failure arrived on a **non-2xx** response (REST *or* GraphQL) |
| `id` | **v2.9.0+**, only on a failure that left a **created, billing resource** behind — a `create --wait` that timed out or was interrupted. Read it instead of regexing the message: it is the id for resource removal |

**Branch on `code`, never on `status` or message text.** GraphQL reports missing resources through HTTP 200 with empty data. These errors have no `status`. Thus, `if (status === 404)` misses every GraphQL not-found error:

```jsonc
// serverless get <missing> — REST, so a status is available
{"error":"failed to get endpoint: endpoint not found","code":"not_found","status":404}
// template get <missing> — GraphQL answered 200/null, so there is no wire status
{"error":"failed to get template: template not found: bogus-template-id","code":"not_found"}
```

`code` uses the typed code from the API or error when available. Otherwise, the output sink supplies a fallback. Local validation and transport failures thus also have codes.

**`timeout` is the one documented exception**, because two outcomes share it and only the
message separates them (see the [codes table](#codes)). A handler that reads only `code` is
still correct: treat `timeout` as never-retry and poll instead. For a single API call, the message can indicate "safe to retry". Without that evidence, an extra poll is harmless. An incorrect retry creates a second job.

### Codes

| code | meaning |
| --- | --- |
| `usage_error` | unknown command, unknown flag, bad/wrong-count arguments, or a **cobra-required** flag left out. Usage text prints after the JSON |
| `not_found` | the **API** does not have the resource. During `create --wait`, this can also mean that a created resource has gone or never became visible. Examine the `id` field before concluding that nothing exists. |
| `bad_request` (400) `unauthorized` (401) `forbidden` (403) `conflict` (409) `rate_limited` (429) `server_error` (5xx) `api_error` | derived from the REST status |
| `graphql_error` | a GraphQL call failed: an `errors` array in a 200 body, **or** a non-2xx response from the GraphQL endpoint (that form also carries `status`) |
| `no_credentials` | no API key configured at all — set `RUNPOD_API_KEY` or run `runpodctl doctor` |
| `network_error` | the API could not be reached at all — DNS, connection refused, TLS, timeout |
| `cli_error` | anything else local: config, environment, and validation the command does itself |
| `timeout` | **v2.9.0+.** The CLI stopped waiting — two outcomes sharing one code, told apart by the message. If it names a `serverless status` command, the **job is still running server-side**: poll it, never re-invoke (that buys a second job). Otherwise a single API call ran out of time and nothing is running, so a retry is fine |
| `job_failed` | **v2.9.0+.** A serverless job reached a terminal status other than `COMPLETED` (`FAILED`/`CANCELLED`/`TIMED_OUT`). The request itself succeeded — the job payload, including the worker's own `error`, is still on **stdout** |
| `wait_timeout` `wait_interrupted` | **v2.9.0+.** A `create --wait` gave up (budget) or was cancelled (ctrl-c / SIGTERM). The resource **was created and still bills**. Its id is in the `id` field above |

This table lists **codes generated by the CLI**, not every possible code. Explicit API codes pass through in lowercase, including codes outside the table. **For an unknown code, use a fatal default branch and show `error` verbatim.** Never select retry as the fallback.

### What to retry

**runpodctl has no internal retry** — it never backs off for you, so whatever your
wrapper does is all that happens.

- **Retry with backoff:** `network_error`, `rate_limited`, `server_error` (and `api_error`
  when `status` is 5xx). A transient `graphql_error` is possible too but indistinguishable
  from a permanent one, so cap those attempts tightly.
- **Never retry:** `usage_error`, `cli_error`, `bad_request`, `not_found`, `conflict`,
  `no_credentials`, `unauthorized`, `forbidden`, `job_failed` (the job ran and failed —
  re-running is a new job, not a retry).
- **Never retry the *command*, but do follow up:** `timeout` and
  `wait_timeout`/`wait_interrupted` all mean work or a resource outlived the CLI. Re-running
  the same command creates a **second** job or a **second** billed resource. Poll instead
  (`serverless status`, `pod get`), or clean up using the `id` field. One exception applies: a `timeout` message that names **no** follow-up command. A single API call timed out, and no work remains active. Retry is safe in that case.

Two invariants make that safe to encode:

- **`not_found` always means server-side.** A bad *local* path (say a mistyped
  `--model-path`) is `cli_error`, so `not_found` never means "you typed a path wrong".
- **`network_error` is the only code the CLI assigns to mean "couldn't reach the API"**,
  detected structurally. Deliberately *not* `network_error`: a malformed `RUNPOD_API_URL`
  is `cli_error`, so a retry loop never fires for something a retry cannot fix. Local wait timeouts previously used this code. Since **v2.9.0**, `model add --wait-for-hash` reports `timeout` instead of `cli_error`. The exit code and message text stay the same. A handler that branches on `code` must include the new branch.

### Auth failures are two different codes

`no_credentials` means **no key is configured**. A key that is present but wrong, expired
or revoked is `unauthorized` (401), and one lacking access to the resource is `forbidden`
(403):

```jsonc
// RUNPOD_API_KEY=rpa_bogus… pod list
{"error":"api request failed with status 401","code":"unauthorized","status":401}
```

Do not combine these error cases. A "missing"-key prompt for a revoked key causes repeated unsuccessful attempts.

### Invocation mistakes split across two codes

`usage_error` covers what cobra validates: unknown command/flag, wrong arg count, and
missing `MarkFlagRequired` flags. Validation a command performs itself lands in
`cli_error`, even though it is just as much an invocation mistake:

```jsonc
// ssh remove-key with neither --name nor --fingerprint
{"error":"either --fingerprint or --name must be provided","code":"cli_error"}
```

So `cli_error` is a mixed bucket — "your invocation was wrong" *and* "your local
environment is wrong". Read `error` to tell them apart. Do not retry either.

### Missing API key

The JSON-covered commands all report `no_credentials` — `pod` (`list`/`get`/`create`),
`template create`/`update`, every `ssh` subcommand, `model *`:

```jsonc
{"error":"api key not found. get your key at https://www.runpod.io/console/user/settings then: export RUNPOD_API_KEY=your-key OR run: runpodctl doctor","code":"no_credentials"}
```

```jsonc
{"error":"unknown flag: --nope","code":"usage_error"}
```

Usage text follows the JSON on stderr — and, unlike older builds, a *runtime* error no
longer dumps usage text after it.

### Exit codes, and what else is on stderr

Every failure on the JSON path exits non-zero (`model` and `update` used to print an error
and exit **0**, they do not anymore). The exceptions are in
[plaintext gaps](#plaintext-gaps) below.

**Non-empty stderr is not a failure signal.** Deprecation notices (`warning: 'runpodctl
get pod' is deprecated…`), `pod create` advisories (`note: …`) and config-migration lines
all go to stderr on successful runs. Gate on the exit code first, then parse stderr.

### Plaintext gaps

The JSON error shape covers these commands, including every GraphQL call site:
`pod`, `serverless`, `template`, `volume`, `registry`, `gpu`, `datacenter`, `billing`, `user`, `model`, `ssh`, `send`, `receive`, `hub`, and `update`.
GraphQL failures use `graphql_error`, or `not_found` for nil-data lookups.
These surfaces still print plaintext without `code`:

| surface | shape |
| --- | --- |
| legacy `get`/`create`/`remove`/`start`/`stop pod`, `create`/`remove pods`, `get cloud` | `Error: <msg>` on stderr, exit 1 — including the missing-key case, which carries the same message as `no_credentials` but no JSON and no `code`. Success prints a human **table** on stdout, not JSON |
| `exec` (hidden, deprecated) | **v2.10.0+:** joined the JSON error shape — flat JSON with a `code` on stderr and a **non-zero** exit. Through v2.9.0 it printed the error as plaintext and still exited **0**, so a caller that trusted the exit code saw a silent success. Either way: progress on **stdout**, and it polls up to **5 minutes** for the pod's SSH info before giving up |
| `project` (hidden) | prints errors to **stdout** and exits **0** — the last surface where the exit code cannot be trusted |

### Parsing `ssh info`

`ssh info` has three shapes, and only one of them is an error:

| situation | output |
| --- | --- |
| connectable | `{"id","name","ssh_command","ip","port","ssh_key":{…}}` on stdout, exit 0 — note **snake_case**, unlike the camelCase everywhere else in the CLI. A `"setup":"runpodctl doctor"` key appears when the local key is incorrect |
| pod exists, not connectable | `{"error":"pod not ready: <reason>","id":…,"name":…,"status":…}` on **stdout**, exit **0**, no `code`. Here `status` is the pod's desired status, *not* an HTTP status. v2.9.0+ appends a reason when available (image still pulling, port 22 not published, pod stopped, …). Otherwise, it uses the bare `"pod not ready"`. Thus, an exact-match `=== "pod not ready"` started failing intermittently on that release. A prefix match did not |
| no such pod | `{"error":"pod 'x' not found","code":"not_found"}` on stderr, exit 1 |

So: examine the exit code, then examine for an `error` key even on stdout.

"Not ready" fires whenever the pod has no **public port 22**, which is not the same thing
as "still booting". A pod whose image never starts sshd stays not-ready. Evidence: a `ubuntu:22.04` CPU pod remained at `status: RUNNING` during ~70 s of readiness polls. Bound every SSH readiness loop. Do not treat `RUNNING` as "SSH is
coming". If SSH never starts, the image is the problem, not the wait.

Two v2.9.0 changes help. `pod create --wait` runs a bounded readiness loop and finds an SSH banner, not only a published port. On `pod get`/`pod list`, `runtimeStatus` distinguishes `initializing` from `running`. Inference from `desiredStatus` is no longer necessary. Also, on **v2.9.0+**, a **stopped** pod returns no `ssh_command`.
Previously, it returned an unusable command with old runtime ports.

The stopped pod is also absent from the `ssh connect` `connections` list.
When nothing is reachable, the list is `[]` instead of `null`.

A parser should tolerate non-JSON stderr lines from those commands. Do not rely on the exit code for `project` or for `exec` before v2.10.0. Prefer the non-legacy
equivalents: `pod get`/`pod create`/`pod delete`, and `ssh info <pod-id>` + your own `ssh`
invocation instead of `exec`.

## Environment variables

| variable | default | what it sets |
| --- | --- | --- |
| `RUNPOD_API_KEY` | — | API key. Also settable via `runpodctl doctor` or `~/.runpod/config.toml` (`apikey`) |
| `TIMEOUT` | `30s` | per-API-call deadline — **no `RUNPOD_` prefix** (the CLI reads environment variables unprefixed, so this one looks nothing like the others). Exceeding it is `code: "timeout"`. You may also set a top-level `timeout` in `~/.runpod/config.toml`. Put it above any `[section]` header. Otherwise, it becomes `section.timeout` and is silently ignored. Distinct from `--wait`, which bounds a whole job or readiness wait rather than one call |
| `RUNPOD_API_URL` | `https://rest.runpod.io/v1` | REST control plane (config key `restApiUrl`) |
| `RUNPOD_GRAPHQL_URL` | `https://api.runpod.io/graphql` | GraphQL control plane (config key `apiUrl`) |
| `RUNPOD_INVOKE_URL` | `https://api.runpod.ai/v2` | base for the invoke URLs reported by `serverless create`/`get`/`list`/`update` (config key `invokeUrl`) |

**Invoke uses a separate service from the control plane.** Changes to `RUNPOD_API_URL` or `RUNPOD_GRAPHQL_URL` do not change invoke URLs. For a non-production invoke host, explicitly override `RUNPOD_INVOKE_URL`. Otherwise, generated URLs target production.

## Serverless invoke URLs

`serverless create`/`get`/`list`/`update` return a `urls` object, computed from the
endpoint ID, so a freshly created endpoint is callable without a second lookup:

```jsonc
"urls": {
  "run":     "https://api.runpod.ai/v2/<endpoint-id>/run",
  "runsync": "https://api.runpod.ai/v2/<endpoint-id>/runsync",
  "health":  "https://api.runpod.ai/v2/<endpoint-id>/health"
}
```

`status` is not in the object. It is `<run url minus /run>/status/<job-id>`.

## GPU pricing and per-data-center availability

`gpu list` reports on-demand price per hour per cloud type plus a per-DC stock
breakdown:

```jsonc
{
  "gpuId": "NVIDIA A100 80GB PCIe",
  "displayName": "A100 PCIe",
  "memoryInGb": 80,
  "secureCloud": true,          "securePricePerHr": 1.39,
  "communityCloud": true,       "communityPricePerHr": 1.19,
  "stockStatus": "Low",         "available": true,
  "dataCenterAvailability": [
    {"dataCenterId": "CA-MTL-3", "stockStatus": "Low"},
    {"dataCenterId": "EU-RO-1",  "stockStatus": "none"}
  ]
}
```

- A price is **explicitly `null`** when that cloud type does not offer the GPU, which is
  distinguishable from a real `0`. Read `securePricePerHr`/`communityPricePerHr` rather
  than guessing that a lower tier is cheaper.
- Top-level `stockStatus` gives the **best status across data centers**. Use `dataCenterAvailability[]` to find the actual creation location, especially with a network volume.
- An unknown non-empty status now ranks above absent/`none`. Thus, **`available` no longer reports `false`** when an unknown value is the GPU's only status. An unknown status still ranks below `Low`. A known level thus takes precedence in top-level `stockStatus`. This deliberate choice makes `dataCenterAvailability[]` the necessary field for placement decisions. Casing and surrounding whitespace are normalized now, so they are no
  longer a source of unknown values.
- Two sentinels for one concept: the per-DC breakdown spells an unreported status
  `"none"`, while the top-level field **omits the key** for the same condition. Handle
  both.
- **Stock values are capitalized levels but the sentinel is lowercase** — `"High"`,
  `"Medium"`, `"Low"`, `"none"` in practice. `"unavailable"`, `"out of stock"`, and `"no stock"` also mean no stock. Internal comparison ignores case. Convert to lowercase before tests. Do not write `if s != "none"`.
- **`gpu list` hides GPUs without stock by default.** For one target data center, pass `--include-unavailable`. Otherwise, a GPU with stock only there can be absent from the results.

Two scoping limits the fields do not express:

- **The prices are pod on-demand rates** (`gpuTypes { securePrice communityPrice }`). These are not serverless rates. Serverless charges apply per request-second. Do not present them as endpoint costs.
- **`dataCenterAvailability[]` has no cloud-type attribution**, while pricing is split
  secure vs community. "Cheapest option that schedules in DC X" therefore is not answerable
  from `gpu list` alone. Treat it as two separate reads.

And when you act on the choice: pin placement with `--data-center-ids`, or the analysis
does not constrain anything. For serverless, `--gpu-id` accepts a GPU *type* id. The server translates it to a GPU **pool**. The endpoint can thus use cards other than the one priced. See pool and type ids in [`runpod-usage` gpu-selection](../../runpod-usage/reference/gpu-selection.md).
