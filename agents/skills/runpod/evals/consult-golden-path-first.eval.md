# Routing: check the worked example before planning a multi-step job

## Prompt

Two requests, answer both:

(a) Stop pod `abc123`.
(b) I want to serve a HuggingFace model on a serverless endpoint without baking the
weights into the image or managing a network volume. Get me there.

## Expected behavior

The two halves must route **differently** — that split is the point of this eval.

**(a) is a single CRUD call → skip step 0.** Goes straight to the lane per the
capability matrix (`stop-pod` if MCP is connected, else `runpodctl pod stop abc123`).
Opening a golden path for this is wrong: it burns a file read on a one-liner.

**(b) uses multiple resources and provisions a billable resource, so step 0 applies.** Before plans or calls, match the task against the index in `runpod/SKILL.md`. Find *"Serve a HuggingFace model without baking it in or a volume (host-cached)"*. Open [golden path 20](../golden-paths/20-model-caching-endpoint.md) and follow it.

Include `--model-reference` syntax, the GPU-only constraint, and cost/cleanup instructions.
Do not derive another plan from the tool tables. Do not go directly to `create-endpoint`/`serverless create` and invent the model configuration.

A partial match also counts. A different model can still use the path's order and known-problem guidance. Reading that path is correct.

## Assertions

- **(a)** answers with a single call and does **not** open a golden path
- **(b)** consults the golden-paths index **before** proposing commands or a plan
- **(b)** identifies path 20 (model caching / `--model-reference`) specifically, not
  just "there are examples"
- **(b)** does not present a hand-derived multi-step plan as the primary answer when a
  verified path covers it
- Neither half claims a capability is missing without checking (see
  `no-unchecked-absence-claims.eval.md`)

---

## Scenario B — entering a lane directly (the discriminating case)

Measurement showed that Scenario A above is a **weak test**. Agents opened the matching path with and without step 0. The router's "Want to…" table has an almost identical row, and agents read the complete file. Keep A for
the skip-on-trivial-call half, but A alone does not detect a regression.

The distinguishing case is an agent that **never reads the router** because it already uses a specific workflow. This is normal after a session starts.

### Prompt

*(session where the Runpod MCP tools are connected; entrypoint is
`runpod-mcp/SKILL.md`, not the router)*

I need a highly-available serverless endpoint. Same model weights available in three
different data centers so a regional outage does not take me down. Walk me through it.

### Expected behavior

1. **Opens `runpod/golden-paths/README.md` before planning**, on the strength of the
   lane's own "for a multi-step job, read the worked example before calling tools"
   pointer — not because the user said "check the examples".
2. **Lands on path 19** (3-region) or path 10 (2-region HA).
3. **One endpoint, one volume per DC** — `--network-volume-ids v1,v2,v3` with
   `--data-center-ids`. Not three separate endpoints behind a custom failover
   layer, and not "bake the weights, volumes can't do this".
4. **Flags that volumes do not replicate automatically** — a partial sync means a
   fraction of traffic silently serves stale weights.
5. State that MCP's `create-endpoint` does not express multi-volume attachment. For that step, use runpodctl or the GraphQL `saveEndpoint` fallback.

### Assertions

- Opens a golden path **before** settling on an approach
- Plan attaches several per-DC volumes to **one** endpoint
- Warns about non-replication
- Does **not** claim that a multi-DC endpoint cannot mount per-DC volumes. That false absence claim was the observed failure when the example was not read.

### Measured 2026-08-19

Same prompt, 2 runs per arm, `origin/main` vs this branch, agents reporting the files
they opened:

| | opened a golden path | plan source | one endpoint + per-DC volumes |
| --- | --- | --- | --- |
| without the lane pointer | 0 / 2 | derived | 0 / 2 |
| with it | 2 / 2, before planning | golden-path | 2 / 2 |

Both control runs invented a limitation to justify the derived plan — *"you cannot
attach one network volume to a multi-DC endpoint"* and *"network volumes are not a
mechanism for multi-DC redundancy"* — both falsified by path 10's live 2026-07-10 run.
