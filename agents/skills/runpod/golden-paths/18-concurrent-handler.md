# Golden path 18 — concurrent handler (one worker serving many requests at once)

**Goal:** For "make each worker do more", write an async handler with `concurrency_modifier`. One worker must process multiple jobs simultaneously. Prove overlap against a live service. Explain the effect on autoscaling, including fewer necessary workers.

This is the throughput knob that lives *inside* the worker. Autoscaling (golden
path 13) is the knob *outside* it.
**Status:** ✅ COVERED — live-verified 2026-07-13 end to end.

A tiny async handler
(`<your-registry>/gp18-concurrent:v1`, python:3.11-slim + runpod) with
`concurrency_modifier → 4` ran on a **CPU endpoint with workers-max 1**. Four `/run` jobs that each `await asyncio.sleep(5)` finished in 5.66 s wall clock. `/health` showed `inProgress:4` on a single running worker, with identical handler start timestamps. The
same image with `concurrency_modifier → 1` serialized the same 4 jobs to **25.2 s**
(`inProgress:1, inQueue:3`).
**Lane(s):** docker (build/push) + runpodctl (template) + Runpod REST (`/run`, `/status`, `/health`)

## When to use this
Use a concurrent handler when your work is I/O-bound. The worker spends most of each job waiting, not computing:
- Calling a remote model / third-party API and awaiting the response.
- DB or vector-store queries, object-storage reads/writes.
- Any `await`-able network round-trip.

While one job is parked on `await`, the worker's event loop runs the next job. One worker
then serves N jobs in roughly the time of one, so **fewer workers** are necessary for the same
throughput (cheaper, fewer cold starts).

Do NOT use this for CPU/GPU-bound work. If one job saturates compute, 4 simultaneous jobs share the same capacity. Each becomes slower, and GPU memory can run out. Heavy inference and image generation are examples.

For compute-bound work, keep concurrency at 1 and
scale **out** with more workers (golden path 13). Concurrency raises *per-worker*
throughput. Autoscaling adds/removes workers — they are complementary knobs.

## Prerequisites
- `RUNPOD_API_KEY` resolvable. Test: `curl -s -o /dev/null -w '%{http_code}'
  https://rest.runpod.io/v1/pods -H "Authorization: Bearer $RUNPOD_API_KEY"` → `200`.
- `docker` running + `docker login` (here: Docker Hub user `<your-registry>`).
- `runpodctl` installed + authenticated.

## The two things that make it concurrent
```
async def handler(job): ...              →  the handler must be async and await its I/O
concurrency_modifier: adjust_concurrency →  returns N = max jobs this worker runs at once
```
Both are required. An `async` handler alone runs one job at a time. `concurrency_modifier` tells the SDK that it may fetch up to N jobs for this one worker. Miss the `async`/`await` and the jobs cannot interleave. Miss the
modifier and N stays 1.

## Walkthrough (verified commands)

### 1. Handler — async + concurrency_modifier
`await asyncio.sleep(5)` stands in for a real I/O wait. The timestamps it returns are how we
later prove the overlap. `concurrency_modifier` returns a constant here for a predictable
demo — it receives `current_concurrency` and can adapt to load in production (return more
under high traffic, fewer under low).
```python
# handler.py
import runpod
import asyncio
import os
import time

CONCURRENCY = int(os.environ.get("CONCURRENCY", "4"))

async def handler(job):
    job_input = job.get("input", {})
    delay = float(job_input.get("delay", 5))
    tag = job_input.get("tag", "job")

    start = time.time()
    await asyncio.sleep(delay)          # <-- await yields the loop so other jobs run
    end = time.time()

    return {"tag": tag, "delay": delay,
            "worker": os.environ.get("RUNPOD_POD_ID", "unknown"),
            "started_at": round(start, 3), "finished_at": round(end, 3)}

def adjust_concurrency(current_concurrency):
    return CONCURRENCY                  # max jobs this ONE worker runs at once

runpod.serverless.start({
    "handler": handler,
    "concurrency_modifier": adjust_concurrency,
})
```
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /
RUN pip install --no-cache-dir runpod~=1.7.6
COPY handler.py .
CMD ["python", "-u", "/handler.py"]
```

### 2. Build (linux/amd64), local dry-run, push
```bash
docker build --platform=linux/amd64 -t <your-registry>/gp18-concurrent:v1 .
echo '{ "input": { "delay": 1, "tag": "local" } }' > test_input.json
docker run --rm --platform=linux/amd64 -e CONCURRENCY=4 \
  -v "$PWD/test_input.json:/test_input.json" <your-registry>/gp18-concurrent:v1
