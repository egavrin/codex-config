# Common gotchas

Cross-cutting mistakes that bite people deploying on Runpod, as
symptom → cause → fix. See `docker.md` and `storage.md` for the full mechanics.

## Image built for the wrong CPU architecture

- **Symptom:** worker/pod fails to start, "exec format error", or the container
  never comes up — often only after building on an Apple Silicon / ARM machine.
- **Cause:** the image was built for arm64. Runpod hosts are x86_64.
- **Fix:** rebuild with `docker build --platform=linux/amd64 ...` and re-push.
  This is the #1 deploy failure.

## Using the `latest` tag

- **Symptom:** you push new code but workers keep running old behavior. You cannot
  tell which version is live.
- **Cause:** `latest` is mutable and Runpod caches images per host, so workers
  serve a stale cached `latest`.
- **Fix:** use explicit tags (`v1.0.0`, `v1.0.1`) or pin the digest
  (`name:tag@sha256:...`). Bump the tag on every change.

## Private image will not pull

- **Symptom:** endpoint/pod stuck initializing. Logs show an image pull /
  authentication error.
- **Cause:** the image is private and Runpod has no registry credentials.
- **Fix:** add container-registry credentials in Console → Settings → Container
  Registry, then select them on the template/endpoint. Runpod uses
  `docker login`-style creds. Headless equivalent: MCP
  `create-container-registry-auth`, then pass the id as `containerRegistryAuthId`
  on create-pod/create-endpoint.
- **AWS ECR correction:** register the repository instead of stored credentials. MCP `create-registry-delegation` gives Runpod scoped pull access to an ECR repository ARN. See that tool's parameter descriptions for the specifics.

## Image builds, then inference crashes with "Numpy is not available"

- **Symptom:** the image builds fine and the worker **starts**, but the first job
  fails at inference with `RuntimeError: Numpy is not available` (often preceded at
  import by `UserWarning: Failed to initialize NumPy: _ARRAY_API not found`).
- **Cause:** a NumPy 2.x / older-torch ABI mismatch. `pip install torch==2.2.2` installs the latest `numpy` (2.x) by default. That torch wheel uses NumPy 1.x and cannot use 2.x. Any `.numpy()` call during inference then throws an exception.
- **Fix:** pin `numpy<2` in `requirements.txt` (or upgrade torch to a numpy-2-aware
  build). Before deployment, run the container locally with a `test_input.json` (`docker.md` "Test the container locally"). The import warning indicates the problem early. The crash occurs during an actual job, not startup.

## `pip install runpod` fails on a `runpod/pytorch` base ("Cannot uninstall cryptography")

- **Symptom:** building/setting up on an official `runpod/pytorch` image, `pip install
  runpod` (or `-r requirements.txt`) aborts with `Cannot uninstall cryptography 41.0.7 …
  no RECORD file was found` (and/or `error: externally-managed-environment`).
- **Cause:** the base ships a **Debian-managed** `cryptography`, so pip cannot uninstall
  it to install the newer version `runpod` depends on. PEP-668 also marks the base pip
  "externally managed".
- **Fix:** `pip install --break-system-packages --ignore-installed cryptography runpod`.
  Install conflict-free dependencies (for example `faster-whisper`) first, separately, so
  `--ignore-installed` stays scoped to the `cryptography`/`runpod` pair. Verified live
  2026-07-10 (golden path 09). Bake it into the Dockerfile as two `pip install` steps.

## Cold starts and timeouts

- **Symptom:** first request after idle is slow or times out. `/runsync` returns
  a timeout while the model is still loading.
- **Cause:** cold start = container pull + start + model load. `runsync` has a
  ~60s ceiling. Large model loads can exceed it.
- **Correction:** use `/run` and poll status, or increase the synchronous timeout. Enable FlashBoot. Keep workers warm with `min_workers` or a longer `idle_timeout`. Load the model at module level, outside the handler. Use cached models or a network volume to prevent a download at each start.

## Pod shows "Running" but ports/services are not reachable yet

- **Symptom:** the pod is green/"Running", but the proxy URL returns 502. The public IP or TCP port mapping is empty, or JupyterLab shows a white screen.
- **Cause:** "Running" only means the container exists — services and port
  assignments take extra time to initialize.
- **Correction:** wait ~30–60s. Examine the **Telemetry** tab to make sure that the service is ready. When the **Connect** menu has values, read the assigned public IP and external TCP port. Note external TCP port mappings change on every pod reset, and
  Community Cloud public IPs can change on migration/restart.
- **Restart variant:** after `pod stop`→`start`, the external TCP port changes. `runpodctl ssh info` can return an old port.
  In a live development-pod case (2026-07-10), the original port was `17740`.
  After stop/start, the first `ssh info` still returned `17740`, and all SSH connections failed.
  It also returned `READY` while sshd remained unavailable for ~90s.
  A later `ssh info` returned the correct new port `12890`.

  After restart, do not trust the first `READY` or port value.
  Repeat `ssh info` until the port accepts an `ssh` connection. Then, update `~/.ssh/config` `Port`. This is what breaks VS Code
  Remote-SSH reconnects (see golden path 06).

