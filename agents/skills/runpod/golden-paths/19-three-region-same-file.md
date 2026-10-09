# Golden path 19 — three-region same-file endpoint (prove the HA promise with a real served payload)

**Goal:** Extend [10](10-multi-region-ha-serverless.md) to one endpoint with three network volumes in three data centers. Synchronize the same file to all three. Prove identical responses to the same request regardless of the selected DC. Path 10 demonstrated multi-volume attachment and manual S3 sync across **two** DCs.
This path uses **three** DCs. A burst reaches **all three** and returns **byte-identical** output every time.

**Status:** ✅ **COVERED — live-verified 2026-07-13** end to end.
The run created **three** 10 GB volumes: `gp19-euro` in **EU-RO-1**, `gp19-eucz` in **EU-CZ-1**, and `gp19-euris` in **EUR-IS-1**.
All supported S3. It **S3-synced identical `gp19-data/` to all three**.
`aws s3 ls` showed identical sizes: 23 B marker and 106 B payload on each.
It deployed **one CPU endpoint** with **all three** volumes through GraphQL `saveEndpoint`.

The **32-request concurrent burst** returned **32/32 `COMPLETED`**.
The 10 workers used all three DCs: EU-RO-1 ×4, EU-CZ-1 ×5, and EUR-IS-1 ×1.
Each worker read its **co-located** volume.
Every response was **byte-identical**: 1 distinct marker and 1 distinct payload across all 32.
The image was `<your-registry>/gp19-3region:v2` (`python:3.11-slim` + `runpod`).
The run deleted all three volumes, endpoint, and templates afterward.