# → Job local_test completed successfully.  (offline SDK dry run)
docker push <your-registry>/gp18-concurrent:v1
```

### 3. Template + endpoint — workers-max 1 on purpose
`CONCURRENCY` is passed as a template environment variable so one image serves both the concurrent and
the serial (contrast) case. **`workersMax:1`** forces *concurrency*, not scaling, to absorb
the load — the whole point of the proof.
```bash
runpodctl template create --name gp18-concurrent-tpl --serverless \
  --image <your-registry>/gp18-concurrent:v1 --container-disk-in-gb 10 \
  --env '{"CONCURRENCY":"4"}'
# → template id, e.g. <template-id>

runpodctl serverless create --template-id <template-id> --name gp18-concurrent-ep \
  --compute-type CPU --workers-min 0 --workers-max 1 --data-center-ids EU-RO-1
# → endpoint id, e.g. <endpoint-id>
```
> Use `runpodctl serverless create --compute-type CPU`, **not** the REST `POST
> /v1/endpoints` with `"computeType":"CPU"` — that call silently provisions a **GPU**
> endpoint (verified 2026-07-14: it returns `gpuCount:1` / `cpuFlavorIds:null`).

`CONCURRENCY` belongs to template environment settings, not individual requests. Thus, the serial comparison in [Verify](#verify-it-works-the-actual-test--observed-output) must have its own `CONCURRENCY=1` template and endpoint. Use the same image. Only that environment value differs. Create them now so both cases are ready (skip this pair if you only want the
concurrent proof):
```bash
runpodctl template create --name gp18-serial-tpl --serverless \
  --image <your-registry>/gp18-concurrent:v1 --container-disk-in-gb 10 \
  --env '{"CONCURRENCY":"1"}'
# → serial template id, e.g. <template-id-serial>

runpodctl serverless create --template-id <template-id-serial> --name gp18-serial-ep \
  --compute-type CPU --workers-min 0 --workers-max 1 --data-center-ids EU-RO-1
# → serial endpoint id, e.g. <endpoint-id-serial>
```

## Verify it works (the actual test + observed output)
Fire 4 `/run` jobs at once, each sleeping 5 s, and watch `/health` mid-run. If they overlap,
wall clock ≈ one job (~5 s) and `/health` shows all 4 in progress on **one** worker. Warm
the worker first (one throwaway job + poll `/health` until `ready:1`), because a cold start
also gates the first call.

Observed, **concurrency = 4**, warm worker (real, 2026-07-13):
```
HEALTH mid-run: {"inProgress":4,"inQueue":0}  {"running":1}   ← 4 jobs, ONE worker
WALL CLOCK for 4 jobs (each sleeps 5s): 5.66s

