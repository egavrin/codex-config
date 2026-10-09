---
name: flash
description: "Use runpod-flash for code-first serverless work. Write Python locally and run it on remote Runpod GPUs/CPUs with `flash dev` and hot-reload plus live worker logs. Then, deploy with `flash deploy`. Use for @Endpoint/@remote functions, resource configuration, and Flash deployment diagnosis. For infrastructure management through the CLI alone, use runpodctl or runpod-mcp."
metadata:
  user-invocable: true
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Runpod Flash

Write code locally. Use `flash dev` to run functions on remote Runpod GPUs/CPUs with hot-reload and live worker logs. Then, use `flash deploy` for deployment. `Endpoint` handles provisioning.

`runpod-flash` has independent releases. **`flash --help` and `flash <command> --help` define the command interface.** This skill explains concepts, decision rules, and problems that help output does not cover. Read the installed version with
`pip show runpod-flash` before concluding a subcommand or flag is unavailable.

**Worked examples first for anything multi-step.** Flash appears in verified end-to-end
paths — [03 variant B (whisper endpoint via flash)](../runpod/golden-paths/03-whisper-endpoint/variant-b-flash.md)
and [08 (fine-tune → serve)](../runpod/golden-paths/08-finetune-to-serverless.md). The full
index is [runpod/golden-paths/README.md](../runpod/golden-paths/README.md). Before a deployment plan, open the matching path. It gives the sequence and cost cleanup that this skill summarizes.

**Load on demand — this skill keeps the mental model + known problems inline. Details live in [`reference/`](reference/):**

| Need | Read |
|------|------|
| Install, auth, `flash init`, and the full `flash` command list | [reference/setup-and-cli.md](reference/setup-and-cli.md) |
| `Endpoint(...)` constructor parameters, `NetworkVolume`/`PodTemplate`/`EndpointJob`, GPU & CPU enum tables | [reference/api.md](reference/api.md) |
| Worked patterns — choosing a model, warm-worker model loading, CPU→GPU pipeline, parallel calls | [reference/patterns.md](reference/patterns.md) |

Quick start: `uv tool install runpod-flash` → `flash login` (or `export RUNPOD_API_KEY=...`) → `flash init my-project` → `flash dev`. Details in [reference/setup-and-cli.md](reference/setup-and-cli.md).

## Dev vs Deploy

- `flash dev` — **iterate.** Local server at `:8888`, but your decorated functions
  execute on **remote GPU/CPU workers**. Hot-reloads on save and **streams the worker's
  logs live** to the terminal. No build/upload/deploy wait — use this the whole time you
  develop.
- `flash deploy` — **ship.** Builds an artifact and deploys a stable endpoint. Slow
  (build + upload + provision). Only do this once the code works under `flash dev`.

`flash dev` ships **only the function body** to the worker, so a `NameError` for a
module-level name surfaces immediately here. `flash deploy` imports the whole module and
can mask that bug (see Known problem #1). Develop against `flash dev` and you catch it first.

## Autonomous Dev Loop

`flash dev` is a long-running server. Three rules:
- **Run it in the background** — do not block on it.
- **Capture its output** to a log file.
- **Drive it over HTTP.**

The captured log is the remote worker's live stream (cold start, model load, `print`s,
tracebacks) — read it to debug.

```bash
flash dev > /tmp/flash-dev.log 2>&1 &                          # background; never run it blocking
for i in $(seq 1 60); do grep -q "flash dev  localhost:" /tmp/flash-dev.log && break; sleep 2; done  # bounded ~2min; if it never appears, check the log for errors
URL=$(grep -o "localhost:[0-9]*" /tmp/flash-dev.log | head -1)               # actual port (8888 bumps if taken)
curl -s "$URL/main/predict" -d '{"data": {...}}'               # dispatches to the remote worker
```

- Read the actual URL from the log. Flash increases the port if 8888 is in use. It prints `✓ flash dev  localhost:<port>` and the route table.
- **Routes are namespaced by file**: `main.py`'s `/predict` is served at `/main/predict`.
- **Two route shapes, two body shapes** (mismatch → `422` naming the missing field in `loc`):
  - **Load-balanced** (`@api.post("/predict")`) → `POST /main/predict`, body is the arg
    at top level: a handler `def predict(data: dict)` wants `{"data": {...}}` (not the bare object).
  - **Queue-based** (bare `@Endpoint` decorator) → `POST /main/runsync` (the local dev
    server only generates `/runsync`, production also exposes `/run`),
    body is **double-wrapped** in `input`: a handler `def synthesize(data: dict)` wants
    `{"input": {"data": {...}}}`. The outer `input` is the queue envelope. The inner key is
    the handler's param name.
