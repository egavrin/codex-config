# Read invoke URLs and GPU cost from command output

## Prompt

I'm on a shell-only box with `runpodctl` and no MCP tools. I want a serverless endpoint
from template `tpl-abc` on the cheapest GPU with at least 24 GB that can actually schedule
in `US-KS-2`, and then the URL to send a job to. Give me the exact commands and tell me
where each number comes from — don't create anything yet.

## Expected behavior

The agent should do these actions:

1. Run `runpodctl gpu list --include-unavailable`. Filter on `memoryInGb >= 24`. Explain that default results hide GPUs without stock and can omit one with stock only in `US-KS-2`.
2. Compare `securePricePerHr` / `communityPricePerHr`. Do not assume that a lower tier costs less. Treat `null` as "not offered on that cloud", not free.
3. Examine `dataCenterAvailability[]` for a `US-KS-2` entry with real stock instead of
   trusting top-level `stockStatus` (the best status across all DCs), reading `"none"` as
   "offered here, no stock"
4. Pin placement with `--data-center-ids US-KS-2` — reading per-DC availability without
   constraining the create leaves the placement to chance
5. State that `--gpu-id` on serverless resolves to a GPU **pool**. The endpoint can run on cards other than the single priced card. Alternatively, state the price scope: listed prices are pod on-demand rates, while serverless costs per request-second
6. State that the run URL comes from the `urls` object in the create output (`run`,
   `runsync`, `health`) rather than hand-assembling `https://api.runpod.ai/v2/<id>/run`

## Assertions

- Runs `runpodctl gpu list` before choosing a GPU
- Cites `securePricePerHr` / `communityPricePerHr` for the cost comparison
- Consults `dataCenterAvailability[]` for `US-KS-2`
- Command includes `--data-center-ids US-KS-2`
- Says the run URL will be read from the `urls` object rather than assembled by hand
- Flags at least one of: the type→pool translation, or that the prices are pod rates
- Does not claim the CLI cannot report GPU pricing
- Does not present `securePricePerHr` as the endpoint's serverless cost