tag  delayTime execTime     started_at    finished_at
c1        149     5223  1783956842.643  1783956847.645
c2        151     5287  1783956842.643  1783956847.645
c3         56     5324  1783956842.643  1783956847.644
c4        148     5280  1783956842.643  1783956847.646
handler start spread: 0.000s      ← all four entered the handler at the SAME instant
```
All four started at the identical timestamp and finished ~5 s later → they ran **together on
one worker**. Serial execution would have taken ~20 s.

For comparison, send the same 4 jobs to the serial endpoint (`<endpoint-id-serial>`) from step 3. It uses the same image with `concurrency = 1` (`--env '{"CONCURRENCY":"1"}'`):
```
HEALTH mid-run: {"inProgress":1,"inQueue":3}  {"running":1}   ← one at a time, 3 queued
WALL CLOCK for 4 jobs (each sleeps 5s): 25.2s
start times staggered ~6.4s apart            ← each job waits for the previous to finish
```
Same worker, same jobs, one line of config: **5.66 s vs 25.2 s**. That ~4× is the concurrency
win, and it is why the concurrent endpoint needed **zero** extra workers to keep up.

### How this changes autoscaling (pairs with 13)
Autoscaling decides *how many workers* to run from queue pressure (queue-delay or
request-count scalers, up to `workersMax`). Per-worker concurrency decides *how many jobs
each worker drains at once*. With higher concurrency, each worker clears the queue N× faster. The scaler sees the backlog disappear and starts fewer workers.

The same traffic uses a smaller fleet, with fewer cold starts and lower idle cost. Set `workersMax`
using **peak concurrent jobs ÷ per-worker concurrency**, not peak jobs alone. Tune the
scaler itself in golden path 13 (autoscaling).

## Gotchas we hit
1. **Concurrency ramps. It does not jump to N on the first burst.** The first burst after cold start had only 3 of 4 jobs overlap.

   The SDK calls `concurrency_modifier` again and raises the ceiling over a few polls. Thus, the 4th job landed in the next batch. Once warm, all 4 overlapped with a **0.000 s** start spread. Warm the
   worker (and let concurrency settle) before trusting a throughput measurement.
2. **`async` handler AND `concurrency_modifier` — both are necessary.** An async handler without
   the modifier still runs one job at a time (N defaults to 1). The modifier without real
   `await`points (for example a blocking `time.sleep`) cannot interleave either. The `await` is what
   yields the event loop to the next job.
3. **Concurrency is for I/O-bound work only.** CPU/GPU-bound jobs do not benefit — N of them
   time-slice the same silicon and each gets slower. On GPU you can exhaust VRAM
   (N × model memory). For compute-bound work keep concurrency at 1 and scale out (13).
4. **Shared state is now genuinely shared.** With N jobs in one process, module-level
   globals, counters, and non-thread-safe clients are touched concurrently. Keep per-job
   state inside the handler. Make any shared client concurrency-safe.
5. **`workersMax:1` is deliberate for the proof.** In production, combine concurrency and a higher `workersMax`. Concurrency fills each worker, and autoscaling adds workers only when every worker is saturated.
6. **`/health` is the live proof.** `inProgress` climbing above 1 while `workers.running`
   stays at 1 is the direct evidence of per-worker concurrency. `inQueue` piling up with
   `inProgress:1` is the serial signature.

## Cost & cleanup
```bash
runpodctl serverless delete <endpoint-id>      # concurrent endpoint
runpodctl serverless delete <endpoint-id-serial>      # serial (contrast) endpoint
runpodctl template delete <template-id>            # concurrent template
runpodctl template delete <template-id-serial>            # serial template
runpodctl serverless list && runpodctl pod list # confirm clean
```
Both endpoints were scale-to-zero (`workersMin:0`), ~$0 idle, and deleted after the run
(verified: 0 gp18 endpoints/templates/pods remain). The public image
`<your-registry>/gp18-concurrent:v1` was **left in place** so this doc references a real,
pullable tag. It costs nothing. No pod or volume is created by this path.

## Skill gaps folded back
- The live run confirmed measurable per-worker concurrency. When `concurrency_modifier` returns N, one worker can hold N jobs in progress (`/health inProgress:N, running:1`). A 4-job I/O-bound burst decreased from ~25 s (serial) to ~5.7 s on a single worker.
- Documented the **ramp-up** behavior (concurrency rises over a few polls, not instantly)
  and the **workers-max sizing rule** (peak jobs ÷ per-worker concurrency) as the concrete
  bridge to autoscaling (golden path 13).