- Edit a handler and save — hot-reload re-syncs the body. Just re-send the request, no
  redeploy. Add `--auto-provision` to skip the first-call cold start. `kill %1` when done.

## Endpoint: Three Modes

Full constructor parameters and the GPU/CPU enum tables are in [reference/api.md](reference/api.md).

### Mode 1: Your Code (Queue-Based Decorator)

One function = one endpoint with its own workers.

```python
from runpod_flash import Endpoint, GpuGroup

@Endpoint(name="my-worker", gpu=GpuGroup.AMPERE_80, workers=5, dependencies=["torch"])
async def compute(data):
    import torch  # MUST import inside function (cloudpickle)
    return {"sum": torch.tensor(data, device="cuda").sum().item()}

result = await compute([1, 2, 3])
```

### Mode 2: Your Code (Load-Balanced Routes)

Multiple HTTP routes share one pool of workers.

```python
from runpod_flash import Endpoint, GpuGroup

api = Endpoint(name="my-api", gpu=GpuGroup.ADA_24, workers=(1, 5), dependencies=["torch"])

@api.post("/predict")
async def predict(data: list[float]):
    import torch
    return {"result": torch.tensor(data, device="cuda").sum().item()}

@api.get("/health")
async def health():
    return {"status": "ok"}
```

### Mode 3: External Image (Client)

Deploy a pre-built Docker image and call it via HTTP.

```python
from runpod_flash import Endpoint, GpuGroup, PodTemplate

server = Endpoint(
    name="my-server",
    image="my-org/my-image:latest",
    gpu=GpuGroup.AMPERE_80,
    workers=1,
    env={"HF_TOKEN": "xxx"},
    template=PodTemplate(containerDiskInGb=100),
)

# LB-style
result = await server.post("/v1/completions", {"prompt": "hello"})
models = await server.get("/v1/models")

# QB-style
job = await server.run({"prompt": "hello"})        # optional: webhook="https://..." for completion callback
await job.wait()
print(job.output)
```

Connect to an existing endpoint by ID (no provisioning):

```python
ep = Endpoint(id="abc123")
job = await ep.runsync({"prompt": "hello"})  # runsync wraps this as {"input": {"prompt": "hello"}}
print(job.output)
```

## How Mode Is Determined

| Parameters | Mode |
|-----------|------|
| `name=` only | Decorator (your code) |
| `image=` set | Client (deploys image, then HTTP calls) |
| `id=` set | Client (connects to existing, no provisioning) |

The table above is *how* the mode is picked from params. *When* to reach for `image=`:

### When to use `image=` (custom container) vs your own code