## Proxy 524 / 100-second timeout

- **Symptom:** requests through `https://<pod-id>-<port>.proxy.runpod.net` die at
  ~100s with a `524`.
- **Cause:** the HTTP proxy runs through Cloudflare, which caps connection time at
  100 seconds.
- **Correction:** do not keep one request open for that interval. Return a job id and poll, or use background queues/progress endpoints. For long connections, use direct TCP (public IP) instead of the proxy.

## Network volume locked to a data center

- **Symptom:** cannot get GPUs, or the endpoint will not schedule workers after
  attaching a volume.
- **Cause:** a network volume lives in one DC. Attaching it forces all compute
  into that DC, shrinking GPU availability.
- **Correction:** before attachment, make sure that the volume's DC has the target GPU. Alternatively, attach multiple volumes from different DCs (one per DC) to distribute workers. Data does not sync between them automatically.

## Model not baked or mounted

- **Symptom:** handler errors with "model not found," or OOM/download stalls on
  first request.
- **Cause:** the worker has no model — it was not baked into the image, cached, or
  mounted from a volume.
- **Fix:** pick one delivery path (bake in, cached HF model at
  `/runpod-volume/huggingface-cache/hub/`, or network volume) and make the handler
  read from that path. For gated/private HF models set `HF_TOKEN`.

## Data disappeared after stop

- **Symptom:** files written during a run are gone after stopping the pod or the
  worker scaling down.
- **Cause:** you wrote to container/ephemeral disk, which is wiped on stop.
- **Fix:** write to `/workspace` (pod volume disk) or a network volume
  (`/runpod-volume` on serverless). Editing/resetting a pod also wipes anything
  outside `/workspace`.

## Huge log or job output

- **Symptom:** logs stop appearing (throttled), or job submission/result is
  rejected for size.
- **Cause:** excessive logging triggers throttling. Job payloads exceed limits
  (`/run` ~10 MB, `/runsync` ~20 MB).
- **Correction:** reduce log detail or use structured logs. Write large output to a network volume or external S3. Return a URL/reference instead of the full output.

## GPU out of memory

- **Symptom:** job fails with an OOM/CUDA memory error.
- **Cause:** model or batch size exceeds the selected GPU's VRAM.
- **Fix:** reduce batch size / context length, or pick a larger-VRAM GPU. For
  vLLM, lower `GPU_MEMORY_UTILIZATION` and/or `MAX_MODEL_LEN`.

## Serverless worker "ready" but jobs never run

- **Symptom:** the endpoint has `ready` workers but jobs sit `IN_QUEUE` with
  `inProgress: 0` and never complete.
- **Cause:** a broken/mis-dispatching worker image, or workers `throttled` on a
  scarce GPU pool unnecessary for the model.
- Fix: switch to a different (maintained) Hub worker on a broad, high-availability GPU pool. Do not continue to wait. Diagnose through endpoint `/health` worker counts. `runpodctl serverless health <id>` reads them (v2.9.0+).

  Then, read worker logs. There is no serverless worker-log command in runpodctl and no worker-log path on REST v1. Use MCP `stream-worker-logs`, the v2 REST logs path, or the Console Workers tab.

## Serverless job goes `IN_PROGRESS` then times out

- **Symptom:** a worker *picks up* the job (`IN_PROGRESS`) but never returns output.
  The job fails with `"job timed out after 1 retries"` after ~30–50 s.
- **Cause:** a healthy worker often rejects the job. A handler-signature error or empty-`input` bug in the request can cause this result. It does not necessarily indicate a broken image.
- **Fix:** get the **worker logs** (MCP `stream-worker-logs` or the Console) before
  assuming the image is bad. Real case (flash endpoint, 2026-07-10): fitness checks
  passed, then it logged `read() got an unexpected keyword argument …` /
  `Job has missing field(s): id or input` — a handler-signature + empty-input bug (see
  flash known problem "Request body shape"). Only if the logs show a genuinely dead/looping
  worker should you switch workers or try a different data center.

## Delete returns an error but succeeded

- **Symptom:** an MCP `delete-*` (or a DELETE call) returns `isError: true` /
  "Unexpected end of JSON input".
- **Cause:** the Runpod REST API returns **204 No Content**. There is no JSON body
  to parse.
- **Fix:** treat it as success. Make sure that deletion succeeded with a follow-up `get-`/`list-` (the
  resource should 404 / be absent).

## Handler swallowing errors

- **Symptom:** jobs report success but return nothing useful. Failures are
  invisible.
- **Cause:** a broad `try/except` suppresses the exception, so the SDK never marks
  the job `FAILED`.
- **Fix:** return a structured error for graceful failures, or re-raise to flag
  the job `FAILED`. Do not silently swallow.
