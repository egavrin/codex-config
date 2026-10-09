# Invoke a serverless endpoint and get the result

## Prompt

I have a serverless endpoint `ep-abc123` running a vLLM worker. Send it
`{"prompt": "why is the sky blue?"}` and show me what it returns.

## Expected behavior

The agent should do these actions:

1. Invoke with `runpodctl serverless run ep-abc123 --input '{"prompt":"why is the sky blue?"}'`,
   which submits the job and polls until its final state.
2. Pass only the **handler** payload — the cli wraps it as `{"input": ...}` itself.
3. Read the job payload from stdout, including on job failure. Report the worker's output or its `error`.
4. If `timeout` names a `serverless status` command after the wait budget expires, poll that command. Do not invoke the job again.

## Assertions

- Uses `runpodctl serverless run ep-abc123` with `--input` (or `--input-file`)
- Does not hand-build a `curl` to `https://api.runpod.ai/v2/ep-abc123/run` or `/runsync`, and does not construct an `Authorization: Bearer` header by hand
- Does not double-wrap the payload as `{"input":{"prompt":...}}`
- On a `timeout`, polls with `runpodctl serverless status ep-abc123 <job-id>` instead of re-submitting the job
- Treats a `job_failed` exit as the worker's failure (payload on stdout), not as a cli/auth problem
