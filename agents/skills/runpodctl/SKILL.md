---
name: runpodctl
description: "Manage Runpod GPU/CPU workloads through the terminal. Cover pods, serverless endpoints, templates, network volumes, Hub deployment, models, SSH, and file transfer (send/receive). Use for terminal/CI/scripts, Hub browse/deploy, SSH setup, `doctor`, or sessions without Runpod MCP tools. For structured tool calls in an MCP-enabled session, prefer runpod-mcp."
allowed-tools: Bash(runpodctl:*)
metadata:
  compatibility: Linux, macOS
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Runpodctl

Manage GPU pods, serverless endpoints, templates, volumes, and models.

## Install

`curl -sSL https://cli.runpod.net | bash` (Linux/macOS, and Windows via WSL) or `brew install runpod/runpodctl/runpodctl`. Manual binaries and the Windows and conda steps live in the [runpodctl README](https://github.com/runpod/runpodctl#install), beside the `install.sh` they describe. The command surface comes from the binary — `runpodctl <resource> <action> --help` — or the generated pages under [`runpodctl/docs/`](https://github.com/runpod/runpodctl/tree/main/docs).

> Old runpodctl builds lack newer flags and behavior. For example, `--model-reference` is absent before v2.4.0.
> These differences cause errors, and the Homebrew tap can have an older version.
> Before any work, complete these steps:
>
> - Read `runpodctl version`.
>
> Then, run `runpodctl update`, or reinstall from the [latest release](https://github.com/runpod/runpodctl/releases).
> - Pin one recent version for the whole task.
> - Never change between old and new binaries during a task. This causes known failures.
>
> - Read the current build once with `runpodctl version` before you continue.

## Quick start

```bash
runpodctl update                    # FIRST: get on the latest build — old versions cause confusing errors
runpodctl version                   # confirm the current version before doing any work
export RUNPOD_API_KEY=your_key      # Non-interactive auth (agents) — runpodctl reads this
runpodctl doctor                    # Interactive first-time setup (API key + SSH) — for humans
runpodctl --help                    # See current top-level commands
runpodctl pod create --help         # Inspect exact current flags before creating
runpodctl gpu list                  # See available GPU types
runpodctl datacenter list           # GPU availability per data center (use to co-locate GPU + volume)
runpodctl hub search vllm           # Find a hub repo
runpodctl serverless create --hub-id <id> --name "my-vllm"  # Deploy from hub
runpodctl template search pytorch   # Find a template
runpodctl pod create --template-id runpod-torch-v21 --gpu-id "NVIDIA GeForce RTX 4090"  # Create from template
runpodctl pod list                  # List your pods
```

> Auth: an agent should `export RUNPOD_API_KEY=...` (non-interactive). `runpodctl
> doctor` is interactive (prompts) and also sets up SSH keys — good for a human's
> first run, not for scripted use.

API key: https://console.runpod.io/user/settings

## Live Help Is Authoritative

Live `runpodctl --help` output is authoritative for exact flags, aliases, and command syntax. Use this skill for workflows, decision rules, safety notes, and common examples.

```bash
runpodctl --help
runpodctl <resource> --help
runpodctl <resource> <action> --help
```

Before using unfamiliar commands, inspect live help first. Do not rely on this skill as an exhaustive flag reference.

**What live help does *not* cover:** output shapes, error codes, and exit-code behavior. `--help` lists flags. It never shows you what a failure looks like. For those, use [reference/output-and-errors.md](reference/output-and-errors.md).

When in doubt, probe the binary. Run the command incorrectly on purpose (`runpodctl serverless get nope`) and read its JSON output. Every doc is a snapshot, this skill included. The binary in front of you wins.

## Output & errors

Data is **JSON on stdout** (`--output=yaml` is the only alternative — there is no table
format, anything else silently returns JSON). A failure from the resource commands is a
single flat JSON object on **stderr** plus a **non-zero exit**:

```jsonc
{"error":"failed to get endpoint: endpoint not found","code":"not_found","status":404}
```

**Branch on `code`, never `status` or the message.** `status` exists only for a non-2xx response. GraphQL reports missing resources as HTTP 200 with null data. Thus, `if status == 404` misses every GraphQL not-found result.

| `code` | what to do |
| --- | --- |
| `network_error` | **retry with backoff** — the only code meaning "couldn't reach the API" |
| `rate_limited` `server_error` | **retry with backoff** — 429/5xx from the API |
| `usage_error` `cli_error` `bad_request` `not_found` `conflict` | do not retry, fix the input |
| `no_credentials` | no key set: `export RUNPOD_API_KEY=…` or `runpodctl doctor` |
| `unauthorized` `forbidden` | A key is set but is wrong/expired or lacks access. Do not retry or prompt again for a missing key. |
| anything else | treat as fatal, surface `error` verbatim — the API can pass through its own code |

**runpodctl never retries internally**. Nothing backs off for you.

- **`not_found` always means the API lacks the resource**, never a mistyped local path
  (that is `cli_error`).
- **`cli_error` is a mixed bucket:** local environment problems *and* invocation mistakes
  the command validates itself (for example `ssh remove-key` with neither `--name` nor
  `--fingerprint`). Only cobra-enforced required flags are `usage_error`.
- **`usage_error`** = unknown command/flag, bad arguments, missing cobra-required flag. Usage
  text follows the JSON. Runtime errors no longer print usage.
- **Non-empty stderr does not mean failure** — deprecation `warning:` and `note:` lines go
  to stderr on success too. Gate on the exit code, then parse stderr.

Coded errors, the serverless `urls` object and GPU pricing must use **runpodctl ≥ v2.8.0**.
Older binaries emit `{"error":"…"}` without **`code` or `status`**. Thus, `switch (err.code)` silently receives `undefined`. **Make `code` presence the gate**, not JSON versus plaintext. `runpodctl version` is unreliable here because it returns plaintext and source builds report a placeholder version.

Full code table, the surfaces that still print plaintext (`exec`, legacy `pod`
commands, `project`), and the env-var table (incl. `RUNPOD_INVOKE_URL`):
**[reference/output-and-errors.md](reference/output-and-errors.md)**.

## Decision Rules

- Use Hub for a known deployable app or worker. Examples include vLLM, ComfyUI, Whisper, and a Runpod-maintained repository.
  - **Picking a worker:** prefer a **first-party or well-adopted, recently-released** worker on a **broad, high-availability GPU pool**. Observable signals via `runpodctl hub list`: `--owner runpod-workers` (first-party), `--order-by releasedAt`/`updatedAt` (recency), `--order-by deploys`/`stars` (adoption). Do not pin a scarce large-GPU tier unnecessary for a small model.
- **"Active worker" = minimum workers, not maximum.** If a user asks for an "active worker," they mean `--workers-min 1` (keep one worker always warm → no cold start), **not** `--workers-max 1` (that only caps the ceiling). A warm min-1 worker is ideal for development/iteration.
- ⚠️ **A min-1 worker bills continuously, even while idle** (it defeats scale-to-zero). If you set `--workers-min 1` for development, restore `--workers-min 0` or delete the endpoint when finished. Otherwise, idle workers continue to cause charges.
    - **runpodctl ≥ v2.10.0 is necessary.** Earlier binaries silently omitted `--workers-min 0` and `--idle-timeout 0` from update requests (`omitempty` removed zero). The reset appeared successful, but endpoint billing continued. Examine `runpodctl version`. On an older binary, examine `serverless get <id>` and fall back to `PATCH https://rest.runpod.io/v1/endpoints/<id>` with an explicit `{"workersMin":0}`.
- `serverless update` has **no `--gpu-id` flag**. To change an existing endpoint's GPU pool, call `PATCH https://rest.runpod.io/v1/endpoints/<id>` with `{"gpuTypeIds":[...]}` directly.
- **Create CPU serverless endpoints with `runpodctl serverless create --compute-type CPU`.** Do not use MCP: v2 `create-endpoint` must have `gpuPoolIds` and has no CPU concept. **Never use** public control REST `POST https://rest.runpod.io/v1/endpoints` with `"computeType":"CPU"`. It silently creates a **GPU** endpoint (verified evidence in the Serverless command section below).
- Use templates for an existing template ID or reusable image/config defaults. Also use them for control beyond Hub's settings.
- Use direct pod creation with `--image` for a specific Docker image when a saved template is unnecessary.
- Use serverless for request/response inference APIs and scalable workers. Use pods for interactive work, notebooks, training, diagnosis, or long sessions.
- Use CPU pods for preprocessing, file movement, lightweight scripts, and non-CUDA work. Use GPU pods when CUDA, model inference, training, or GPU memory is required.
- **Keep `--cloud-type` at its `SECURE` default.** Community Cloud hosts are approved vendors. Secure Cloud hosts are data-center-grade providers and usually have more stable behavior. Only pass `--cloud-type COMMUNITY` when the user explicitly asks for it (note that for a public port 22, supply `--public-ip`).
- Do not pass GPU flags when creating CPU pods. Examine `runpodctl pod create --help` for the current valid flag set.
- **Waiting for a resource to be usable: use `--wait`, do not write a poll loop** (v2.9.0+). `create` returns as soon as the resource is *scheduled*, which is why a "RUNNING" pod often refuses ssh and a fresh endpoint 404s. `pod create --wait` returns when port 22 answers with an ssh banner. `serverless create --wait` when `/health` reports a ready or running worker.

  On timeout or ctrl-c, the resource is **kept**. Its ID appears in the error object's `id` field. Read that field and remove temporary resources.

  Do not assume creation failed (pods bill by the second, endpoints without a running worker do not, but start one on first request).
- Standing up a **service on a pod** (Ollama, ComfyUI, a dev server)? Declare `--ports` and `--env` **at creation** (reset a running pod before you add them). Follow the `runpod-usage` pod development loop (`reference/pod-workflows.md`). Install through SSH-exec, bind to `0.0.0.0`, and poll the proxy URL until it answers.
- For SSH details, use `runpodctl pod get <pod-id>` or `runpodctl ssh info <pod-id>`. runpodctl has **no interactive-shell command**. `ssh info` returns the command and key but does not connect. Run commands over SSH yourself with `ssh user@host "command"`.
- Network volumes are location-sensitive. Examine datacenter availability before attaching volumes, and use `send` / `receive` or S3-compatible storage for migrations.
- Clean up paid resources after tests: delete serverless endpoints, pods, and temporary volumes created for validation.
  - **Cost guard on creation:** use `--terminate-after` (deletes the pod). `--stop-after` only *stops* it, so disk/volume keep billing.
  - **Attached volume:** to delete a network volume, remove the pod using it first.

### Serverless facts (context, not rules)

- **Scale-to-zero billing:** With default `--workers-min 0`, serverless endpoints scale to zero. Idle GPU time is not billed. Billing is per request-second, which suits a request/response API.
- **Broken image:** If workers are `ready` but jobs stay `IN_QUEUE` with `inProgress: 0`, the image is broken or mis-dispatches. Change to a different worker. Do not merely wait.
- **Diagnosing it:** Read worker/job counts with `runpodctl serverless health <endpoint-id>` (v2.9.0+). Then, read worker output with `runpodctl serverless logs <endpoint-id>` (v2.10.0+). No custom curl is necessary. Repeated `system` "start container" lines with no `container` output means the container exits before the handler runs.

## Commands

Essentials below. **For flags, ask the binary** — `runpodctl <resource> <action> --help`, which is current by construction. [reference/command-reference.md](reference/command-reference.md) holds the part `--help` cannot answer: what a flag *means* when it succeeds, which field to trust, and what a failure looks like.

### Pods

```bash
runpodctl pod list                                   # running pods (+ --all / --status / --since / --created-after)
runpodctl pod get <pod-id>                           # details incl. SSH info + runtimeStatus
runpodctl pod create --template-id <id> --gpu-id "NVIDIA GeForce RTX 4090"   # from template
runpodctl pod create --image <img> --gpu-id "NVIDIA GeForce RTX 4090"        # from image
runpodctl pod create --compute-type cpu --image ubuntu:22.04                 # CPU pod (lowercase `cpu`; serverless uses `CPU`)
runpodctl pod create --image <img> --gpu-id <id> --wait                      # block until ssh answers, then print the pod (v2.9.0+)
runpodctl pod {start|stop|restart|reset|update|delete} <pod-id>              # lifecycle (delete aliases: rm/remove)
runpodctl pod logs <pod-id>                          # recent container+system logs, json lines (v2.10.0+)
runpodctl pod logs <pod-id> --follow                 # keep streaming, reconnects on its own
runpodctl pod logs <pod-id> --since 30m --source system   # platform view: image pull / create / start
```

**A stalled deploy shows up in `--source system`** (v2.10.0+): repeated pull progress, or a
`create container` that never reaches `start`. Use `--source container` for your workload's own
output. Each line is one `{source,line,ts}` object, so pipe it straight to `jq`.

**Read `runtimeStatus`, not `desiredStatus`, to decide whether a pod is usable** (v2.9.0+):
`desiredStatus: RUNNING` says that while the image is still pulling. Field meanings, reason
tokens, and two edges (`--status` filters `desiredStatus` only, `unknown` = lookup failed, not
pod down) → [reference/command-reference.md](reference/command-reference.md#pod-status-fields).

### Hub

Browse/search the Runpod Hub (curated deployable repositories).

```bash
runpodctl hub search vllm                            # find a repo (+ hub list [--type/--category/--order-by/--owner])
runpodctl hub get <listing-id|owner/name>            # repo details
```

### Serverless (alias: sls)

```bash
runpodctl serverless list | get <endpoint-id> | delete <endpoint-id>
runpodctl serverless create --name "x" --template-id <id>       # from template
runpodctl serverless create --name "x" --hub-id <listing-id>    # from hub (+ --env KEY=VAL to override defaults)
runpodctl serverless create --hub-id <id> --gpu-id "NVIDIA GeForce RTX 4090" \
  --model-reference https://huggingface.co/<org>/<model>:main   # attach & host-cache a HF model (GPU only)
runpodctl serverless update <endpoint-id> --workers-max 5
runpodctl serverless create --template-id <id> --workers-min 1 --wait          # block until a worker is ready (v2.9.0+)
```

**Endpoint responses include invoke URLs.** `create`/`get`/`list`/`update` return a `urls` object (`run`, `runsync`, `health`). Read these URLs instead of constructing them. A second URL lookup is unnecessary for a new endpoint. They are
built from `RUNPOD_INVOKE_URL` (default `https://api.runpod.ai/v2`), which
`RUNPOD_API_URL`/`RUNPOD_GRAPHQL_URL` do **not** move: [reference/output-and-errors.md](reference/output-and-errors.md#serverless-invoke-urls).

**Reading worker logs** (v2.10.0+) — also first-class, so worker output no longer depends on the
MCP lane or a custom SSE read:

```bash
runpodctl serverless logs <endpoint-id>                       # every worker's recent logs, json lines
runpodctl serverless logs <endpoint-id> --worker <worker-id>  # just one worker
runpodctl serverless logs <endpoint-id> --follow              # picks up workers that scale up mid-follow
runpodctl serverless logs <endpoint-id> --since 1h --source system   # why a worker will not start
```

Logs belong to a **worker**. Without `--worker`, the command reads all workers and tags each line with `workerId`. **Crash-loop evidence:** Repeated `system` "start container" lines without `container` output indicate exit before the handler runs. Jobs stay queued despite available capacity.

**Invoking an endpoint** (v2.9.0+) — first-class commands, so an agent does not hand-build a
curl request or manage a bearer token:

```bash
runpodctl serverless run <endpoint-id> --input '{"prompt":"hello"}'   # submit and wait for the result
runpodctl serverless run <endpoint-id> --input-file payload.json      # same, payload from a file ("-" = stdin)
runpodctl serverless run <endpoint-id> --input '{}' --wait 15m        # longer budget (default 5m)
runpodctl serverless run <endpoint-id> --input '{}' --no-wait         # submit, print the queued job, exit 0
runpodctl serverless status <endpoint-id> <job-id>                    # check a job submitted earlier
runpodctl serverless health <endpoint-id>                             # worker + job counts
```

- Pass only the handler payload. The CLI supplies the `{"input": <your json>}` wrapper. A complete curl envelope causes two wrappers.
- **`timeout` means the CLI stopped its wait.** It does not show an endpoint fault.
  If the message names a `serverless status` command, the job continues on the server.
  Poll that job. Do **not** invoke it again, because that creates a second job.

Payload rules, the stdout/stderr split, exit codes and why `/runsync` is never used →
[reference/command-reference.md](reference/command-reference.md#invoking-an-endpoint-serverless-run-v290).

**Create from hub:** `--hub-id` resolves the hub listing, extracts the build image and config (GPU IDs, container disk, environment variables), creates an inline template, and deploys. Accepts both SERVERLESS and POD listing types. GPU IDs and environment variable defaults from the hub config are included automatically. Override with `--gpu-id` and `--env`.

**CPU serverless endpoints** (the always/never rule is in Decision Rules above): create with `runpodctl serverless create --compute-type CPU` (optionally `--instance-id`, for example `cpu3g-4-16`). Evidence dated 2026-07-14 shows why public REST is prohibited here. `POST https://rest.runpod.io/v1/endpoints` with `"computeType":"CPU"` silently returned a GPU endpoint (`gpuCount:1`, `cpuFlavorIds:null`). `runpodctl --compute-type CPU` correctly returned `computeType:"CPU"` with `instanceIds:["cpu3g-4-16"]`. The MCP server is **not** an alternative here: its v2 `create-endpoint` must have `gpuPoolIds` and the v2 spec has no `computeType`/`cpuFlavor` field at all (verified 2026-07-29). The public control REST is v1-only (`rest.runpod.io/v2` just redirects to documentation).

The separate **runtime/invoke** API `https://api.runpod.ai/v2/<endpoint-id>/…` (health/run/runsync/openai) is a different v2 and works fine — the v1-vs-v2 caveat here is only about the **control/management** REST.

**Model cache (`--model-reference`):** Attach a Hugging Face model to the endpoint by full URL with a ref, for example `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct:main`. Runpod caches it host-side in the standard HF cache dir (`/runpod-volume/huggingface-cache/hub/`), so the worker loads it directly — no bake, no volume. Repeatable. Works with `--template-id`/`--hub-id`, GPU only, **runpodctl v2.4.0+**. Full mechanics + how it compares to baking / network volume / the Model Repository: **[reference/model-caching.md](reference/model-caching.md)**. Worked end-to-end: golden path [20 — model-caching endpoint](../runpod/golden-paths/20-model-caching-endpoint.md).

Multi-region / high-availability (`--network-volume-ids`): attach multiple network volumes (one per data center). This spreads workers across DCs instead of pinning them to one. Use `runpodctl serverless create --template-id <t> --network-volume-ids <v1>,<v2> --data-center-ids <dc1>,<dc2> …`.
**runpodctl ≥ v2.4.0 is necessary** (older versions do not support multi-volume attach).

Examine
`runpodctl version`. The Homebrew tap can lag, so prefer the
[GitHub releases](https://github.com/runpod/runpodctl/releases) binary. Data does **not**
sync between volumes automatically — see golden path
[10 — multi-region HA serverless](../runpod/golden-paths/10-multi-region-ha-serverless.md).

For exact serverless flags, run `runpodctl serverless <action> --help`.

`serverless update --model-reference` includes the server-resolved `modelReferences` in JSON/YAML output. `--clear-models` returns `modelReferences: []`. Other updates do not fetch model references. Use `serverless model-status <id>` to inspect them.

### Templates (alias: tpl)

```bash
runpodctl template search <q>                        # find (+ template list [--type official/community/user, --all, --limit])
runpodctl template get <template-id>                 # details (README, env, ports)
runpodctl template create --name "x" --image "img" [--serverless]
runpodctl template delete <template-id>
```

### Network Volumes (alias: nv)

```bash
runpodctl network-volume list                         # List all volumes
runpodctl network-volume get <volume-id>              # Get volume details
runpodctl network-volume create --name "x" --size 100 --data-center-id "US-GA-1"  # Create volume
runpodctl network-volume update <volume-id> --name "new"  # Update volume
runpodctl network-volume delete <volume-id>           # Delete volume
```

For exact network volume flags, run `runpodctl network-volume <action> --help`.

> **No storage-tier flag.** `create` provisions the data center's **default** tier — there is
> no `--type`. For a **High-Performance** volume, use one of these methods:
> - The console toggle for a ⚡ data center.
> - A **v2 REST** call (`POST https://v2-rest.runpod.io/v2/network-volumes` with
> `"type":"HIGH_PERFORMANCE"`).
>
> - MCP `create-network-volume` with `volumeType` (`STANDARD` | `HIGH_PERFORMANCE`).
> The tier cannot change after creation. Launch details: golden path [21](../runpod/golden-paths/21-storage-tiers.md).

### Models (Model Repository)

`runpodctl model` manages the **Runpod Model Repository** — managed, versioned storage
for your **own** model artifacts (upload once, distributed to workers, not pinned to a
data center like a network volume). What it is, why/how, migrating off a baked-in model,
and Model-Repo-vs-volume: **[reference/model-caching.md](reference/model-caching.md)**.

```bash
runpodctl model list                                  # List your models
runpodctl model list --all                            # List all models (not just yours)
runpodctl model list --name "llama"                   # Filter by name
runpodctl model list --provider "meta"                # Filter by provider
runpodctl model add --name "my-model" --model-path ./model   # Upload a local model dir (multipart)
runpodctl model remove --name "my-model" --owner <owner>     # Remove a model
```

`model add` supports upload sessions, versioning, metadata, and private-source credentials — see live `runpodctl model add --help`.

### Info & SSH

```bash
runpodctl user                                       # account info + balance (alias: me)
runpodctl gpu list                                   # available GPUs + $/hr + per-DC stock (+ --include-unavailable)
runpodctl datacenter list                            # datacenters (alias: dc)
runpodctl ssh info <pod-id>                          # SSH connection details (command + key; NOT an interactive session)
```

**`gpu list` carries pricing and placement data** — `securePricePerHr` /
`communityPricePerHr` (explicitly `null` when that cloud does not offer the GPU) and a
`dataCenterAvailability[]` breakdown. For a specific DC, read the availability breakdown. Top-level `stockStatus` only shows the best status across DCs. Pass `--include-unavailable`. The default list hides no-stock GPUs and can omit a GPU with stock only in your target DC. The prices
are **pod on-demand** rates.

Shape, stock-value vocabulary and the `"none"` vs
omitted-key sentinel:
[reference/output-and-errors.md](reference/output-and-errors.md#gpu-pricing-and-per-data-center-availability).

`ssh info` returns connection details, not a session. If interactive SSH is unavailable, run `ssh user@host "command"`. Read [reference/command-reference.md](reference/command-reference.md) for registry authentication, `billing` history, and SSH key management (`ssh add-key`/`remove-key`).

### File Transfer

```bash
runpodctl send <path>                                # prints a one-time code, then blocks until the receiver connects
runpodctl receive <code>                             # positional code (no --code flag)
```

Transfer is encrypted, incremental, and compressed. Do not pre-tar. Capture the **first line of `send` stdout**, which is the code, as it streams (background + tee). Each `send` creates a **fresh** code. Both sides must exit `0`. Full agent flow (pod push via `ssh` + `receive`): [reference/command-reference.md](reference/command-reference.md#file-transfer).

### Utilities

```bash
runpodctl doctor                                      # Diagnose and fix CLI issues
runpodctl update                                      # Update CLI
runpodctl version                                     # Show version
runpodctl completion                                  # Auto-detect shell and install completion
```

## URLs

### Pod URLs

Access exposed ports on your pod:

```
https://<pod-id>-<port>.proxy.runpod.net
```

Example: `https://abc123xyz-8888.proxy.runpod.net`

### Serverless URLs

Prefer `runpodctl serverless run|status|health` (above) — same api, with auth, validation and
bounded polling handled. Use raw urls for functions that the commands do not cover. These include streaming, the OpenAI-compatible route, and copy-paste `curl` for a user.

```
https://api.runpod.ai/v2/<endpoint-id>/run        # Async request
https://api.runpod.ai/v2/<endpoint-id>/runsync    # Sync request
https://api.runpod.ai/v2/<endpoint-id>/health     # Health check
https://api.runpod.ai/v2/<endpoint-id>/status/<job-id>  # Job status
```

`serverless create`/`get`/`list`/`update` already return `run`/`runsync`/`health` in a
`urls` object — prefer those over hand-assembling, since a non-default
`RUNPOD_INVOKE_URL` changes the base. Only `status/<job-id>` has to be built by hand.

## Source & docs

- CLI source: https://github.com/runpod/runpodctl
- Releases (binaries): https://github.com/runpod/runpodctl/releases
- Documentation: https://docs.runpod.io/runpodctl/overview

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
