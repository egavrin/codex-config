---
name: runpod
description: "Start here for every Runpod task. Scope includes GPU/CPU pods, serverless endpoints, templates, network volumes, image builds, and Runpod concepts. Select the applicable skill (runpod-mcp, runpodctl, flash, companion-clis, runpod-usage, runpod-templates, runpod-migrate). This skill indexes two dozen end-to-end examples verified against live services (golden paths). Use it when the workflow is unclear. Also use it for every multi-step or provisioning task, even when the workflow is clear."
metadata:
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Runpod (router)

The entrypoint for the Runpod skills. This skill does no work itself — it picks
the right lane and hands off. For a multi-step or provisioning task, first examine the [worked examples](#worked-examples-golden-paths). Use the matching example to select the workflow. Otherwise, read the matching skill's `SKILL.md` next.

## The lanes

| Lane | Use it for |
| --- | --- |
| **runpod-mcp** | Manage infra (pods, endpoints, jobs, templates, volumes, registries, catalog, billing) via **structured tool calls** — when the Runpod MCP tools are connected in this session. |
| **runpodctl** | Manage the same infra from a terminal/CI/script. CLI-only functions include Hub browse/deploy, `send`/`receive` file transfer, SSH keys, `doctor` setup, and model cache. |
| **flash** | **Write Python** that runs on Runpod serverless — `@remote`/`@Endpoint` functions, `flash dev` hot-reload, `flash deploy`. Code-first, not infra management. |
| **companion-clis** | Prerequisite artifacts: download a model (`hf`) and build/push an image (`docker`). Manage repos/releases (`gh`) and move data to a network volume over S3 (`aws`). |
| **runpod-usage** | **Understand** how Runpod works before acting — pods vs serverless, building a container, storage, GPU selection, gotchas. Knowledge only. |
| **runpod-templates** | Official prebuilt pod templates (ComfyUI, PyTorch, …). Identify a template for the workload. Examine its image contents: ports, paths, autostart, readiness, and first-boot omissions. Reference + routing hub. Deploy via runpod-mcp/runpodctl. |
| **runpod-migrate** | Move existing code off the GraphQL API or REST v1 onto REST v2. Inventory which parts use which version. Rewrite call sites and flag breaking changes. Edits the user's code. Does not manage infra. |

## These skills are a snapshot; the tools are the source of truth

Every lane below wraps something that ships on its own release train and moves faster than
this repo. So route with these skills, but **take capability and syntax from the tool in front
of you**:

| Lane | Ask it directly |
| --- | --- |
| runpodctl | `runpodctl --help`, `runpodctl <resource> <action> --help`, `runpodctl version`. For failure shapes, run a command wrong on purpose and read the JSON |
| runpod-mcp | your client's tool list (`/mcp` in Claude Code) — each tool carries its own parameter descriptions |
| flash | `flash --help`, and the deploy/dev output |
| companion-clis | that CLI's own `--help` (`hf`, `gh`, `docker`, `aws`) |
| runpod-templates | `runpodctl template list --type official`, `template get <id>` (its readme is authoritative) |
| REST v2 | the live spec at `https://api.runpod.io/v2/openapi.json` |

**Examine current capability before you tell a user that a tool cannot do something.** Such claims easily become stale and give readers little reason to investigate again. This occurred twice: runpodctl v2.9.0 added `serverless health`, and v2.10.0 added `pod logs`/`serverless logs`. If a limit still holds, name the version it holds for
rather than saying "cannot".

## First run — check auth before the first infra action

For infrastructure tasks (pods, endpoints, jobs, volumes), use a working control plane — the **Runpod MCP**
or **runpodctl**. Examine setup before work starts. If setup is incomplete, help the user complete it. Do not continue with a partial fallback.

**Examine credentials** (credential resolution order: `RUNPOD_API_KEY` env → `.env` → `~/.runpod/config.toml`):
```bash
runpodctl user            # succeeds ⇒ a key is set and valid
```
Plus, in Claude Code, `/mcp` should show `runpod` **Connected**.

**Get a key first. Do not default to MCP OAuth.** One `RUNPOD_API_KEY` authenticates **runpodctl + flash + the hosted MCP**. The MCP header is `--header "Authorization: Bearer $RUNPOD_API_KEY"`. The MCP's "Sign in with Runpod" OAuth authenticates **MCP alone**. The CLIs remain blocked.

This prevents CLI-only work: Hub, `send`/`receive`, SSH, `doctor`, model cache/Model Repository, and CPU endpoints. ⚠️ **OAuth-only setup is incomplete.** If no setup exists, stop and get a key in this order:
1. **`flash login`** — browser OAuth that saves a real key to `~/.runpod/config.toml` (runpodctl
   + flash read it, reuse it for the MCP Bearer). One step, unlocks all. Human-only.
2. **`export RUNPOD_API_KEY=…`** (https://console.runpod.io/user/settings) — same full unlock.
   Best for headless agents.
3. **MCP OAuth only** (`/mcp` → *Sign in*) — last resort, MCP-only work. CLIs stay unauthed.

**Then:** If a tool route already works, use it. If only MCP has OAuth authentication, obtain a key before any CLI-only step. Missing a CLI? `curl -sSL https://cli.runpod.net | bash` (runpodctl) ·
`uv tool install runpod-flash` (flash) · `npx @runpod/mcp-server@latest add` (MCP). Full setup:
[`runpod-usage/reference/getting-started.md`](../runpod-usage/reference/getting-started.md).

## How to route

**0. Does a worked example already cover this?** For work beyond one call, first read [the golden-paths index](#worked-examples-golden-paths). Then, select the workflow. A matching example already states the applicable tools, flags, order, and known problems. Examine it when **any** of these is true:

- the task includes **more than one resource** (image + template + endpoint, pod + volume,
  multi-region, …) or **more than one lane**
- it **provisions something billable**, or the user's ask is shaped like *"get X running /
  deployed / working"*
- it involves **storage, networking, autoscaling, streaming, or debugging a live resource** —
  the areas where the non-obvious ordering is the whole difficulty
- you are about to write a **multi-step plan** for it

Skip step 0 for a single read or CRUD call ("list my pods", "stop pod X", "what GPUs are available"). Go directly to the applicable workflow. **A matching golden path takes precedence over this router's table.** It was verified end to end on a real account. If the two disagree, follow the golden path and report the difference as a potential defect.

1. **Conceptual question, or an unmade design choice** (serverless vs pod? which
   GPU? bake the model or mount a volume?) → read **runpod-usage** first, then
   continue with the answer.
2. **For a common pod workload or a template-pod repair, use runpod-templates.** Examples include "run ComfyUI /    PyTorch dev box", boot failure, and missing models. Examine official prebuilt options before an installation plan. Let that skill select the repair workflow.
3. **Write/iterate/ship your own code on Runpod GPUs** → **flash**.
4. **Produce an artifact** (download a model, build+push an image, create a repository
   release, sync data to a volume) → **companion-clis**.
5. **Migrate existing code between Runpod API versions** — "move us to REST v2",
   "which Runpod API is this repo on?", "what breaks if we upgrade?" →
   **runpod-migrate**. (Calling the API to *do* something is a different job, that
   is the infra lanes below.)
6. **Manage infrastructure** (create/list/update/delete pods, endpoints,
   templates, volumes, list GPUs/data centers, run a serverless job, billing):
   - Capability only the CLI has — **Hub, `send`/`receive`, SSH keys, `doctor`,
     model cache** → **runpodctl**.
   - Otherwise, if the Runpod **MCP tools are connected** in this session
     (`create-pod`, `list-endpoints`, … are available) → **runpod-mcp**.
   - Otherwise (shell-only agent, no MCP) → **runpodctl**.

### runpod-mcp vs runpodctl (the overlap)

Both drive the same Runpod API, so they overlap on infra CRUD. Choose by
**capability first, environment second**:

- **MCP wins on convenience** for simple, structured operations — reads and basic
  CRUD — when its tools are connected (typed parameters, no shell quoting).
- **Use runpodctl when a necessary capability is absent from MCP**, even if MCP is connected. It is the only option for a shell-only agent or a user-requested reproducible command.

Capability matrix (pick the preferred lane per operation):

| Operation | Preferred lane | Why |
| --- | --- | --- |
| List/get anything. Start/stop/restart/delete a pod. Simple CRUD on endpoints, templates, volumes, registries, catalog, billing | **runpod-mcp** if connected, else runpodctl | Simple structured ops — MCP is typed and convenient |
| Create a **simple** pod (one image + one GPU) | **runpod-mcp** if connected, else runpodctl | Both handle it |
| Create a pod **from a template** or a **CPU** pod | **runpod-mcp** if connected, else runpodctl | MCP's create-pod takes `templateId` (v2-only) and `computeType: "CPU"` |
| Create a pod with a **multi-GPU priority list**, or **template + CPU together** | **runpodctl** | MCP narrows to one GPU type, and rejects a template deploy for a CPU pod |
| Deploy from the **Hub** | **runpod-mcp** if connected, else runpodctl | MCP has `list-hub-repos` + `deploy-hub-repo` |
| **File transfer** (`send`/`receive`), **SSH** keys/info, **`doctor`** setup, **model** cache | **runpodctl** | MCP has no tool for these |
| Invoke a serverless job (`run`/`runsync`/status/stream) | **runpod-mcp** if connected, else runpodctl | Both lanes have first-class job commands now (runpodctl `serverless run`/`status`/`health`, v2.9.0+). MCP is typed, and only MCP streams a job's incremental output (`stream-job`) |
| Read **pod or worker logs** | **either** — runpod-mcp if connected, else runpodctl | Both lanes read them: MCP `stream-pod-logs`/`stream-worker-logs` return parsed frames. Runpodctl `pod logs`/`serverless logs` emit json lines and `--follow` (v2.10.0+) |

Rule of thumb: **Use MCP by default for simple operations. Change to runpodctl when a necessary flag/feature is absent from MCP.**

## Deploying a workload (the golden loop)

For every "get <X> running on Runpod" task, follow `runpod-usage/reference/development-loop.md`. Select pod or serverless, provision, install from scratch only when necessary, validate, and deliver. Then, apply cost controls and remove temporary resources. Two rules bind within it:

- Prefer a prebuilt template / Hub worker to an image built from source. [`runpod-templates`](../runpod-templates/SKILL.md) indexes official pod templates.
- Before delivery, test the workload with a real request from outside the pod/endpoint. A "Running"/"ready" status does not prove that it serves requests.
- **Default to Secure Cloud.** Community Cloud hosts are approved vendors. Secure Cloud
  hosts are data-center-grade providers and so tend toward more stable behavior. Only
  deploy Community when the user explicitly asks. (`runpodctl pod create` already
  defaults to `--cloud-type SECURE`, do not override it.)
- **Select cache versus network volume by latency, not cost.** Download time is never billed. On a cache miss, Runpod delays worker start until the model arrives. The job stays queued and the endpoint appears idle.

  Latency-sensitive → pre-load a
  network volume. Otherwise the cache is the cheaper default. Cache capacity is per
  machine, so time both on the user's own endpoint rather than quoting a threshold.

  See
  [`runpodctl/reference/model-caching.md`](../runpodctl/reference/model-caching.md).

It branches to two sub-loops:

- **Service you open at a URL** (Ollama, ComfyUI, dev box) →
  [`runpod-usage/reference/pod-workflows.md`](../runpod-usage/reference/pod-workflows.md)
  (ports + env + volume at creation, SSH-exec install, bind `0.0.0.0`, poll the
  proxy URL). Execute in the runpodctl lane.
- **Request/response API that scales to zero** (Whisper, inference) →
  [`runpod-usage/reference/endpoint-workflows.md`](../runpod-usage/reference/endpoint-workflows.md)
  (Hub worker vs flash vs custom image, invoke `/run`/`/runsync`, poll job status).

## Worked examples (golden paths)

This is **step 0 of routing**, not an appendix. [`./golden-paths/README.md`](./golden-paths/README.md) contains two dozen end-to-end scenarios. Nearly all have **live verification on a real account**. Each includes real commands, observed output, Known problems, and Cost & cleanup sections. These details are expensive to discover again.

**Match the task to a row below. Open that path before plans or tool calls.** Also read a partial match. Its order and known problems often apply even when the model, GPU, or region differs. Only fall through to the lane
tables above when nothing here is close.

| Want to… | Golden path |
| --- | --- |
| Run a server (Ollama/ComfyUI) on a pod at a URL | [01](./golden-paths/01-ollama-pod.md), [02](./golden-paths/02-comfyui-pod/README.md) |
| Deploy a serverless model endpoint (Hub / flash / custom image) | [03](./golden-paths/03-whisper-endpoint/README.md), [05](./golden-paths/05-model-to-endpoint-pipeline.md) |
| Serve a HuggingFace model without baking it in or a volume (host-cached) | [20 — model caching (`--model-reference`)](./golden-paths/20-model-caching-endpoint.md) |
| Call a ready hosted model (no deploy) | [11 — Public Endpoints](./golden-paths/11-public-endpoints.md) |
| Fine-tune, then serve the result | [04](./golden-paths/04-finetune-pod.md), [08](./golden-paths/08-finetune-to-serverless.md) |
| Interactive dev box (SSH / VS Code) | [06](./golden-paths/06-dev-pod.md) |
| Move data pod → volume → serverless | [07](./golden-paths/07-network-volume-handoff.md) |
| **Custom serverless when flash is not enough** (dual-mode image dev loop) | [09](./golden-paths/09-custom-serverless-dev-loop/README.md) |
| Build a minimal image for a target (pod vs serverless queue) | [22 (pod)](./golden-paths/22-minimal-pod-image/README.md), [23 (queue)](./golden-paths/23-minimal-queue-image/README.md), concepts in [building-images](../runpod-usage/reference/building-images.md) |
| Decide what to bake into the image vs mount on a network volume | [25 — bake vs mount](./golden-paths/25-bake-vs-mount/README.md) |
| Pick a network-volume **storage tier** (standard vs high-performance) | [21 — storage tiers](./golden-paths/21-storage-tiers.md) |
| **High availability / multi-region** serverless (multi-volume + data sync) | [10](./golden-paths/10-multi-region-ha-serverless.md), [19 (3-region)](./golden-paths/19-three-region-same-file.md) |
| Stream output incrementally (`/stream`) | [12](./golden-paths/12-serverless-streaming.md) |
| Tune autoscaling / raise per-worker throughput | [13 (autoscaling)](./golden-paths/13-autoscaling-tuning.md), [18 (concurrency)](./golden-paths/18-concurrent-handler.md) |
| Load-balancing / HTTP-server or WebSocket worker | [14 (LB)](./golden-paths/14-load-balancing-endpoint.md), [17 (WebSocket)](./golden-paths/17-serverless-websocket.md) |
| Get notified on job completion (push, not poll) | [16 — webhooks](./golden-paths/16-serverless-webhooks.md) |
| Examine health / debug a failing endpoint | [15 — monitor & debug](./golden-paths/15-monitor-and-debug.md) |

## Multi-lane tasks

The sequence is always understand → produce artifacts → manage infra → test. Infra can only reference artifacts that already exist. Keep each step in
one lane, and switch lanes at credential boundaries.

Example — "deploy `openai/gpt-oss-20b` to a serverless endpoint":
1. **runpod-usage** — serverless vs pod, GPU tier for 20B, bake vs mount vs cache.
2. **companion-clis** — `hf download …`, `docker build --platform=linux/amd64 …`, `docker push`.
3. **runpod-mcp** or **runpodctl** — create the endpoint referencing the image + GPU pool.
4. Same infra lane — invoke the endpoint and examine status to make sure that the operation succeeded.

## Auth

Everything is one key: **`RUNPOD_API_KEY`** (https://console.runpod.io/user/settings).
Each lane just makes that key resolvable — `runpodctl doctor`, `flash login`, MCP
stdio environment variable, or MCP hosted "Sign in with Runpod" (OAuth, no key on disk).
Companion CLIs use their **own** credentials (HuggingFace token, GitHub auth,
Docker Hub PAT, Runpod **S3** keys for `aws`) — do not reuse `RUNPOD_API_KEY` for
those.

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