**Lane(s):** `runpodctl` (volumes) + `aws`/S3 API (sync, see
[companion-clis → AWS CLI](../../companion-clis/SKILL.md#aws-cli)) + GraphQL
`saveEndpoint` (multi-volume attach — required on runpodctl < v2.4.0, see
[10](10-multi-region-ha-serverless.md))

## When to use

Use this to *demonstrate* — not just assert — that a multi-region
endpoint serves consistent results. Path [10](10-multi-region-ha-serverless.md) is the
canonical HA reference (mechanism, the three sync methods, the operating discipline).
This path proves the complete workflow with a served payload. A handler reads the synchronized file from `/runpod-volume` and reports the answering DC/worker. Observe requests across three DCs and make sure that each returns identical bytes. Use it as
a template for a smoke test you run after every re-sync.

## The thesis, restated

| | What you attach | Where workers schedule | What a request sees |
| --- | --- | --- | --- |
| One volume | 1 volume, 1 DC | only that DC | one disk — always consistent, but hostage to one DC |
| **Three volumes (this path)** | 1 volume per DC × 3 DCs | **any of the 3 DCs** | **three independent disks** — consistent **only if you keep them byte-identical** |

The availability win (3× the GPU/CPU pools) is free once you attach three volumes. The
Correctness depends on explicit synchronization. Volumes do not synchronize automatically. EU-CZ-1 requests read the EU-CZ-1 disk, and EUR-IS-1 requests read the EUR-IS-1 disk. Different disk contents cause silently different endpoint responses. This path
proves the disks match by serving the file and comparing the bytes returned from every DC.

## Prerequisites

- `runpodctl` (any version — single-volume create + volume management). This run used GraphQL `saveEndpoint` because runpodctl v2.3.0 could not attach multiple volumes. In ≥ v2.4.0, use `runpodctl serverless create --network-volume-ids v1,v2,v3` ([10 step 4](10-multi-region-ha-serverless.md#4-attach-all-volumes-to-one-endpoint-one-per-dc)).
- `aws` CLI with a profile holding your Runpod **S3 API keys** (access key = Runpod
  `user_...`, secret = `rps_...`). These are **Console-only** to create (Settings → S3 API
  Keys) — an agent cannot self-provision them. See
  [companion-clis → AWS CLI](../../companion-clis/SKILL.md#aws-cli).
- Docker + a registry (here `<your-registry>`). Build `--platform linux/amd64`.
- Three DCs that all expose the **S3 API** (so sync can operate without compute):
  **EU-RO-1, EU-CZ-1, EUR-IS-1** are all supported.

## Walkthrough

> Reuse placeholders through S3 synchronization, GraphQL attachment, validation, and cleanup.
> Record each returned ID.
> Use `<vol-ro>`/`<vol-cz>`/`<vol-is>` for the three DC volumes, `<template-id>` for the template, and `<endpoint-id>` for the endpoint. Same placeholder = same
> resource everywhere.

### 1. Create one 10 GB volume per DC

```bash
runpodctl network-volume create --name gp19-euro  --size 10 --data-center-id EU-RO-1
runpodctl network-volume create --name gp19-eucz  --size 10 --data-center-id EU-CZ-1
runpodctl network-volume create --name gp19-euris --size 10 --data-center-id EUR-IS-1
```
✅ Live output (each id becomes both the S3 bucket name and an attach arg):
```json
{ "dataCenterId": "EU-RO-1",  "id": "<vol-ro>", "name": "gp19-euro",  "size": 10 }
{ "dataCenterId": "EU-CZ-1",  "id": "<vol-cz>", "name": "gp19-eucz",  "size": 10 }
{ "dataCenterId": "EUR-IS-1", "id": "<vol-is>", "name": "gp19-euris", "size": 10 }
```
> You pay storage **per volume** — three volumes = 3× the GB bill ($0.07/GB/mo to 1 TB).
> Size only for the data you replicate.

### 2. Sync the SAME file to all three (S3 API, no compute)

One canonical local source → every volume. The bucket is the volume id. `--region` is the
DC id. The endpoint host is the DC id lower-cased.

```bash
mkdir -p gp19-data
printf 'gp19 shared payload v1\nThe same bytes must be served from every DC.\nchecksum-anchor: 3region-identical-42\n' > gp19-data/payload.txt
printf 'gp19-3region-marker-v1\n' > gp19-data/marker.txt

for pair in "EU-RO-1:<vol-ro>" "EU-CZ-1:<vol-cz>" "EUR-IS-1:<vol-is>"; do
  DC=${pair%%:*}; VOL=${pair##*:}
  aws s3 sync ./gp19-data/ --profile runpod --region "$DC" \
    --endpoint-url "https://s3api-$(echo "$DC" | tr 'A-Z' 'a-z').runpod.io/" \
    "s3://$VOL/gp19-data/"
done
```

### 3. Verify the three disks are byte-identical (this is the point)

```bash
for pair in "EU-RO-1:<vol-ro>" "EU-CZ-1:<vol-cz>" "EUR-IS-1:<vol-is>"; do
  DC=${pair%%:*}; VOL=${pair##*:}
  echo "=== $DC ($VOL) ==="
  aws s3 ls --profile runpod --region "$DC" \
    --endpoint-url "https://s3api-$(echo "$DC" | tr 'A-Z' 'a-z').runpod.io/" "s3://$VOL/gp19-data/"
done
```
✅ **Live 2026-07-13** — identical file set + sizes on all three independent disks:
```
=== EU-RO-1 (<vol-ro>) ===
2026-07-13 11:32:49         23 marker.txt
2026-07-13 11:32:49        106 payload.txt
=== EU-CZ-1 (<vol-cz>) ===
2026-07-13 11:32:51         23 marker.txt
2026-07-13 11:32:51        106 payload.txt
=== EUR-IS-1 (<vol-is>) ===
2026-07-13 11:32:53         23 marker.txt
2026-07-13 11:32:53        106 payload.txt
```

### 4. A tiny handler that serves the file + reports who answered

`handler.py` reads the synced file from `/runpod-volume/gp19-data`.
It returns the contents and the worker/DC identity.
`RUNPOD_DC_ID` identifies the DC per request.
`RUNPOD_VOLUME_ID` proves that each worker mounted its own DC's volume.
An optional `hold` keeps a worker busy so a burst causes scale-out (see Verify):

```python
import os, socket, time, runpod
VOL = "/runpod-volume/gp19-data"

def _read(name):
    try:
        with open(os.path.join(VOL, name)) as f:
            return f.read().strip()
    except Exception as e:
        return f"<error reading {name}: {e}>"

def handler(event):
    hold = float((event.get("input") or {}).get("hold", 0))
    if hold:
        time.sleep(hold)                      # keep this worker busy → force scale-out
    return {
        "marker":  _read("marker.txt"),
        "payload": _read("payload.txt"),
        "served_by": {
            "hostname":         socket.gethostname(),
            "RUNPOD_DC_ID":     os.environ.get("RUNPOD_DC_ID"),
            "RUNPOD_VOLUME_ID": os.environ.get("RUNPOD_VOLUME_ID"),
        },
    }

runpod.serverless.start({"handler": handler})
```
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir runpod
COPY handler.py .
CMD ["python", "-u", "handler.py"]
```
```bash
docker build --platform linux/amd64 -t <your-registry>/gp19-3region:v2 .
docker push <your-registry>/gp19-3region:v2
```

### 5. Create the CPU endpoint and attach all three volumes (GraphQL `saveEndpoint`)

Make a template, create the endpoint with **one** volume (REST/CLI accept the singular
field), then attach the **full set of three** with `saveEndpoint`:

```bash
runpodctl template create --name gp19-tpl --serverless \
  --image <your-registry>/gp19-3region:v2 --container-disk-in-gb 10     # → template id <template-id>

# create with one volume + all three DCs
curl -s -X POST https://rest.runpod.io/v1/endpoints \
  -H "Authorization: Bearer $RUNPOD_API_KEY" -H 'Content-Type: application/json' \
  -d '{"templateId":"<template-id>","name":"gp19-3region",
       "networkVolumeId":"<vol-ro>","dataCenterIds":["EU-RO-1","EU-CZ-1","EUR-IS-1"],
       "workersMin":0,"workersMax":12}'                              # → endpoint id <endpoint-id>
```
Now attach all three. `networkVolumeIds` takes **objects**, and `api.runpod.io/graphql`
must have a browser-like `User-Agent` (Cloudflare returns 403/1010 otherwise). To select CPU for the endpoint, pass `instanceIds` (a CPU flavor, for example `cpu3c-2-4`) and empty `gpuIds`. `EndpointInput` has no `computeType` field. It expresses CPU through `instanceIds`:

```bash
curl -s -X POST "https://api.runpod.io/graphql?api_key=$RUNPOD_API_KEY" \
  -H 'Content-Type: application/json' -H 'User-Agent: Mozilla/5.0' \
  -d '{"query":"mutation($input:EndpointInput!){saveEndpoint(input:$input){id name computeType instanceIds}}",
       "variables":{"input":{"id":"<endpoint-id>","name":"gp19-3region","templateId":"<template-id>",
         "instanceIds":["cpu3c-2-4"],"gpuIds":"",
         "dataCenterIds":["EU-RO-1","EU-CZ-1","EUR-IS-1"],
         "networkVolumeIds":[{"networkVolumeId":"<vol-ro>"},
                             {"networkVolumeId":"<vol-cz>"},
                             {"networkVolumeId":"<vol-is>"}],
         "workersMin":0,"workersMax":12,"scalerType":"QUEUE_DELAY","scalerValue":1,"idleTimeout":5}}}'
```
✅ **Live 2026-07-13** — returned `"computeType":"CPU","instanceIds":["cpu3c-2-4"]`, and
`GET /v1/endpoints/<endpoint-id>` confirmed all three attached:
`"networkVolumeIds":["<vol-is>","<vol-ro>","<vol-cz>"]`.

> On **runpodctl ≥ v2.4.0** you can skip the GraphQL step entirely:
> `runpodctl serverless create --template-id <template-id> --compute-type CPU
> --network-volume-ids <vol-ro>,<vol-cz>,<vol-is> --data-center-ids
> EU-RO-1,EU-CZ-1,EUR-IS-1 --workers-min 0 --workers-max 12`. Examine `runpodctl version`.

### 6. Verify — one endpoint, three DCs, one payload ✅ live 2026-07-13

The scheduler favors whichever DC has capacity, so a small burst of an instant handler
concentrates on **one** DC. To distribute work, send a concurrent burst with `hold`. Busy workers make the autoscaler add workers in parallel across DCs. A 32-request concurrent burst (`hold=35`, `workersMax=12`), polled to
completion:

```
STATUS:            {'COMPLETED': 32}                          # 32/32 succeeded
DC distribution:   {'EU-RO-1': 12, 'EU-CZ-1': 16, 'EUR-IS-1': 4}   # served from ALL THREE DCs
DISTINCT markers:  1   ('gp19-3region-marker-v1')             # identical regardless of DC
DISTINCT payloads: 1   ('gp19 shared payload v1 … checksum-anchor: 3region-identical-42')
```
Ten distinct workers answered, each reading its **co-located** volume — the same
`/runpod-volume/gp19-data` on every worker resolves to *that worker's DC's* disk:
```
DC=EU-CZ-1   VOL=<vol-cz>   (gp19-eucz)   × 5 workers
DC=EU-RO-1   VOL=<vol-ro>   (gp19-euro)   × 4 workers
DC=EUR-IS-1  VOL=<vol-is>   (gp19-euris)  × 1 worker
```
The three-region run proved that each worker mounted its DC's independent volume (`RUNPOD_VOLUME_ID` identified the co-located volume). All 32 responses were byte-identical because the three disks contained the same synchronized file. Drift on any one volume would have shown up as
a second distinct payload from that DC's workers.

> **Getting the spread.** A first, sequential burst of 18 instant requests all landed on
> **one** DC (warm workers get reused). Raising `workersMax`, submitting **concurrently**,
> and adding a `hold` is what forced scale-out: 24 concurrent → 2 DCs, 32 concurrent →
> all 3. Workers in one DC can prove parity if they read the synchronized file. To exercise HA and placement across DCs, use real concurrency.

## Keeping the three volumes in sync (operating discipline)

Same rules as [10](10-multi-region-ha-serverless.md#keeping-volumes-in-sync-operating-discipline),
now across three disks:
- **One source of truth** (a canonical local dir or your own bucket) → push to **all
  three** volumes. Never edit a volume ad hoc.
- **Re-sync to all three on every data change**, then run again the step-6 burst as a smoke
  test. A model bump that lands on 2 of 3 volumes = ~1/3 of traffic serving stale data.
- After every sync, compare `aws s3 ls` sizes across all three volumes. Compare checksums when possible. Make sure that the served burst returns a single distinct payload.
- **Volumes are read-only data planes.** Writes go through your sync pipeline, not the
  handler — concurrent worker writes can corrupt a volume.

## Gotchas

- **No auto-sync** — the entire reason this path exists. Three independent disks. Drift on
  any one → that DC's workers serve different bytes. Prove parity with a served burst, not
  a claim.
- **One volume per DC** — you cannot stack two volumes in the same DC. Each of the three
  DCs gets exactly one. Each worker's `RUNPOD_VOLUME_ID` = its own DC's volume.
- **Traffic concentrates without concurrency** — the scheduler prefers one DC's capacity.
  Instant handlers + sequential requests reuse one DC's warm workers. Force spread with
  concurrent submission + a `hold` + higher `workersMax` (step 6).
- For multi-volume attachment through one `--network-volume-ids v1,v2,v3` call, runpodctl ≥ v2.4.0 is necessary. On older CLIs, use the GraphQL `saveEndpoint` object shape (step 5). The Console UI (Edit Endpoint → Advanced → Network Volumes) also works.
- **For GraphQL `saveEndpoint`, supply `User-Agent: Mozilla/5.0`** on `api.runpod.io/graphql`.
- **`EndpointInput` has no `computeType`** — express CPU via `instanceIds` (a CPU flavor
  like `cpu3c-2-4`) + empty `gpuIds`. Omit both and the endpoint stays GPU.
- S3 is available only in certain DCs, including EU-RO-1, EU-CZ-1, EUR-IS-1, US-KS-2, and [others](https://docs.runpod.io/storage/s3-api). Without S3, populate the volume through a CPU pod ([10 Method 2](10-multi-region-ha-serverless.md#method-2--cpu-pod-in-dc-no-gpu)).
- **Cost scales with N** — three volumes = 3× the storage bill. Size minimally.
- **S3 access key ≠ API key** — the AWS "access key" is your Runpod `user_...` id, secret
  is the `rps_...` S3 key (Console-only), not `RUNPOD_API_KEY`.

## Cost & cleanup

```bash
runpodctl serverless delete <endpoint-id>        # endpoint (drops the 3-volume attach)
runpodctl template delete   <template-id>            # template(s)
runpodctl network-volume delete <vol-ro>        # gp19-euro  (EU-RO-1)  — billed separately
runpodctl network-volume delete <vol-cz>        # gp19-eucz  (EU-CZ-1)
runpodctl network-volume delete <vol-is>        # gp19-euris (EUR-IS-1)
runpodctl serverless list && runpodctl network-volume list && runpodctl pod list   # confirm clean
```
✅ All deletions returned `{"deleted": true}` on the live run. Lists came back with only
pre-existing resources. Scale-to-zero (`workersMin 0`) and tiny CPU workers kept compute cost near $0. The three 10 GB volumes were the only meaningful cost.

They were deleted immediately. The pushed image `<your-registry>/gp19-3region:v2` (a ~150 MB
`python:3.11-slim` + `runpod` handler) was **left public** so this doc references a real,
pullable tag. It costs nothing.

## Relation to other paths & skill gaps

- [10 (multi-region HA serverless)](10-multi-region-ha-serverless.md) defines the mechanism, three volume-population methods, and operating rules. 19 proves the pattern across three regions. It uses the same file in three DCs. A request burst returns identical bytes from all three.
- **[07 (network-volume handoff)](07-network-volume-handoff.md)** is the single-volume
  pod↔serverless base case. For a DC without the S3 API, its pod+volume pattern is how you
  populate that DC's disk.
- **[05](05-model-to-endpoint-pipeline.md)/[08](08-finetune-to-serverless.md)** produce
  the artifact you then replicate across DCs here.
- **Skill gap:** the CPU-via-`instanceIds` shape for `saveEndpoint` (no `computeType`
  field) is worth folding into
  [endpoint-workflows.md](../../runpod-usage/reference/endpoint-workflows.md) alongside
  the multi-volume version note from 10.
