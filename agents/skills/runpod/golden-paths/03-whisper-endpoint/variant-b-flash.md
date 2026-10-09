# Golden path 03 — Whisper — Variant B: from scratch with flash

**Status:** COVERED — live-verified 2026-07-07. **Lane:** flash (code-first serverless). **Use this variant** for a custom or lighter worker with your own model size, I/O schema, or pre/post-processing. Also use it when no suitable Hub worker exists. You write and own a faster-whisper
handler, iterate on a real GPU with `flash dev`, then `flash deploy`. For a heavy
prebuilt model with a solid Hub worker, prefer
[Variant A — Hub](variant-a-hub.md) (flash would just be re-implementing it).

Shared schema, known problems, and cost notes live in the [folder README](README.md). The
flash skill is at [../../../flash/SKILL.md](../../../flash/SKILL.md).

## Prerequisites

- Python 3.10–3.13 and the flash CLI:
  ```bash
  uv tool install runpod-flash          # or: pip install runpod-flash
  ```
- A Runpod API key exported for non-interactive use:
  ```bash
  export RUNPOD_API_KEY=...             # https://console.runpod.io/user/settings
  ```

## Walkthrough

1. **Declare dependencies and GPU IN the decorator, NOT pyproject.toml.** Flash sends only the function body to the worker. Put imports and the model cache inside that body. Declare pip dependencies and GPU tier on `@Endpoint`.
   ```python
   # whisper_worker.py  — deps + GPU declared in the decorator (NOT pyproject.toml)
   from runpod_flash import Endpoint, GpuGroup

   @Endpoint(
       name="whisper-flash",
       gpu=GpuGroup.AMPERE_16,                 # whisper base needs <2GB; broad supply
       workers=(0, 3), idle_timeout=60,        # scale-to-zero
       dependencies=["faster-whisper",
                     "nvidia-cublas-cu12", "nvidia-cudnn-cu12"],  # CTranslate2 GPU libs
   )
   async def transcribe(input_data: dict) -> dict:
       import base64, tempfile, urllib.request
       from faster_whisper import WhisperModel
       global _MODEL                            # load once per worker (see flash gotcha 11)
       try: _MODEL
       except NameError: _MODEL = WhisperModel("base", device="cuda", compute_type="float16")
       # download input_data["audio_url"] (or decode audio_base64) -> temp file -> transcribe
   ```
   Two rules from [../../../flash/SKILL.md](../../../flash/SKILL.md) are necessary here. Put **native CUDA libraries in `dependencies=[]`**: `nvidia-cublas-cu12` + `nvidia-cudnn-cu12`. Otherwise, CTranslate2/faster-whisper silently uses CPU (known problem 12). **Load the model once per worker** through a module-level `global _MODEL` cache inside the body. This supports both `flash dev` and `flash deploy` (known problems 1 + 11).

2. **Scaffold a project** (outside your git repositories):
   ```bash
   flash init ~/whisper-flash            # scaffold (writes AGENTS.md + CLAUDE.md)
   ```

3. Change the code on a real remote GPU with hot-reload. This costs little and tests the payload shape before delivery:
   ```bash
   flash dev                             # runs the function on a remote GPU, streams live worker logs
   ```

4. **Deploy it** — builds an artifact and deploys a stable endpoint:
   ```bash
   flash deploy                          # returns an endpoint id
   ```

## Verify it works

Call it through the Runpod job API. **Nest the payload under the handler parameter name.** For `input_data`, the body is `{"input":{"input_data":{...}}}`, not plain `{"input":{...}}` (see the known problem below):

```bash
curl -s https://api.runpod.ai/v2/<endpoint-id>/runsync \
  -H "Authorization: Bearer $RUNPOD_API_KEY" -H "Content-Type: application/json" \
  -d '{"input":{"input_data":{"audio_url":"https://github.com/runpod-workers/sample-inputs/raw/main/audio/gettysburg.wav"}}}'
```

Verified: cold ~55–75 s (image pull + model download), **warm <1 s**. Returns
`{text, language, ...}` with the correct Gettysburg transcript ("Four score and
seven years ago…"). The first cold call can exceed the `runsync` 60 s limit. Use `/run` with `/status/<id>` polling, or flash client `ep.runsync(data, timeout=120)`. Once warm, use `runsync`.

## Variant-specific gotchas

- **Raw-HTTP callers nest under the parameter name** (flash known problem 10). When
  something other than the flash client hits the deployed endpoint
  (`curl .../runsync`, another service), the wire body is
  `{"input": {"<handler_param_name>": <value>}}`. A handler
  `async def transcribe(input_data: dict)` therefore expects
  `{"input":{"input_data":{...}}}`. **Name the parameter `input`** if you want the
  plain Runpod contract (matching Variant A's schema). The flash client's
  `ep.runsync(x)` hides this — it is only a known problem for external callers.
- **Only the function body ships to the worker** (flash known problem 1). Put imports and
  any module-level constants/helpers *inside* the decorated body, or `flash dev`
  raises `NameError` (and `flash deploy` can mask it). This is why the model cache
  is written as an in-body `global _MODEL` (known problem 11).
- List native CUDA libraries in `dependencies=[]` (flash known problem 12). Include `nvidia-cublas-cu12` and `nvidia-cudnn-cu12` with `faster-whisper`. Otherwise, it silently runs on CPU.
- **`runsync` is 60 s, and payload limit is 10 MB** (flash known problems 9 + 6). For large audio, pass a URL instead of bytes. For cold starts, use `/run` with polling.

## Cost & cleanup (link back to README for shared)

Scale-to-zero (`workers=(0, 3)` in the decorator) means ~$0 while idle. Teardown:

```bash
flash app delete whisper-flash          # reliable even if `flash undeploy list` shows "no endpoints"
# or: runpodctl serverless delete <endpoint-id>
```

Full shared cost/cleanup and the 204-on-delete note are in the
[folder README](README.md#cost--cleanup-shared).
