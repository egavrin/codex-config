# Getting a model to a serverless worker

Four ways to make model weights available to a Runpod serverless worker. Pick by
where the weights come from, how large/private they are, and how often they change.

| Method | How | Best when | Cold start |
|--------|-----|-----------|-----------|
| **Bake into image** | `COPY`/download during `docker build`, push to a registry | small/private weights, fully reproducible image | fast (in image) but bloats pulls |
| **HF model cache** (`--model-reference`) | point the endpoint at a HuggingFace model URL. Runpod caches it host-side | the model is already on HuggingFace (public/gated/private) | fastest — host-cached, no download billing |
| **Network volume** | pre-load weights onto a DC-pinned volume, mount it | large weights reused across workers. You manage the files | fast once populated. Volume is pinned to one data center |
| **Model Repository** (`runpodctl model`) | upload your **own** artifacts to Runpod-managed, versioned storage | private/custom models not on HuggingFace, without image bloat or a DC-locked volume | managed + host-distributed |

For HuggingFace models, use the **HF cache**. For your artifacts, use **Model Repository**, or a network volume if you want to manage the filesystem. For a fully reproducible image or included system libraries, **bake** the model into the image. Cache vs volume is a latency
call, not a cost call — see the next section before choosing.

## Cache or network volume — it is a latency call, not a cost call

**You are not billed for model download time, cache hit or miss.** If no host already holds the model, Runpod's documentation states: "the system delays starting your workers
until the model is downloaded onto the machine where your workers will run, ensuring you
still won't be charged for the download time."

So the thing a cache miss costs you is **time to first response**, not money. The **job stays in the queue** while Runpod delays worker startup for the download. This state can look like a fault. From the outside that looks like a stuck or idle
endpoint, not a download. It is not broken — it is the miss path.

### How the cache actually works

