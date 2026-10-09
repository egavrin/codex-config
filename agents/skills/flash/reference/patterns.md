# Flash — Common Patterns

## Choosing a model

Flash has no model catalog. Name a HuggingFace repository id in code. The worker downloads it at runtime (see Loading ML models below). Other sources: a custom image's `MODEL_NAME` env
(vLLM etc.), a URL, or your own weights on a NetworkVolume.

- **Start with the smallest model that proves the pipeline** (`gpt2`, `stabilityai/sd-turbo`, or a 0.5–1B variant). It provisions in seconds. Validate `@Endpoint` connections, dependencies, GPU, and I/O under `flash dev`. Then, change *only the id string* to the real model.
- **Match the model to GPU VRAM** (fp16 ≈ parameters × 2 bytes + overhead):

  | Model (fp16) | ~VRAM | `gpu=` |
  |---|---|---|
  | ≤3B / SD1.5 / sd-turbo | ≤8 GB | `GpuGroup.AMPERE_16` or `GpuGroup.ADA_24` |
  | 7–8B | ~16 GB | `GpuGroup.ADA_24` or `GpuGroup.AMPERE_24` |
  | 13B | ~28 GB | `GpuGroup.ADA_32_PRO` or `GpuGroup.AMPERE_48` |
  | 70B | ~140 GB | `GpuGroup.HOPPER_141` / `GpuGroup.BLACKWELL_180` (or quantize) |

- A ready-made hosted model with **no code** is [Runpod Public Endpoints / Hub](https://docs.runpod.io/hub) — a different product, not Flash.

> **Model size is not a flash limit.** A large HF repository streams its weights to the worker at runtime.
> A worker scaled to zero downloads them again on every cold start.
> For a large model used frequently, cache the weights to avoid repeated downloads.
>
> Persist them to a **NetworkVolume** (see *Loading ML models* below).
> On runpodctl/serverless, use the **HF model cache** (`--model-reference`) or include the weights in the image.
>
> [`runpodctl/reference/model-caching.md`](../../runpodctl/reference/model-caching.md) describes the same choice in its delivery-methods table.
> Streaming is simple.
>
> Reused weights give faster, less costly cold starts.

## Loading ML models (warm workers)

Model **weights are not part of the 1.5GB build artifact** — that cap is your code + pip
dependencies (torch is auto-excluded). Weights download on the worker at runtime (HuggingFace,
etc.), so **model size is not a Flash limit**. Two things make this fast and cheap:

- **Load once per worker, not per request.** Use a *class* `@Endpoint`. Its `__init__` loads the model into VRAM once at worker start. Methods process requests and reuse that model.
- Persist the cache on a NetworkVolume. A cold worker then reuses weights without another download at every cold start.

```python
from runpod_flash import Endpoint, GpuType, DataCenter, NetworkVolume

vol = NetworkVolume(name="model-cache", size=100, datacenter=DataCenter.US_GA_2)

@Endpoint(
    name="sd",
    gpu=GpuType.NVIDIA_GEFORCE_RTX_5090,
    workers=(0, 3),
    idle_timeout=300,                                # keep workers warm between calls
    datacenter=DataCenter.US_GA_2,
    volume=vol,
    env={"HF_HUB_CACHE": "/runpod-volume/models"},   # cache weights on the volume
    dependencies=["torch", "diffusers", "transformers", "accelerate"],
)
class SD:
    def __init__(self):                              # runs ONCE per worker
        import torch
        from diffusers import StableDiffusionPipeline
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16
        ).to("cuda")

    async def generate(self, prompt: str) -> dict:   # per request, reuses self.pipe
        image = self.pipe(prompt=prompt).images[0]
        image.save("/runpod-volume/out.png")         # /runpod-volume/ persists; elsewhere is wiped
        return {"saved": "/runpod-volume/out.png"}
```

- **Gated** models: pass `env={"HF_TOKEN": "..."}`.
- `workers=(1, n)` keeps one worker warm (no cold start on the first request). `(0, n)` scales to zero and cold-starts after `idle_timeout`.
- The class form is the cleanest way to load once. In function-form `@Endpoint` use a module-global cache for the same effect (see Known problem #11 in the skill). The class form is preferred for real inference.

## CPU + GPU Pipeline

```python
from runpod_flash import Endpoint, GpuGroup, CpuInstanceType

@Endpoint(name="preprocess", cpu=CpuInstanceType.CPU5C_4_8, workers=5, dependencies=["pandas"])
async def preprocess(raw):
    import pandas as pd
    return pd.DataFrame(raw).to_dict("records")

@Endpoint(name="infer", gpu=GpuGroup.AMPERE_80, workers=5, dependencies=["torch"])
async def infer(clean):
    import torch
    t = torch.tensor([[v for v in r.values()] for r in clean], device="cuda")
    return {"predictions": t.mean(dim=1).tolist()}

async def pipeline(data):
    return await infer(await preprocess(data))
```

## Parallel Execution

```python
import asyncio
results = await asyncio.gather(compute(a), compute(b), compute(c))
```
