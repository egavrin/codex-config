# Golden path 03 — Whisper endpoint (audio → text)

**Goal / Status: COVERED — live-verified 2026-07-07 / Kind: serverless / Lane: runpodctl+Hub or flash**

Deploy a serverless endpoint that, given an audio URL (or base64 audio), returns
the transcription. This is a **serverless** path — request/response, scale-to-zero
— not a pod. Two variants were both live-verified. This folder splits them so you
can jump straight to the one you want.

## Lane choice (why serverless, and why Hub is the default)

Whisper is a request/response inference API → **serverless** (invoked via
`/run`/`/runsync`, scales to zero between requests). See the shape decision in
[../../../runpod-usage/reference/development-loop.md](../../../runpod-usage/reference/development-loop.md)
and the serverless specialization in
[../../../runpod-usage/reference/endpoint-workflows.md](../../../runpod-usage/reference/endpoint-workflows.md).

The least-fragile way to stand up a *known* worker is the **Runpod Hub**. This walkthrough
uses **runpodctl** (`serverless create --hub-id …`). With the MCP server connected,
`deploy-hub-repo` does the same thing in one tool call. A ready Hub worker means no handler code, no
`docker build --platform=linux/amd64`, no registry auth, no cloudpickle/import
known problems — just `serverless create --hub-id …`. That is why **Variant A (Hub) is the
default**.

Rejected:
- **flash** suits custom or small handlers that change during development. For a heavy prebuilt model, it duplicates the faster-whisper handler that the Hub already supplies and maintains. More moving parts, no upside here. (Still fully
  covered as [Variant B](variant-b-flash.md) for when you *do* want to own the code.)
- **Custom image + endpoint** — most fragile (write handler → build amd64 → push →
  maybe registry auth → create endpoint). Only worth it if no good Hub worker exists.

## Which variant should I use?

| | [Variant A — Hub](variant-a-hub.md) | [Variant B — flash](variant-b-flash.md) |
| --- | --- | --- |
| Approach | Deploy a maintained Hub worker | Write your own faster-whisper handler |
| Effort | ~2 min, zero code | ~15 min, you own the handler |
| Customization | Take the worker's model + I/O schema | Own the model size, I/O schema, pre/post-processing |
| Image | Heavy prebuilt WhisperX image | Lighter/cheaper image you control |
| Iteration | None needed (prebuilt) | `flash dev` on a real remote GPU (hot-reload) |
| Pick when | A **heavy, prebuilt, known** model has a good Hub worker | **Custom/small** workload, or no good Hub worker fits |

For a big prebuilt model with a solid Hub worker, stay on the Hub. Flash would only implement the same behavior again. Use flash for a necessary custom model
size / I/O / a lighter image, or nothing on the Hub fits.

## Variants

- [Variant A — Runpod Hub worker](variant-a-hub.md) (recommended)
- [Variant B — from scratch with flash](variant-b-flash.md)

## Input & output schema (shared)

Both variants speak the Runpod job API. Body is always `{"input": { ... }}`.

> **Variant B condition:** a flash handler nests the value under its **parameter name**.
> See the raw-HTTP problem in [variant-b-flash.md](variant-b-flash.md).
> The schema below gives the plain Hub contract (Variant A).

Key input fields (WhisperX Hub worker, Variant A):

| Field | Type | Req | Notes |
| --- | --- | --- | --- |
| `audio_file` | string | yes | **HTTP(S) URL** to the audio, **or base64-encoded audio** (optionally a `data:audio/wav;base64,…` data-URI prefix). Both verified. |
| `language` | string | no | ISO code (`en`, `fr`, …), auto-detected if omitted |
| `align_output` | bool | no | word-level timestamps (default false) |
| `diarization` | bool | no | speaker labels. Supply `HF_TOKEN` env / `huggingface_access_token` |
| `batch_size` | int | no | default 64 |
| `initial_prompt`, `temperature`, `vad_onset`, `vad_offset`, `min_speakers`, `max_speakers` | — | no | see worker README |

**Output:** `{"output": {"detected_language": "en", "segments": [{"start","end","text", ...}]}}`.
The transcript is the concatenation of `segments[].text`.

**"Uploading" audio:** there is no file-upload step. Use either a public URL or base64. For a public URL, host the file there and pass the URL as `audio_file`. Otherwise, base64-encode the bytes and pass that string as `audio_file`. Base64 rides the job payload, so respect the limits:
`/run` ~10 MB, `/runsync` ~20 MB. For larger files, use a URL (presigned S3/GCS
works).

## Cross-cutting gotchas (shared)

- **Cold start versus the `runsync` 60 s window.** The first request after idle pulls the image and loads the model. This takes approximately 20–90 s on the Hub or 55–75 s on flash. Either can exceed the 60 s synchronous window. Use `/run` + poll `/status/<id>`
  for the first call, then `runsync` once warm. **Bound any poll loop.**

  More in
  [../../../runpod-usage/reference/gotchas.md](../../../runpod-usage/reference/gotchas.md)
  ("Cold starts and timeouts").
- **Broken Hub worker: `ready` but jobs never run.** `IN_QUEUE` jobs with `inProgress: 0` despite `ready` workers indicate a broken image or mis-dispatch. Workers can also be `throttled` on a scarce GPU pool. **Change workers instead of waiting.** Examine endpoint `/health` worker counts with `runpodctl serverless health <id>` (v2.9.0+). For worker logs, this account of the run specifies MCP `stream-worker-logs`, the v2 REST logs path, or the Console Workers tab.

  It states that runpodctl has no serverless worker-log command and REST v1 has no worker-log path (details in Variant A).
- **Delete returns 204, not JSON.** DELETE or MCP `delete-*` can report "Unexpected end of JSON input" after success. REST returns **204 No Content**, with no body to parse. Treat it as success. Make sure that deletion succeeded with a follow-up
  `get`/`list` (the resource should 404 / be absent).

## Cost & cleanup (shared)

`--workers-min 0` ⇒ **scale-to-zero**: no GPU billing while idle (you pay only per
request-second, plus the free scale-to-zero). This is the right cost posture for a
request/response API, so it is safe to leave an endpoint deployed. Delete test
resources when done:

```bash
runpodctl serverless delete <endpoint-id>
# flash apps can also be removed with: flash app delete <app-name>
```

See each variant file for the exact teardown command it used.