Three tiers, nearest first ([Runpod engineering
blog](https://www.runpod.io/blog/building-runpods-model-store)): **host-local disk** →
a **data-center-scoped network volume** → the **origin** (HuggingFace). The scheduler is
locality-aware — it prefers hosts that already have the model, or can reach it from a
nearby cache. On a miss, one worker downloads and then everyone in that data center
reads the shared copy. Runpod's own writeup says quota and eviction policy on that
DC-scoped tier are "still open problems, not solved ones", and that a full volume falls
back to origin downloads. Treat residency as best-effort, not a guarantee.

**Capacity applies per machine.** The host tier uses a share of each machine's disk. Thus, the same model can fit on one host but not another. That is why there is no cache-size
number to look up, and why two workers on the same endpoint can cold-start at very
different speeds.

**An unavailable tier fails without an error.** This occurs when the data center lacks shared-copy support or its storage is full. The
endpoint falls back to per-host downloads and just feels slower. Inconsistent cold
starts across workers on one endpoint are the normal symptom, not a bug to chase.

### Which to pick

| Situation | Use |
|---|---|
| **Latency-sensitive** — user-facing, tight SLA, or you scale into fresh regions often and cannot absorb a first-request stall | **Network volume**, pre-loaded. Costs storage per month, but the weights are already there. |
| **Not latency-sensitive**, or the model is not huge | **HF model cache** (`--model-reference`). Free, nothing to pre-load, and a hit is seconds. |
| Unsure | **Test both.** This is a measurable trade, not a rule. Deploy each option and time its cold start on your model, in your region. |

**Measure your endpoint. Do not use another environment's numbers as proof.** This beta feature currently behaves differently across accounts and hosts. A
benchmark from a blog post, a forum thread, or another endpoint tells you very little
about what yours will do.

Two constraints affect large models. Cache capacity changes with the host, so residency has no guarantee.
A network volume is **pinned to one data center**.
For multiple regions, use one pre-loaded volume per DC (golden path [10](../../runpod/golden-paths/10-multi-region-ha-serverless.md)).

To measure it, watch the worker logs on a cold start in a fresh region (`runpodctl
serverless logs <endpoint-id>`, or the MCP `stream-worker-logs`). Weight-download time in
**minutes** rather than seconds means that region is not carrying the model for you.

### Regional availability — unknown, do not guess

**Runpod publishes no list of data centers with model-cache support.** The [cached models documentation](https://docs.runpod.io/serverless/endpoints/model-caching) give no regional restriction. The engineering blog describes the shared tier only as "scoped per datacenter". Third-party posts claim it is region-limited. None cite a
source. **Do not state a supported-region list to a user.**

Examine which data centers offer network volumes. The shared tier uses that per-DC storage. Without network-volume support, a data center cannot supply a shared copy. Its workers use per-host downloads instead. Read it live, do not memorize it:

```bash
# MCP: list-data-centers  →  networkVolumeTypes
```

Snapshot 2026-09-22: **17 of 33** data centers report a `networkVolumeTypes` value:

- `AP-JP-1`.
- `CA-MTL-3`.
- `CA-MTL-4`.
- `EU-FR-1`.
- `EU-NL-1`.
- `EU-RO-1`.
- `EUR-IS-1`.
- `EUR-IS-3`.
- `EUR-NO-1`.
- `EUR-NO-2`.
- `US-CA-2`.
- `US-CO-1`.
- `US-IL-1`.
- `US-MO-2`.
- `US-NC-2`.
- `US-TX-3`.

Network storage is necessary but does not prove model-cache support. Present this as **a list for investigation**, not the official model-cache region list. To make sure that support exists for a specific
region, deploy there and measure the first cold start.

### Documented limits

- **One cached model per endpoint** ([documentation → Current
  limitations](https://docs.runpod.io/serverless/endpoints/model-caching)). `runpodctl`
  accepts `--model-reference` repeatedly, so the CLI will take more than one — the
  platform limit is the binding one.
- **All quantizations get downloaded.** If a HF repository holds several (4-bit AWQ, 8-bit
  GPTQ, …), the system currently pulls them all. You cannot select one yet.
- The feature is **beta**.

## HF model cache — `--model-reference`

Attach a HuggingFace model to an endpoint with its full URL and ref. Runpod caches it on the host for direct worker loads. No image copy or volume is necessary.

```bash
runpodctl serverless create --template-id <id> --gpu-id "NVIDIA GeForce RTX 4090" \
  --model-reference https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct:main
```

- The trailing `:main` is the branch/tag/revision.
- Weights land in the standard HF cache dir `/runpod-volume/huggingface-cache/hub/`
  (`models--{org}--{name}/snapshots/{hash}/`), so anything that reads the HF cache
  (Transformers, vLLM, …) picks it up automatically.
- The CLI flag is repeatable, but the platform currently supports **one cached model per
  endpoint** (documentation → Current limitations).
- Works with `--template-id` **and** `--hub-id`, but **GPU only** (`--compute-type GPU`).
- **runpodctl v2.4.0+ is necessary.** Examine `runpodctl version`. The Homebrew tap can lag —
  prefer the [GitHub releases](https://github.com/runpod/runpodctl/releases) binary.
- Gated/private HF models: provide an `HF_TOKEN` (endpoint environment variable).

You are **not billed for download time** — hit or miss. Cold starts take seconds when the host already has the model. Otherwise, Runpod delays worker startup until the download completes. The job then stays in the queue longer. See
[Cache or network volume](#cache-or-network-volume--it-is-a-latency-call-not-a-cost-call).

## Model Repository — `runpodctl model`

Runpod-managed **storage + registry for your own model artifacts**. Upload weights once. Runpod stores, versions, and distributes them to workers. The model object has a name, versions, metadata, and a status lifecycle.

```bash
runpodctl model list                                  # list your models
runpodctl model list --all                            # include models you don't own
runpodctl model list --name "llama"                   # filter by name
runpodctl model list --provider "meta"                # filter by provider
runpodctl model add --name "my-model" --model-path ./model   # upload a local model directory
runpodctl model remove --name "my-model" --owner <owner>     # remove a model
```

`model add` runs a **multipart upload session** (built for large weights) — the live
`runpodctl model add --help` exposes `--create-upload`, `--part-size`, `--file-size`,
`--file-name`, `--content-type`, `--metadata key=value`, `--model-status`,
`--version-status`, and `--credential-reference`/`--credential-type` (for pulling from a
private source). Run it before relying on exact syntax — it is authoritative.

To migrate a model from an image, stop the `COPY` of its weights. Run `runpodctl model add --model-path <the same dir you used to COPY>`. Then, reference the uploaded model from the endpoint. This shrinks the image and
lets you version the weights independently of the code.

A **network volume** is a raw filesystem that you manage. It is **pinned to one data center**, where its workers must run. The managed Model Repository supplies versions and distributes models across hosts. It has no single-DC restriction. Use a volume for direct filesystem control or an existing population workflow. Use Model Repository for a managed, versioned artifact.

> **Runtime-load path — do not guess.** The command surface above (`runpodctl model add`)
> is from live `runpodctl --help` and is accurate for *uploading*. Public documentation does **not yet explain** how a worker references an uploaded Model Repository artifact at runtime.
> If asked for runtime-load steps for a `runpodctl model add` artifact, state this limit.
>
> Do not invent a path.
>
> The HF **model-caching** feature has a documented runtime path. It uses the `--model-reference` flag / endpoint "Model" field.
> The model is in `/runpod-volume/huggingface-cache/hub/`.
>
> The handler resolves the local snapshot there and loads offline with `HF_HUB_OFFLINE=1`. See golden path 20 and the official
> example `runpod-workers/model-store-cache-example`.
