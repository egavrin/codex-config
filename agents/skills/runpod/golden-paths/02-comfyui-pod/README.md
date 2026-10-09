# Golden path 02 — ComfyUI server on a pod + access URL

**Goal / Status: COVERED — live-verified 2026-07-07 / Kind: pod, server / Lane: runpodctl**

For "run ComfyUI on Runpod and give me the URL", provision a GPU pod and start ComfyUI. Return a proxy URL that loads the web UI. A checkpoint and the default text-to-image workflow must be usable. This is the same shape
as `../01-ollama-pod.md`. It follows the pod development loop in
[`../../../runpod-usage/reference/pod-workflows.md`](../../../runpod-usage/reference/pod-workflows.md).

There are two ways to get there, split into their own files below.

If the Pod already runs and an imported workflow lacks model download metadata, use the [ComfyUI model-repair guide](../../../runpod-templates/reference/comfyui-model-repair.md). This golden path still owns Pod provisioning. This post-launch recovery extension was not part of
the 2026-07-07 live verification, so feature-detect the live image and its routes.

## Which variant should I use?

| | Variant A — from scratch | Variant B — prebuilt official image |
| --- | --- | --- |
| **What you deploy** | Official PyTorch template. You `git clone` + install ComfyUI | Runpod's official prebuilt ComfyUI image (auto-starts) |
| **Steps** | create → SSH install → detached start → poll | create → poll (no SSH/install/run step) |
| **First-boot wait** | ~30–60s of proxy 502s after you start it | ~4 min of proxy 502s (copies ComfyUI to the volume on first boot) |
| **Control** | Full — pick versions, custom nodes, a lighter footprint | What ships (ComfyUI 0.26.2, torch 2.10.0+cu128, ComfyUI-Manager, FileBrowser, JupyterLab) |
| **Known problems you must handle** | PEP 668 `--break-system-packages`, `setsid` detach, bind `0.0.0.0` | Larger image (150 GB container disk), only the checkpoint uses SSH |
| **Pick when** | Custom/lighter behavior or specific versions/nodes are necessary | You just want ComfyUI up reliably with the least effort — **default** |

**Default recommendation: Variant B (prefer prebuilt).** Per the development loop,
[prefer a prebuilt/known option before building from scratch](../../../runpod-usage/reference/development-loop.md#2-prefer-a-prebuilt--known-option-before-building-from-scratch)
— it auto-starts and skips the install gotchas. Reach for Variant A only when no
prebuilt fits (custom nodes, a lighter image, or pinned versions).

## Variants

- [Variant A — from scratch](variant-a-from-scratch.md) — install ComfyUI yourself on a PyTorch template.
- [Variant B — prebuilt official image](variant-b-prebuilt.md) — deploy `runpod/comfyui`, which auto-starts.

## Acceptance criteria (shared)

Both variants must satisfy the same delivery bar:

1. **Auth** resolved (`export RUNPOD_API_KEY=...`).
2. GPU pod, GPU with **≥16 GB VRAM** (RTX 4090 is ideal), **port `8188/http`
   exposed at creation**, SSH enabled, on a **network volume**, with a
   `--terminate-after` cost guard.
3. ComfyUI running, **bound to `0.0.0.0`** on port `8188`.
4. Poll the proxy URL until the UI answers (expect proxy 502s during boot). Use the per-variant timings. Escalate on any manual step. Do not repeat waits indefinitely or report false progress.
5. **Secondary:** an ungated checkpoint is available so the default graph works.
   Ideally a generation is confirmed via the API.
6. Returns `https://<pod-id>-8188.proxy.runpod.net`.

## Cross-cutting gotchas (shared)

These bite both variants (details and the fix per variant are in each file):

- **PEP 668 / template torch (Variant A).** Official PyTorch templates are now
  Ubuntu 24.04 / py3.12 (externally-managed) with torch in the **system** Python.
  A bare `pip install` errors without `--break-system-packages`, and a fresh
  `uv venv` will not inherit torch — install into the existing interpreter. See
  [`../../../runpod-usage/reference/on-pod-setup.md`](../../../runpod-usage/reference/on-pod-setup.md).
- **Detach the server / `setsid` (Variant A).** A plain `&` dies on SSH
  disconnect (SIGHUP). Start with `setsid … < /dev/null &`, return immediately,
  and poll in a **separate** SSH call (do not `sleep` in the same invocation).
- **"Running" ≠ ready.** A pod showing "Running" does not mean ComfyUI serves.
  Always test from **outside** through the proxy and expect a warm-up window of
  502s — that is normal, keep polling. See the loop's
  [verify step](../../../runpod-usage/reference/development-loop.md#6-verify-with-a-real-request--up--ready).
- **Bind `0.0.0.0`.** localhost/`127.0.0.1` → the proxy cannot reach it → 502.
  Variant B already passes `--listen 0.0.0.0`. Variant A must set it.
- **Network-volume DC lock.** A network volume belongs to one data center. Create the pod in that **same DC**. This limits GPU availability.
  First, make sure that your GPU exists in the volume's DC
  ([`../../../runpod-usage/reference/storage.md`](../../../runpod-usage/reference/storage.md),
  [`gotchas.md`](../../../runpod-usage/reference/gotchas.md)).
- **Ports at creation. URL is public + unauth.** Reset a running pod before you add ports. Anyone with the proxy URL can access it ([`../../../runpod-usage/reference/networking.md`](../../../runpod-usage/reference/networking.md)).

## Cost & cleanup (shared)

- **Cost guard at creation:** `--terminate-after <iso8601 a few hours out>`
  *deletes* the pod at that time. Prefer it over `--stop-after`, which only
  *stops* the pod so you keep paying for disk/volume.
- **Remove temporary resources after work.** First, run `runpodctl pod remove <pod-id>`. If the network volume exists only for this test, run `runpodctl network-volume delete <volume-id>` afterward. The pod must be removed first.
- Data on the network volume persists across stop/restart and survives pod
  removal (only volume deletion clears it).
- Reference RTX 4090 pricing seen during verification: **$0.69/hr** (Variant B
  pod `7ydkt5vs4fst25`). GPU/DC pricing varies — examine `runpodctl gpu list`.
