# Routing: diagnosing a failing serverless job (health / status / worker logs)

## Prompt

I'm in a plain terminal — no MCP tools connected. My serverless endpoint
`ep-abc123` just returned a `FAILED` job (`job-xyz`). Walk me through finding out
why. Then tell me what changes if I *do* have the Runpod MCP connected.

## Expected behavior

Follows golden path 15 (`runpod/golden-paths/15-monitor-and-debug.md`), which
splits into three signals — all three now reachable from the CLI lane:

1. **Worker/job counts → `runpodctl serverless health ep-abc123`** (v2.9.0+). Do not construct a custom `curl` to `https://api.runpod.ai/v2/ep-abc123/health` for this case. That is a fallback for an older binary or a copy-paste example. The CLI returns the same payload unchanged.
2. **The job itself → `runpodctl serverless status ep-abc123 job-xyz`**. Reads
   `status`, `error`, `retries`, and the `delayTime` vs `executionTime` split to
   decide scaling-bound vs handler-bound, and takes `workerId` from it. Recognizes that the command exits **1** with `{"code":"job_failed"}` after terminal `FAILED`. The job payload remains on stdout. This indicates a job failure, not a CLI failure.
3. **Worker logs → `runpodctl serverless logs ep-abc123`** (v2.10.0+), narrowed with
   `--worker <workerId>` from step 2. Output uses JSON lines (`{source,line,ts,workerId}`), so it pipes to `jq`. Do not use a custom SSE read against `v2-rest.runpod.io/.../logs` or claim "the CLI can't do this". The custom path and Console **Workers** tab are fallbacks for binaries before v2.10.0.
   Reads `--source container` for the handler's traceback, and knows `--source system`
   with repeated "start container" and no container output means a crash loop.

With MCP connected, `endpoint-health` and `get-job-status` are reasonable substitutes for steps 1–2. For step 3, `list-endpoint-workers` → `stream-worker-logs` returns bounded, parsed frames. That is more convenient than CLI JSON lines. It is **not** a capability absent from the CLI. Only `stream-job` (incremental job output) is genuinely
MCP-only.

## Assertions

- Uses `runpodctl serverless health` and `runpodctl serverless status` rather than
  steering to raw `curl` for `/health` and `/status`.
- Do not claim that runpodctl supports only create/list/delete. It also invokes (`serverless run`), polls (`serverless status`), reports health, and edits configuration (`serverless update`).
- Reaches `runpodctl serverless logs` for the worker logs. Do not claim that runpodctl cannot read worker logs. Do not make a connected MCP server mandatory for those logs.
- For an older binary, a raw v2 REST SSE fallback must have a bounded read (`curl -m`). Do not follow an open stream indefinitely.
- Treats a non-zero exit with `job_failed` as the worker's failure, not a CLI or
  auth problem.
