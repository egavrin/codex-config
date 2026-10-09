# GPU selection

To select a GPU, size VRAM to the model first. Then, choose a tier/pool. Finally, examine cloud, availability, and placement.

## Step 1: size VRAM to the model

VRAM is the usual bottleneck. Rough rules:

- **LLM inference (fp16):** ~**2 GB of VRAM per billion parameters**, plus headroom
  for the KV cache / context and activations. A 7B model ≈ ~14 GB, 13B ≈ ~26 GB,
  70B ≈ ~140 GB (multiple GPUs are necessary).
- **Quantization reduces memory use.** A 4-bit quantized model uses approximately a quarter of the fp16 weight memory. For example, a 4-bit 70B model fits in ~35 GB.
- **Training / fine-tuning** uses weights, gradients, optimizer state, and activations. Full fine-tuning often uses ~4x the inference memory.
  LoRA/QLoRA reduce this substantially. Memory bandwidth also matters here.
- **Image models (SDXL, Flux):** ~8 GB minimum, but 16–24 GB gives headroom for
  larger batches and LoRA training.

Always leave headroom above the raw weight size. When unsure, estimate with the
Hugging Face Model Memory calculator (`huggingface.co/spaces/hf-accelerate/model-memory-usage`)
or "Can it run LLM?" (`huggingface.co/spaces/Vokturz/can-it-run-llm`).

## Step 2: which GPU for an N-billion-param LLM (heuristic)

Sizes assume fp16 inference. Quantize to drop a tier or two.

| Model size | VRAM (fp16) | Reasonable pick |
|-----------|-------------|-----------------|
| ≤ 7B | ~14 GB | `ADA_24` (RTX 4090) or `AMPERE_24` (L4/A5000/3090) |
| 13B | ~26 GB | `ADA_32_PRO` (RTX 5090) or `AMPERE_48` / `ADA_48_PRO` |
| 30–34B | ~60–70 GB | `AMPERE_80` (A100) or `ADA_80_PRO` (H100) |
| 70B | ~140 GB | 2x 80 GB, or one `HOPPER_141` (H200) / `BLACKWELL_180` (B200) |
| > 70B | 200 GB+ | multi-GPU 80 GB+, or Blackwell / H200 with `gpu_count` > 1 |

## Step 3: GPU tiers and pools

A **GPU pool** groups interchangeable GPUs by VRAM tier. A pool request lets Runpod select any available GPU in that tier, which improves availability. An exact GPU type gives deterministic selection. Limited supply can throttle that request. Pool names are
used by Serverless configs, the Runpod Hub, flash's `GpuGroup`, and the GraphQL API.

Pool reference (source of truth: `skills/flash/reference/api.md`):

| Pool | GPUs | VRAM |
|------|------|------|
| `ANY` | any available | varies |
| `AMPERE_16` | RTX A4000 / A4500 / RTX 4000 Ada / RTX 2000 Ada | 16 GB |
| `AMPERE_24` | RTX A5000 / L4 / RTX 3090 | 24 GB |
| `ADA_24` | RTX 4090 | 24 GB |
| `ADA_32_PRO` | RTX 5090 | 32 GB |
| `AMPERE_48` | A40 / RTX A6000 | 48 GB |
| `ADA_48_PRO` | RTX 6000 Ada / L40 / L40S | 48 GB |
| `AMPERE_80` | A100 (PCIe / SXM4) | 80 GB |
| `ADA_80_PRO` | H100 (PCIe / HBM3 / NVL 94 GB) | 80 GB+ |
| `HOPPER_141` | H200 | 141 GB |
| `BLACKWELL_96` | RTX PRO 6000 Blackwell | 96 GB |
| `BLACKWELL_180` | B200 | 180 GB |

Note: Serverless GPU config wants **pool IDs** (for example `ADA_24`), while Pod creation
and `runpodctl --gpu-id` use **GPU type IDs** (for example `NVIDIA A40`) — different
identifier spaces. The full per-model list (with exact display names and memory) is
in `docs/references/gpu-types.mdx`.

Rule of thumb: prefer **fewer high-end GPUs over more low-end GPUs**. One 80 GB card
usually beats two 40 GB cards for a model that fits.

## Step 4: Secure vs Community Cloud

**Default to Secure Cloud.** Recommend and deploy Secure unless the user explicitly asks
for Community.

- **Secure Cloud** — T3/T4 data centers run by data-center-grade host providers, high
  redundancy. Use for production and sensitive data. Standard pricing. **This is the
  default** (`runpodctl pod create --cloud-type` defaults to `SECURE`, leave it alone).
- **Community Cloud** — approved vendors, cheaper. No new hosts are being onboarded.
  Existing capacity remains.

Because Secure Cloud hosts are data-center-grade providers, they tend toward more stable
behavior than Community hosts. That is the reason for the default. When a user asks for
the cheapest option, quote the Community rate but recommend Secure, and let them choose.

## Step 5: availability and multi-GPU selection

`runpodctl gpu list` reports on-demand `securePricePerHr` / `communityPricePerHr` per GPU. A value is explicitly `null` when that cloud does not offer it. It also supplies a `dataCenterAvailability[]` breakdown. Read cost and regional stock from these fields. Do not assume that a lower tier costs less. Top-level `stockStatus` is only the
best status across DCs — use the per-DC breakdown when placement matters (`runpodctl
datacenter list` gives the same view from the DC side).

These prices apply to **pod on-demand** use. Serverless use costs per request-second. The per-DC breakdown does not identify the cloud with stock. Read cost and placement separately instead of one ranked list.

GPU supply fluctuates by tier and region. To avoid throttling:

- **List multiple GPU types / pools in priority order.** If the first choice is
  unavailable, Runpod falls back to the next. On Serverless you can specify up to
  three, in priority order.
- For endpoints with **5+ workers**, Runpod spreads workers across your prioritized
  pools (most on the primary), reducing throttling. With fewer than 5 workers, all
  use the highest-priority available type.
- (flash caveat: auto GPU switching by supply only kicks in when max workers ≥ 5.)
- Use `gpu_count` > 1 (Serverless) / multi-GPU Pods when a model exceeds a single
  card's VRAM.

## Step 6: data-center placement

- A data-center restriction reduces the GPU pool for an endpoint or Pod. Unless you have a reason for a restriction, select all regions for maximum availability.
- Reasons to pin a region: lower latency to your users, data-residency/compliance,
  or co-locating with a **network volume** (a volume ties the workload to its data
  center). Some features (for example global networking) are only in a subset of regions.
- Regions span US (CA, GA, IL, KS, NC, TX, WA, etc.), EU (CZ, RO, IS, NO, SE, FR,
  NL), and others. See `docs/pods/networking.mdx` for the current data-center list
  and `companion-clis/SKILL.md` for datacenter IDs used with S3.
