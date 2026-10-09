# Deploy a vLLM serverless worker from the Runpod Hub

## Prompt

Deploy the vLLM serverless worker from the Runpod Hub. Use an available GPU, and
have it scale from 0 up to 2 workers. Give me the exact command(s).

## Expected behavior

The agent should do these actions:

1. Find the hub listing id with `runpodctl hub search vllm`
2. Create the endpoint with `runpodctl serverless create --hub-id <id> --workers-min 0 --workers-max 2`
3. Handle the GPU correctly (this is the easy thing to get wrong):
   - Preferably omit `--gpu-id` and let the hub config's default GPU apply, OR
   - If specifying `--gpu-id`, use a GPU **pool ID** (for example `AMPERE_48`, `ADA_24`, `HOPPER_141`) — not a display name like `"NVIDIA A40"` from `runpodctl gpu list`. On the `--hub-id` path the API rejects display names with `Invalid GPU Pool ID`.

## Assertions

- Finds the hub id via `runpodctl hub search vllm` (does not invent one)
- Runs `runpodctl serverless create --hub-id <id> ...`
- Sets `--workers-min 0` and `--workers-max 2`
- If supplied, `--gpu-id` must name a GPU pool ID (for example `AMPERE_48`). Do not use a `gpu list` display name such as `"NVIDIA A40"`.
- Does not pass a `gpu list` display name to `--gpu-id` on the hub path

## Notes

This evaluation covers the problem found in live tests and tracked as runpod/runpodctl#287. On the `--hub-id` path, `serverless create --gpu-id` must use GPU pool IDs. However, `gpu list` and the `--help` text show display names. Until
that is reconciled, the safe answer is to omit `--gpu-id` or use a pool ID.
