# Golden path 09 — custom serverless the hard way (iterate in a pod, then flip to serverless)

**Goal:** Deploy a **custom** serverless endpoint when no suitable Hub worker exists and `flash` decorators cannot express the workload. Reasons include custom system packages, specific torch/CUDA versions, custom model loading, and complex startup.
Use one image and one handler with two run modes. Develop the handler interactively on a GPU pod (`python handler.py` in a loop).

Then, change one env var (`MODE_TO_RUN=serverless`) so the same code becomes an endpoint.
Worked example: a whisper **speech → text** handler.
**Status:** COVERED — live-verified 2026-07-10 end to end. The complete loop ran on a real account.

An RTX 4090 pod (`runpod-torch-v280`) transcribed the JFK sample with `python handler.py`. The image built with `--platform linux/amd64` and pushed to `<your-registry>/whisper-dualmode:v1` reproduced the result in a clean `/app`. A serverless endpoint from that image (`MODE_TO_RUN=serverless`) returned the **same transcription** for the same audio. This confirmed pod↔serverless parity.

The commands/outputs below are the
real ones. Known problems hit live are folded in. The [`template/`](template/) files are
**vendored into this path and self-contained** — the walkthrough has no external dependency.

They were originally adapted from the community repository
[justinwlin/Runpod-GPU-And-Serverless-Base](https://github.com/justinwlin/Runpod-GPU-And-Serverless-Base)
(provenance only, not required to run this).
**Lane(s):** runpodctl (pod + template + serverless) + docker (build/push) + Runpod REST (`/run`, `/status`) + Runpod MCP (`stream-worker-logs`, for diagnosis)

## When to use this — the escape hatch

The [development loop](../../../runpod-usage/reference/development-loop.md) says
**prefer prebuilt** (Hub worker) then **flash** before building an image. Reach for
this path only when both fall short:

| Situation | Use instead |
| --- | --- |
| A maintained Hub worker does the job | Hub worker (golden path [03](../03-whisper-endpoint/variant-a-hub.md)) |
| Pure-Python handler, standard dependencies | **flash** (golden path [03](../03-whisper-endpoint/variant-b-flash.md)) |
| **Custom apt/system dependencies, pinned CUDA/torch, heavy or unusual startup, or interactive GPU diagnosis before image creation is necessary** | **this path (09)** |

09 is slower than flash. It gives a real GPU shell for development and complete image control. Use it for live diagnosis of a new workload that fails in serverless.

## The core idea: one handler, two modes

```
                       MODE_TO_RUN
                            |
        +-------------------+--------------------+
        | pod (default)                          | serverless
        v                                        v
  start.sh: SSH + Jupyter, sleep            start.sh: python handler.py
  you SSH in, run `python handler.py`  -->  runpod.serverless.start({handler})
  → runs handler() ONCE on a sample         → runs handler() PER JOB
        \______________  same handler.py, same module-level model load  ____________/
```

The invariant: the model loads at **import time** (module level — the cold-start
rule), and `handler(event)` is the **same function** both modes call. So whatever
`python handler.py` proves on the pod is what the serverless worker will do. No
"works in dev, breaks in prod" gap.

## The template (vendored in [`template/`](template/))

A trimmed, whisper-flavored version of the base repo. Four files:

| File | Role |
| --- | --- |
| [`handler.py`](template/handler.py) | Loads whisper once at import. `handler(event)` transcribes `audio_url`/`audio_base64`. `pod` mode runs it once on a sample, `serverless` mode hands it to the SDK. |
| [`start.sh`](template/start.sh) | `pod` → SSH + Jupyter + `sleep infinity`. `serverless` → `python handler.py`. |
| [`Dockerfile`](template/Dockerfile) | `ARG BASE_IMAGE` defaulting to the exact image behind `runpod-torch-v280` (`runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`) so torch/CUDA already match hosts. Installs the dependencies, copies the two scripts. |
| [`requirements.txt`](template/requirements.txt) | `runpod` + `faster-whisper` (torch comes from the base image — do not reinstall it). The Dockerfile installs them in **two steps** — see the cryptography known problem below. |

## Walkthrough — the repeatable loop

### 1. Provision a dev pod (interactive, from an official base)
Create a GPU pod on an official Runpod PyTorch template (or the base repository's
template), register an SSH key first, cost-guard it. Same shape as golden path
[06](../06-dev-pod.md)/[07](../07-network-volume-handoff.md):
```bash
runpodctl pod create --name whisper-dev-09 \
  --template-id runpod-torch-v280 --gpu-id "NVIDIA GeForce RTX 4090" \
  --data-center-ids EU-RO-1 --container-disk-in-gb 30 \
  --ssh --terminate-after 2026-07-10T23:30:00Z
  # heavy models -> add: --network-volume-id <vol-id> --volume-mount-path /workspace
runpodctl pod get <pod-id>        # poll until "ssh" block has an ip/port (see 06 bad-draw gotcha)
# once ready, read ip / port / key from `ssh info` into shell vars (SSH-over-TCP form, golden path 06);
# every ssh/scp below uses "$IP"/"$PORT"/"$KEY":
eval "$(runpodctl ssh info <pod-id> | python3 -c \
  'import sys,json; d=json.load(sys.stdin); print(f"IP={d[\"ip\"]} PORT={d[\"port\"]} KEY={d[\"ssh_key\"][\"path\"]}")')"
```
Verified (2026-07-10): pod `5dsx6eoxk02fod` (RTX 4090, EU-RO-1, $0.69/hr) came up with an
SSH endpoint within ~2 min. `runpod-torch-v280` resolves to the image
`runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`. Inside, `python3` was 3.12.3 and
`torch` `2.8.0+cu128` with `torch.cuda.is_available()` `True`.

### 2. Iterate the handler IN the pod (`python handler.py` loop)
SSH in, drop the template into `/app`, and run the pod-mode self-test until it
transcribes. This is the fast inner loop — **no image rebuild per change**:
```bash
# copy the four template files up to /app on the pod (scp uses -P for the port, ssh uses -p):
ssh -i "$KEY" -o StrictHostKeyChecking=no -p "$PORT" root@"$IP" 'mkdir -p /app'
scp -i "$KEY" -o StrictHostKeyChecking=no -P "$PORT" \
  template/handler.py template/start.sh template/Dockerfile template/requirements.txt \
  root@"$IP":/app/

# then install deps + run the pod-mode self-test over SSH (no image rebuild per change):
# faster-whisper installs clean; runpod needs two extra pip flags on this base (see below)
ssh -i "$KEY" -o StrictHostKeyChecking=no -p "$PORT" root@"$IP" 'cd /app && \
  pip install --break-system-packages faster-whisper && \
  pip install --break-system-packages --ignore-installed cryptography runpod && \
  python3 handler.py'         # MODE_TO_RUN defaults to "pod" → runs once on the JFK sample
```
Verified output on the pod (whisper `base`, cuda `float16`):
```text
------- BOOT -------
mode=pod model=base cache=/app/whisper-cache
device=cuda compute_type=float16
------- MODEL READY -------
RESULT: {'text': 'And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.', 'language': 'en', 'duration': 11.0}
```
Edit `handler.py`, run again, repeat. Put each necessary `pip install` / `apt-get install` into `requirements.txt` / the Dockerfile. That list is the whole deliverable of this step.

> **Live installation problems, now handled in the Dockerfile:** On `runpod/pytorch`, `pip install -r requirements.txt` fails in two ways.
> (1) PEP-668 marks pip "externally managed". Pass `--break-system-packages`.
> (2) `runpod` must have newer `cryptography` than the Debian-managed version.
>
> Pip refuses removal with `Cannot uninstall cryptography 41.0.7 … no RECORD file`.
> Install `runpod` with `--ignore-installed cryptography`. `faster-whisper` has no such conflict, so install it
> first, on its own.

### 3. Bake it into an image and build for amd64
Fold your recorded dependencies into the Dockerfile/requirements, then build **for the
right architecture** (Runpod hosts are x86_64) and push:
```bash
docker build --platform linux/amd64 -t <you>/whisper-dualmode:v1 template/ --push
```
Verified: built and pushed `<your-registry>/whisper-dualmode:v1`
(digest `sha256:e1f739029af2…`). The two-step Dockerfile pip installation added `cryptography-49.0.0` + `runpod-1.10.1` + `faster-whisper` without an uninstall conflict.
> Pin an explicit tag (`:v1`), never `:latest` (see [`../../../runpod-usage/reference/docker.md`](../../../runpod-usage/reference/docker.md)).
> Change `--build-arg BASE_IMAGE=...` for a different torch/CUDA version (matrix in the Dockerfile header).

### 4. Parity check — run `python handler.py` in *your* image on a clean `/app`
Before serverless, run the handler from the image you just built (still
`MODE_TO_RUN=pod`, clean `/app`, no live patches). This proves the **image** works, not
just your hand-patched pod — catching "forgot to add a dep to the Dockerfile" before it
becomes a serverless cold-start failure. Either redeploy a pod from the image, or run it
locally (the CMD is the pod-mode start script, so override it to run the self-test once):
```bash
docker run --rm --platform linux/amd64 <you>/whisper-dualmode:v1 python handler.py
```
Verified (local `docker run`, 2026-07-10): the built image transcribed the JFK sample on a
clean `/app` with the **identical text** the pod produced (here on CPU → `device=cpu
compute_type=int8`, since a laptop has no NVIDIA GPU, the transcription text is the same).

### 5. Flip to serverless — same image, one environment variable
`runpodctl serverless create` takes `--template-id` / `--hub-id`, not an image name (there is no `--image-name` flag). First, register a serverless template that points at the tag and carries `MODE_TO_RUN=serverless`. Then, create the scale-to-zero endpoint from that template:
```bash
# 1. serverless template with the image + the env that flips the mode (--env takes JSON)
runpodctl template create --name whisper-dualmode-sl --serverless \
  --image <you>/whisper-dualmode:v1 --container-disk-in-gb 15 \
  --env '{"MODE_TO_RUN":"serverless"}'                  # → template id, e.g. nnbpsuubpi
  # heavy models on a volume? also add MODEL_CACHE_DIR=/runpod-volume/whisper-cache here

# 2. endpoint from that template (gpu-id, not gpu-type; workers-min 0 = scale-to-zero)
runpodctl serverless create --name whisper-custom \
  --template-id <template-id> \
  --gpu-id "NVIDIA GeForce RTX 4090" \
  --workers-min 0 --workers-max 2 --idle-timeout 60
  # heavy models -> --network-volume-id <vol-id> (pins the DC; see the throttle gotcha)
```
Verified: the created endpoint reported `template.env` `{"MODE_TO_RUN":"serverless"}` — the
mode flip is baked into the template, so every worker serves instead of sleeping.

> **GPU-pool throttle hit live (do not pin the DC unless a volume forces you to):** the first
> attempt pinned `--data-center-ids EU-RO-1` even with no volume attached. `/health` showed
> `workers: {throttled: 1}` and the job sat `IN_QUEUE` for 4+ min — RTX 4090 was scarce in
> that one DC. Deleting and recreating **without** the DC pin (letting the scheduler pick any
> DC with a 4090) put a worker into `initializing` immediately. Only pin the DC when a
> network volume makes it necessary.

### 6. Verify with a real request — "up" ≠ "ready"
Send a **non-empty** input and poll (first call cold-starts, it can exceed `runsync`):
```bash
curl -s https://api.runpod.ai/v2/<endpoint-id>/run -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"input":{"audio_url":"https://github.com/openai/whisper/raw/main/tests/jfk.flac"}}'
# → {"id":"<job-id>","status":"IN_QUEUE"}   then poll /status/<job-id> until COMPLETED
```
Verified result (2026-07-10) — the first (cold) call returned `COMPLETED`, `delayTime`
~59.9 s (worker spin-up + image pull), `executionTime` 2.26 s (GPU transcription):
```json
{"status":"COMPLETED","delayTime":59877,"executionTime":2257,
 "output":{"text":"And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.",
           "language":"en","duration":11}}
```
**Parity confirmed:** The serverless worker and pod returned the **same words** from the same handler. One comma differs: "And so my …" versus "And so, my …". This is a float16 decoding difference, not a code/deployment gap. Same image, same `handler()`, same
result: the dual-mode invariant holds end to end.

## Heavy things → network volume (do not bake giant weights)
Small models (whisper `base` ≈ 140 MB) are fine baked in. For large weights (`large-v3`, LLMs, LoRA stacks), use a network volume instead of a larger image. Cache the weights there and point the handler at that volume. That is golden path
[07](../07-network-volume-handoff.md)'s handoff:
- Pod mounts the volume at **`/workspace`**. Serverless sees the **same** volume at
  **`/runpod-volume`** (the template's `MODEL_CACHE_DIR` already defaults to
  `/runpod-volume/...` when that path exists).
- Download once (on the pod, or the first worker), reuse across all workers — no
  re-download per cold start.

## Verify it works (all three passed live, 2026-07-10)
1. ✅ `python handler.py` on the pod printed a correct JFK transcription (`en`, 11.0 s).
2. ✅ The **built image** reproduced that in pod mode on a clean `/app` (step 4).
3. ✅ The serverless endpoint returned the **same** transcription for the same audio
   (step 6) — pod↔serverless parity, proven from outside via a real `/run`.
Green: #3 passed via a real `/run` from off-platform.

## Gotchas this path will hit
- **`runpodctl serverless create` has no image flag:** it takes `--template-id` /
  `--hub-id`, not an image name. Deploy your own image via a **serverless template**
  first (step 5). The GPU flag is `--gpu-id` (not `--gpu-type`).
- **`cryptography` will not uninstall on the `runpod/pytorch` base:** `pip install runpod`
  fails with `Cannot uninstall cryptography 41.0.7 … no RECORD file` because the base's
  copy is Debian-managed. Install `runpod` with `--ignore-installed cryptography`
  (and `--break-system-packages` for PEP-668). Baked into the Dockerfile's two-step install.
- **Scarce-GPU throttle from pinning one DC:** attaching `--data-center-ids <one DC>`
  with no volume can leave workers `throttled` and jobs stuck `IN_QUEUE`. Do not pin the DC
  unless a network volume forces it. Let the scheduler pick any DC with your GPU.
- **Arch mismatch:** build `--platform linux/amd64` or the worker dies with
  "exec format error" ([docker.md](../../../runpod-usage/reference/docker.md), the #1 deploy failure).
- **`:latest` is a trap:** pin explicit tags. Runpod caches images per host and will
  serve a stale `latest`.
- **Load the model at import, not per request** — the whole dual-mode invariant (and
  the cold-start rule) depends on it. Same as the flash "load once" rule.
- **Empty input:** the serverless SDK rejects an empty `{"input":{}}` — send real
  fields (`audio_url`/`audio_base64`). (Same bite as golden paths 07/08.)
- **`MODE_TO_RUN` default is `pod`** — if you forget to set it on the endpoint, the
  worker will start Jupyter and sleep instead of serving. Always set
  `--env MODE_TO_RUN=serverless`.
- **ctranslate2/CUDA:** `faster-whisper` bundles its own CUDA runtime. Keep it on an
  official `runpod/pytorch` base to avoid CUDA-version fights. If you see cuDNN/CUDA
  load errors, that is the base-image torch/CUDA not matching — pin via `BASE_IMAGE`.
- Diagnosis: if a serverless job times out but the worker looks healthy, pull worker logs with Runpod MCP `stream-worker-logs`. Do this before assuming a broken image. The cause is usually a handler/payload bug (lesson from [07](../07-network-volume-handoff.md)).
- **Volume DC pinning:** volume + pod + endpoint must share the data center.

## Cost & cleanup
```bash
runpodctl pod remove <pod-id>              # after you've built the image
runpodctl serverless delete <endpoint-id>  # scale-to-zero (~$0 idle) but delete when done
runpodctl template delete <template-id>    # the serverless template from step 5 (free, but tidy)
runpodctl network-volume delete <vol-id>   # if you created one (pod removed first)
runpodctl pod list && runpodctl serverless list && runpodctl network-volume list   # confirm clean
```
Pod cost guard: `--terminate-after` at creation (deletes it), not `--stop-after`. The pushed
Docker image (`<your-registry>/whisper-dualmode:v1`) is kept — endpoints reference it by tag.

## Relation to the other paths
- **03 (whisper)** is the *easy* whisper: a Hub worker or flash. **Start there.**
- **05 (model → endpoint)** is the docker→endpoint pipeline for a *fixed* model baked
  in. **09 adds the interactive pod dev loop and the dual-mode image** — the thing you
  want while the handler is still changing.
- **07 (volume handoff)** is how 09 serves heavy weights without a fat image.
- Provenance (optional, community repository): [justinwlin/Runpod-GPU-And-Serverless-Base](https://github.com/justinwlin/Runpod-GPU-And-Serverless-Base)
  — the fuller third-party version with more base-image tags and a Jupyter-first pod
  setup. The vendored `template/` here is self-contained. This repository is not needed to run the path.

## Skill facts confirmed / folded back (live run 2026-07-10)
- **`runpodctl serverless create` deploys a custom image via a template, not a flag.**
  Confirmed the two-step: `template create --serverless --image … --env '{JSON}'` then
  `serverless create --template-id …`. `--env` on `template create` takes a **JSON object**.
  `--gpu-id` (not `--gpu-type`). Matches
  [`endpoint-workflows.md`](../../../runpod-usage/reference/endpoint-workflows.md) /
  [`docker.md`](../../../runpod-usage/reference/docker.md).
- **`faster-whisper` can operate without extra CUDA libraries** on the `runpod-torch-v280` base
  (`runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`) — it ran on cuda `float16` out of the
  box. But for **`runpod` + `cryptography`**, use the `--ignore-installed cryptography`
  (+`--break-system-packages`) install — now recorded in `docker.md` and `gotchas.md`.
