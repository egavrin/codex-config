# Golden paths

These end-to-end tasks measure whether an agent can complete Runpod workflows independently from start to finish. They also provide worked references for reuse.
The original evaluation question is "can it actually do everything agentically".

These are agent-facing scenarios, not marketing demos. An agent must complete the tasks without a human operating Console. Paths 01–19 ran live on a real account and exposed skill gaps that informed subsequent fixes. The commands and outputs are real. Every test resource was removed afterward. Path 04's training phase ran as part of 08.

Paths 01–10 ran 2026-07-07→10, and 11–19 ran 2026-07-13. Path 20 was live-verified 2026-07-15 (diagnosed via the Runpod MCP
worker logs — a `COMPLETED` job off a `--model-reference` cache hit). Path 21 documents
**provisioning (launch) only** — verified against the CLI/REST specs + MCP source (2026-07-16),
not a full live run. Paths 22, 23, and 25 (minimal-image + storage-model paths) were added
2026-07-16 and **run live** (built, pushed, deployed, invoked/SSH'd, torn down). The
load-balanced image contract is covered by the already-live-verified [path 14](14-load-balancing-endpoint.md).

## Before you run any path (shared prerequisites)

Every path assumes this baseline — set it up once, then follow the path:

- Resolve `RUNPOD_API_KEY` or use `runpodctl doctor` / MCP OAuth. For any pod workflow, register an SSH key before pod creation. Full setup:
  [`../../runpod-usage/reference/getting-started.md`](../../runpod-usage/reference/getting-started.md).
- For image workflows, run `docker` and `docker login` for a registry with push access. Some also use `hf` with an HF token or `aws` with Runpod S3 keys. S3 keys are Console-only. An agent cannot create them independently. See
  [`../../companion-clis/SKILL.md`](../../companion-clis/SKILL.md).
- Fill placeholders such as `<template-id>`, `<endpoint-id>`, and `<vol-…>` with actual returned IDs. Reuse those IDs in subsequent steps.
  Docker images named `<your-registry>/gpNN-…` represent original live-run images. You cannot push to that namespace. Run `docker login` and substitute your own namespace. IDs inside "observed output" blocks are historical evidence, not values to paste.
- For a few paths, runpodctl ≥ v2.4.0 is necessary (multi-volume attach). The Homebrew tap can have an older version. If `runpodctl version` is behind, install from [GitHub releases](https://github.com/runpod/runpodctl/releases).

## Layout

- A path with **one approach** is a single file: `NN-name.md`.
- A path with **multiple approaches** is a folder: `NN-name/` with a `README.md`
  (goal, "which variant?", shared schema/gotchas/cost) plus one file per variant.

Each document follows this template:

- Goal · Status · Lane(s).
- When to use.
- Prerequisites.
- Walkthrough (real commands).
- Verify it works (the actual test + observed output).
- Known problems we hit.
- Cost & cleanup.
- Skill gaps folded back.

## Table of contents

| # | Golden path | Kind | Approach(es) | Status |
| --- | --- | --- | --- | --- |
| 01 | [Ollama server on a pod + URL](01-ollama-pod.md) | pod / server | runpodctl pod + SSH | ✅ live-verified |
| 02 | [ComfyUI server on a pod + URL](02-comfyui-pod/README.md) | pod / server | — | ✅ live-verified |
| | ↳ [Variant A — from scratch](02-comfyui-pod/variant-a-from-scratch.md) | | PyTorch template + install | ✅ |
| | ↳ [Variant B — prebuilt official image](02-comfyui-pod/variant-b-prebuilt.md) | | official template (auto-starts) | ✅ (faster) |
| 03 | [Whisper endpoint (audio → text)](03-whisper-endpoint/README.md) | serverless | — | ✅ live-verified |
| | ↳ [Variant A — Runpod Hub worker](03-whisper-endpoint/variant-a-hub.md) | | runpodctl + Hub (recommended) | ✅ |
| | ↳ [Variant B — from scratch with flash](03-whisper-endpoint/variant-b-flash.md) | | flash code-first handler | ✅ |
| 04 | [LoRA fine-tune (training run) on a pod](04-finetune-pod.md) | pod / batch job | runpodctl pod + volume | ✅ live-verified (training phase, via 08) |
| 05 | [Custom model → serverless endpoint](05-model-to-endpoint-pipeline.md) | cross-lane pipeline | hf → docker → runpodctl | ✅ live-verified |
| 06 | [Interactive dev pod (SSH / VS Code)](06-dev-pod.md) | pod / interactive | runpodctl pod + volume | ✅ live-verified |
| 07 | [Network-volume handoff (pod → volume → serverless)](07-network-volume-handoff.md) | pod + serverless | runpodctl + flash | ✅ live-verified |
| 08 | [Fine-tune → serve (LoRA on a pod → serverless)](08-finetune-to-serverless.md) | train → serve loop | runpodctl + peft/axolotl + flash | ✅ live-verified |
| 09 | [Custom serverless dev loop (iterate in a pod → dual-mode image → serverless)](09-custom-serverless-dev-loop/README.md) | custom image / escape hatch | runpodctl + docker (dual-mode `MODE_TO_RUN`) | ✅ live-verified |
| 10 | [Multi-region HA serverless (multi-volume + data sync)](10-multi-region-ha-serverless.md) | serverless / availability | runpodctl ≥v2.4.0 (`--network-volume-ids`) + S3 API (aws) | ✅ live-verified |
| 11 | [Public Endpoints (call a ready hosted model)](11-public-endpoints.md) | serverless / hosted | Runpod Public Endpoint API (native + OpenAI-compatible) | ✅ live-verified |
| 12 | [Serverless streaming (`/stream`)](12-serverless-streaming.md) | serverless | generator handler + `/stream` | ✅ live-verified |
| 13 | [Autoscaling tuning](13-autoscaling-tuning.md) | serverless / scaling | runpodctl + scaler config (queue-delay / request-count) | ✅ live-verified |
| 14 | [Load-balancing endpoint (non-flash)](14-load-balancing-endpoint.md) | serverless / LB | GraphQL `saveEndpoint type:"LB"` + HTTP-server worker | ✅ live-verified |
| 15 | [Monitor & debug / observability](15-monitor-and-debug.md) | serverless / ops | `runpodctl serverless health`/`status`/`logs` (or `/health` + `/status` + v2 REST / MCP worker logs) + config-change events | ✅ live-verified |
| 16 | [Serverless webhooks](16-serverless-webhooks.md) | serverless | `webhook` field on `/run` (push vs poll) | ✅ live-verified |
| 17 | [Serverless WebSocket worker](17-serverless-websocket.md) | serverless / LB | `worker-lb-websocket` + `wss://<ep>.api.runpod.ai/ws` | ✅ live-verified |
| 18 | [Concurrent handler (per-worker concurrency)](18-concurrent-handler.md) | serverless / throughput | async `concurrency_modifier` | ✅ live-verified |
| 19 | [3-region same-file endpoint](19-three-region-same-file.md) | serverless / availability | 3 volumes + S3 sync + GraphQL multi-volume attach | ✅ live-verified |
| 20 | [Host-cached HF model endpoint (`--model-reference`)](20-model-caching-endpoint.md) | serverless / model delivery | runpodctl ≥v2.4.0 (`--model-reference`) + vLLM worker | ✅ live-verified |
| 21 | [Network volume storage tiers (standard vs high-performance)](21-storage-tiers.md) | storage / provisioning | runpodctl (standard) + REST v2 / console (high-perf) | 📘 documented (launch only) |
| 22 | [Minimal pod image (+ do not kill SSH)](22-minimal-pod-image/README.md) | image contract / pod | docker buildx + runpodctl pod (CPU) + SSH | ✅ live-verified |
| 23 | [Minimal serverless queue image](23-minimal-queue-image/README.md) | image contract / serverless | docker buildx + runpodctl serverless (CPU) + `/runsync` | ✅ live-verified |
| 25 | [Bake into image vs mount a network volume](25-bake-vs-mount/README.md) | storage model / image | docker buildx + runpodctl nv + CPU pod (`df -T`: overlay vs MooseFS) | ✅ live-verified |

> For two-variant paths, prefer the prebuilt/Hub option unless custom code is necessary.
> This means ComfyUI Variant B or Whisper Variant A.
> It follows the development loop's "prefer prebuilt over from-scratch" rule.

> Complementary pairs: 13 covers autoscaling, while 18 covers concurrency and per-worker throughput.
> Paths 14 and 17 share `type:"LB"` for load balancing and WebSockets.
> Paths 10 and 19 cover multi-volume HA in 2 and 3 regions.
> Paths 22 and 23 build minimal pod and queue images. [14](14-load-balancing-endpoint.md) supplies the load-balanced counterpart.
> Both paths implement the same "build a tiny image" task.
> These minimal images also evaluate [building-images.md](../../runpod-usage/reference/building-images.md).

## How to use these

1. **Match your task to a row** in the table (or read
   [`../../runpod-usage/reference/development-loop.md`](../../runpod-usage/reference/development-loop.md)
   first if you are unsure whether it is a pod or a serverless job).
2. For a multi-variant path, first open the folder `README.md`. It identifies the variant and supplies the shared schema, known problems, and cost. Then open the
   variant file for the step-by-step.
3. **Examine Status before use.** ✅ live-verified paths have real commands and outputs from complete runs.
   ⚠️ spec paths derive from documentation and are **unproven**.
   Treat their exact flags/paths as unconfirmed. Each file lists the necessary live-run results.
4. **Follow the Walkthrough, then actually run Verify** — "Running" ≠ "ready".
   Do not report success until the service answers a real request.
5. If a live run exposes a skill gap, apply the fix to the relevant `SKILL.md` / `reference/*.md`. Each path's "skill gaps folded back" section provides examples.

## Status legend

- **stub** — goal captured, not yet specified.
- **drafted — gaps identified** — flow + acceptance criteria written. Skill gaps listed.
- spec (not yet live-verified): The complete flow, acceptance criteria, and known problems derive from skills and documentation. The workflow has not run end to end. Validate exact flags and paths on a real account.
- **covered** — the skills contain all necessary agent instructions. Verified by a run.
- **✅ live-verified** (used in the table above) — run end to end on a real account. The
  commands and the "observed output" blocks are from that run.
- **📘 documented (launch only)** (used in the table above) — the provisioning/launch steps
  are written and grounded in the CLI/REST specs, but a full end-to-end run was not performed.

## Cross-cutting requirements (every path)

1. **Auth** — resolve `RUNPOD_API_KEY` (or `runpodctl doctor` / MCP OAuth) before acting.
2. **Agentic execution** — an agent has no Console/web terminal. It must drive
   everything through the CLI/API/MCP and SSH-exec, non-interactively.
3. **Readiness, not fire-and-forget** — poll until the service actually answers.
   Do not report success on "pod Running" alone.
4. **Escalate on manual steps** — if human action is necessary (OAuth, a quota
   increase, a license click, a missing credential), stop and tell the user.
5. **Clean up** — set `--stop-after` / `--terminate-after` on test resources.
