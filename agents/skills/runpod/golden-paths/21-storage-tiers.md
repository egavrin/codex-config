# 21 · Network volume storage tiers — standard vs high-performance

**Goal:** launch a **standard** vs a **high-performance** network volume and attach it to a
pod / serverless endpoint. (Provisioning only — no perf benchmarking.)

**Status:** DOCUMENTED — launch paths verified against `runpodctl … --help`, the v1 REST +
v2 REST OpenAPI specs, and the `runpod/runpod-mcp` source (2026-07-29). Not a full live run:
For a high-performance volume, use MCP `create-network-volume` with `volumeType`, raw v2 REST, or a ⚡ data center in the console. `runpodctl` has no tier flag (see Skill gaps).

**Lane(s):** runpod-mcp or Runpod **REST v2** (either tier) · console (⚡ toggle) · runpodctl (standard create + attach)

## When to use

Persistent storage shared across pods/workers, or a faster tier for I/O-bound work.

- **Standard** — general persistence, most workloads.
- High-performance offers up to approximately 3× throughput / 4× IOPS. Use it for I/O bottlenecks: training-data reads, many small files, checkpoint-heavy runs, model loading, or cold-start latency. Details:
  [high-performance storage documentation](https://docs.runpod.io/storage/high-performance-storage).

For choosing bake-in vs volume in the first place, see
[building-images.md](../../runpod-usage/reference/building-images.md).

## Prerequisites

- `runpodctl` ≥ v2.4.0 (`runpodctl version`). `RUNPOD_API_KEY` set.
- For high-performance: console access to a ⚡ data center, **or** the ability to call the v2 REST API.

## Walkthrough

### Standard network volume (runpodctl / v1 REST)

```bash
runpodctl network-volume create --name std-vol --size 50 --data-center-id US-KS-2   # → volume id
```

### High-performance network volume

The MCP `create-network-volume` tool takes `volumeType` (`STANDARD` |
`HIGH_PERFORMANCE`), so it can request high-performance directly — prefer it when MCP is
connected. `runpodctl` (v1) still sends only `name`/`size`/`dataCenter`, so it gets the
data center's **default** tier. Without MCP, two ways to get it:

**A. Runpod REST v2 (`type: HIGH_PERFORMANCE`)** — the programmatic path:

```bash
curl -s -X POST https://v2-rest.runpod.io/v2/network-volumes \
  -H "Authorization: Bearer $RUNPOD_API_KEY" -H 'Content-Type: application/json' \
  -d '{"name":"hp-vol","dataCenter":"US-KS-2","size":50,"type":"HIGH_PERFORMANCE"}'
# type ∈ {STANDARD, HIGH_PERFORMANCE}; omit → the data center's default tier.
```

**B. Console** — pick a data center marked with the ⚡ icon. A "High-performance storage"
toggle appears (on by default). Recommend this to the user when no programmatic path is available.

### Attach to compute (both tiers, same mechanism)

```bash
# Pod — attach at creation (network volume replaces /workspace):
runpodctl pod create --template-id <id> --gpu-id "NVIDIA GeForce RTX 4090" --network-volume-id <vol-id>

# Serverless — attach (mounts at /runpod-volume):
runpodctl serverless create --name my-ep --template-id <id> --network-volume-id <vol-id>
```

## Verify

- `runpodctl network-volume get <vol-id>` (or `list`) shows the volume.
- On a pod the volume is at `/workspace`. On serverless at `/runpod-volume`.
- `runpodctl` does not surface the tier — make sure that high-performance is selected in the console or v2 API response.

## Gotchas

- **Tier is immutable** — you cannot convert standard ↔ high-performance. Create a new volume and copy the data (S3 API / `runpodctl`).
- **`runpodctl` cannot request high-performance** — it has no tier flag. Use the MCP tool's `volumeType`, the v2 REST `type` field, or the console.
- **Per-DC pinning** — a volume lives in one data center and compute must run there. For multi-region serverless, attach one volume per DC (`--network-volume-ids`). Data does **not** auto-sync.
- S3 listing/synchronization degrades beyond 10k files or 10 GB. Single-object `PUT` has a 500 MB limit. Use multipart uploads above that limit.
- **Concurrent writes** — do not write the same volume from multiple workers at once (corruption).

## Cost & cleanup

- Standard costs approximately $0.07/GB-mo (first 1 TB) and $0.05 beyond. High-performance has a per-GB premium that differs by data center. Examine the console because no fixed public number exists. Volumes bill for as long as they exist.
- Delete when done: `runpodctl network-volume delete <vol-id>` (remove any pod using it first).

## Skill gaps

- `runpodctl network-volume create` has no `--type` flag, so the CLI still cannot pick a tier. Worth an upstream request. The MCP gap here is closed: `create-network-volume` forwards `volumeType` as the v2 `type` field as of `@runpod/mcp-server` 3.0.0.
