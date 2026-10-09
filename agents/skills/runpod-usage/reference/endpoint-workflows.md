# The serverless endpoint loop

The serverless specialization of the development loop (`development-loop.md`) — for
a **request/response API that scales to zero** (transcription, inference). Unlike a
pod there is no SSH, no exposed ports, no proxy: you deploy a worker and invoke it
over the Runpod job API. Proven on the Whisper golden path (both variants).

## 1. Pick the source (in order of preference)

1. **Hub worker (fastest, least fragile)** — a maintained prebuilt worker.
   `runpodctl hub search <app>` → deploy with runpodctl (Hub is runpodctl-only).
   Best when a good worker supplies the necessary behavior.
2. **flash (from scratch, custom/light)** — write an `@Endpoint` handler and
   `flash deploy`. Best for a necessary custom model size / I/O schema / a lighter
   image, or no good Hub worker exists.
3. **Custom image + endpoint (last resort)** — write a handler, `docker build
   --platform=linux/amd64`, push (private image → registry auth), create the
   endpoint (runpodctl/MCP). Only when neither of the above fits.

## 2. Deploy (scale-to-zero)

```bash
# Hub
runpodctl serverless create --hub-id <id> --name <name> --workers-min 0 --workers-max 3
# flash
flash deploy                                  # @Endpoint(workers=(0,3)) in the code
# Custom image — TWO steps: serverless create takes --template-id/--hub-id, NOT an image.
runpodctl template create --name <tpl> --serverless \
  --image <you>/<img>:<tag> --container-disk-in-gb 15 \
  --env '{"KEY":"VALUE"}'                      # --env is a JSON object here; → template id
runpodctl serverless create --template-id <template-id> --name <name> \
  --gpu-id "NVIDIA GeForce RTX 4090" --workers-min 0 --workers-max 2   # --gpu-id, not --gpu-type
```

`--workers-min 0` = no GPU billing while idle (pay only per request-second). Unless a network volume makes it necessary, do not pin `--data-center-ids` for a custom-image endpoint. A single-DC pin on a scarce GPU leaves workers `throttled` and jobs `IN_QUEUE`. Live evidence from 2026-07-10: EU-RO-1 4090 pin → `throttled:1`. Without the pin, scheduling was immediate.

### Picking a Hub worker (this decides success)

Prefer an actively maintained worker on a broad GPU pool with high availability. Do not pin a scarce large tier unnecessary for a small model. If workers become `ready` but jobs stay `IN_QUEUE` with `inProgress: 0`, the image or its dispatch fails. **Switch workers after you find the cause.**

Use `runpodctl serverless health <id>` for counts (v2.9.0+). Use `runpodctl serverless logs <id> --source system` for the cause (v2.10.0+). Repeated `start container` events without `container` output indicate a crash loop, not a capacity problem.

MCP `stream-worker-logs` reads
the same logs.

## 3. Invoke

The raw protocol is below because it is what you hand a user for copy-paste, and what a
non-Runpod client speaks. For direct operation, `runpodctl serverless run <id> --input '{...}'` (v2.9.0+) submits the job and polls its status. It supplies authentication, local payload validation, and a bounded wait. The MCP route supplies typed job tools.

```bash
# warm / small payloads (sync, 60s window):
curl -s https://api.runpod.ai/v2/<endpoint-id>/runsync \
  -H "Authorization: Bearer $RUNPOD_API_KEY" -H "Content-Type: application/json" \
  -d '{"input": { ... }}'

# first / cold call — async, then poll:
curl -s https://api.runpod.ai/v2/<endpoint-id>/run  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" -d '{"input": { ... }}'
curl -s https://api.runpod.ai/v2/<endpoint-id>/status/<job-id> -H "Authorization: Bearer $RUNPOD_API_KEY"
```

- Body is always `{"input": {...}}`. **flash quirk:** a flash handler nests the
  value under its parameter name → `{"input": {"<param>": {...}}}` (name the param
  `input` to get the plain contract).
- Large inputs: pass a **URL**, not bytes (payload limits `/run` ~10MB, `/runsync`
  ~20MB). Base64 rides the payload for small files.
- **Streaming** (`/stream/<job-id>`):
  - Works **only when the handler is a generator** (`yield`s instead of `return`s).
    - Submit with `/run`. Then, call GET `/stream/<job-id>` repeatedly. Each call removes buffered chunks since the previous call and returns `{"status", "stream":[{"output": <yield>}]}`.
  - Stop when `status` is `COMPLETED`.
  - Add `"return_aggregate_stream": True` to `runpod.serverless.start(...)` to *also*
    expose the full list via `/run`/`/runsync`/`/status` (single chunk caps at 1MB).
  - Worked example: golden path 12 (serverless streaming).

## 4. Verify with a real request — "ready" ≠ working

The first call starts a cold worker (image pull and model load), often beyond `runsync`'s 60s. For that request, use `/run` and poll `/status/<id>`. Once warm, use `runsync`. Only report success once a real input returns the right
output. Bound any poll loop.

## 5. Deliver & tear down

Give the user the endpoint id + a copy-paste `curl` and the input schema (how to
pass a URL and/or base64). Scale-to-zero means it is safe to leave. Delete with
`runpodctl serverless delete <id>` (or `flash app delete <app>`).

See [`golden-paths/03-whisper-endpoint/`](../../runpod/golden-paths/03-whisper-endpoint/README.md)
for a fully worked example of both the Hub and flash variants (a README plus one
file per variant).