Default to writing Python (decorator / routes) — it runs arbitrary code with
`dependencies=[...]`/`system_dependencies=[...]` and can operate without a Dockerfile. Even large
HuggingFace models stay in decorator mode (weights stream at runtime — see
[reference/patterns.md → Loading ML models](reference/patterns.md#loading-ml-models-warm-workers)).
Use `image=` **only** for these requirements:

- **a pre-built inference server** — vLLM, TensorRT-LLM (`image="vllm/vllm-openai:latest"`, or `runpod/worker-vllm`, `runpod/worker-comfy`)
- **system-level dependencies not pip-installable** — a specific CUDA/cuDNN, OS libraries
- **models baked into the image** — to skip the runtime download entirely
- **an existing Runpod Serverless worker** — you already have a working image

Trade-off: `image=` mode **cannot run arbitrary Python** (the image owns all logic) and the
image must implement a Runpod Serverless handler. Full list + examples:
https://docs.runpod.io/flash/custom-docker-images

## Gotchas

1. **Only the function body ships to the worker** -- most common error. Put imports *and* any module-level constants/helpers the function uses *inside* the decorated body. `flash deploy` imports the whole module so module globals happen to work. `flash dev` ships just the body, so a module-level name raises `NameError`. A handler that works deployed can break under dev — fix it by moving everything inside.
2. **Forgetting await** -- use `await` with all decorated functions and client methods.
3. **Missing dependencies** -- must list in `dependencies=[]`.
4. **gpu/cpu are exclusive** -- pick one per Endpoint.
5. **idle_timeout is seconds** -- default 60s, not minutes.
6. **10MB payload limit** -- pass URLs, not large objects. Return binary audio/images/files as base64 in JSON (`{"audio_b64": ...}`). Decode it on the client. For larger outputs, write to a NetworkVolume or upload to storage. Return a URL.
7. **Client vs decorator** -- `image=`/`id=` = client. Otherwise = decorator.
8. For auto GPU switching, set workers >= 5. Pass a list of GPU types (for example `gpu=[GpuGroup.ADA_24, GpuGroup.AMPERE_80]`). Set `workers=5` or higher. The platform only auto-switches GPU types based on supply when max workers is at least 5.
9. **`runsync` timeout is 60s** -- cold starts can exceed 60s. Use `ep.runsync(data, timeout=120)` for first requests or use `ep.run()` + `job.wait()` instead.
10. **Request body shape (raw/external HTTP callers only)** -- match the request shape to the endpoint type:
    - **LB routes** (`@api.post(...)`): send the handler arg at the top level — `{"data": {...}}`.
    - QB endpoints (bare `@Endpoint`, hit via `.../run` or `.../runsync`): the worker calls `handler(**job_input)`. The request's `input` keys must match the handler's parameter names. `def transcribe(input_data: dict)` wants `{"input": {"input_data": {...}}}`. `def read(input: dict)` wants `{"input": {"input": {...}}}`. A mismatch fails with
      `got an unexpected keyword argument …`. Use `**kwargs` if the handler ignores the payload.
        - **Never send an empty `input`.** The worker SDK rejects `{"input": {}}` with `Job has missing field(s): id or input`. Always include at least one key.
    - *Context:* the flash client (`ep.runsync(x)`, `api.post(...)`) hides the spreading, so this
      only bites raw HTTP/external callers (mismatch behavior verified 2026-07-10 via worker logs).
      See *Autonomous Dev Loop*.
11. Load a model once per worker, not per call. For real inference, use a class `@Endpoint` whose `__init__` loads the model once per worker. See [reference/patterns.md → Loading ML models](reference/patterns.md#loading-ml-models-warm-workers). In function-form, follow #1 with a module-global cache inside the body. This works under both `flash dev` and `deploy`:
    ```python
    global _MODEL
    try: _MODEL
    except NameError: _MODEL = load_model()   # runs once per worker, reused across calls
    ```
12. Put native CUDA libraries in `dependencies=[]` too. For example, CTranslate2/faster-whisper must have `nvidia-cublas-cu12` and `nvidia-cudnn-cu12`. Otherwise, it silently selects CPU. Add them alongside the Python package.
13. **Silent 401 auth failure** -- a set `RUNPOD_API_KEY` environment variable overrides the `flash login` token, so a bad/expired key wins. The failure is quiet: provisioning logs `GraphQL request failed: 401`, but `flash dev` still prints its normal ready line ("failed endpoints deploy on-demand"), so it *looks* healthy. When endpoints fail to provision:
    1. Examine the provisioning log for `GraphQL request failed: 401`.
    2. Test the current key independently: `curl -s -o /dev/null -w '%{http_code}' https://rest.runpod.io/v1/endpoints -H "Authorization: Bearer $RUNPOD_API_KEY"` (200 = good, 401 = bad).
    3. Fix it: `unset RUNPOD_API_KEY` to fall back to the `flash login` token, or `export` a valid key.
14. **`system_dependencies=` adds to cold start.** Apt packages (for example `["ffmpeg", "espeak-ng"]`) install on the worker before first use. The initial call is slower, in addition to any model download. Warm calls are unaffected.
15. Delete a deployed app with `flash app delete <app>`. `flash undeploy list` can show "no endpoints" for an active app. `flash app delete` (or `runpodctl serverless delete <id>`) reliably removes it.

## Resources

- Setup & CLI: [reference/setup-and-cli.md](reference/setup-and-cli.md) · API & compute enums: [reference/api.md](reference/api.md) · Patterns: [reference/patterns.md](reference/patterns.md)
- Flash source: https://github.com/runpod/flash
- Runnable examples: https://github.com/runpod/flash-examples — clone and adapt the closest one
- Package (PyPI): https://pypi.org/project/runpod-flash/
- Documentation: https://docs.runpod.io/flash/overview
  - Custom Docker images (when + how): https://docs.runpod.io/flash/custom-docker-images
  - Storage / network volumes: https://docs.runpod.io/flash/configuration/storage

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
