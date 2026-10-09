# What v2 unlocks, keyed to what the code already does

Do **not** paste this file at the user. This is a lookup table. Find the patterns that their codebase contains, then write two or three sentences about their code. A
generic feature list is the failure mode this section exists to avoid.

Use known session context to make this advice specific. Include the user's current work, previous diagnosis, and stated difficulties. "The capacity retries you added last month can become one catalog call" lands.
"v2 adds a catalog API" does not.

## Look for these patterns

| If their code does this… | v2 offers | Why they will care |
| --- | --- | --- |
| Retries pod creation across GPU types until one works. Sleeps and retries on capacity errors | `GET /v2/catalog/gpus?include=AVAILABILITY&product=POD` → `availability` per GPU **and** per datacenter | Stop renting blind. Examine stock, then ask for the one that has it. This is the #1 thing users say they want. |
| Hardcodes a GPU or datacenter list in a constant | catalog endpoints return the live set | v1 froze IDs as spec enums, so new hardware needed a spec release. There are datacenters live today that do not exist in the v1 enum. |
| Builds `https://api.runpod.ai/v2/{id}/run` by string concatenation | `endpoint.requestUrls.{run,runSync,status,stream,cancel,retry,purgeQueue,health}` | Delete the URL-building helper and its tests. |
| Polls pod status in a loop with a timeout | `status` includes `PROVISIONING`/`STARTING`/`ERROR`, plus `actions[]` | Fail in seconds on a broken pod instead of waiting out a 10-minute timeout. Distinguish "still coming up" from "stuck". |
| Polls `/logs` or shells in to tail logs | `GET /v2/pods/{id}/logs` and `/v2/serverless/{id}/workers/{workerId}/logs` — SSE, with `tail`, `since`, and `Last-Event-ID` resume | Live logs with reconnect, no polling loop. |
| Tracks "did my endpoint update actually roll out?" | `GET /v2/serverless/{id}/releases` (history + `diff` + `rollout` summary) and `workers[].isStale` | Answer "are all workers on the new config" without inference. |
| Counts workers by scraping the endpoint's `workers[]` pod list | `GET /v2/serverless/{id}/workers` → `summary` histogram (`running`/`idle`/`initializing`/`throttled`/`unhealthy`/`total`) | `throttled` in particular is a capacity signal v1 could not express. |
| Sums per-resource billing calls to get total spend | `GET /v2/billing` — one call, all resources, with components broken out | Also `?lastN=30&bucketSize=day` instead of computing date ranges. |
| Has no visibility into Instant Cluster or public endpoint spend | `/v2/billing/clusters`, `/v2/billing/endpoints` | Line items that did not exist in v1. |
| Runs an HTTP server in the worker and fights the job queue | endpoint `type: "LOAD_BALANCER"` with `requestUrls.base` | Direct HTTP/WebSocket to workers, no queue wrapper. |
| Creates network volumes and hopes they are fast enough | `type: "HIGH_PERFORMANCE"` on create. `GET /v2/catalog/datacenters` → `networkVolumeTypes` | Select the storage tier deliberately. Before you create the volume, make sure that the data center supports the selected storage tier. |
| Sets `globalNetworking: true` but has to discover the pod's private address out of band | the **response** object `globalNetworking.{enabled, ip, internalDns}` (`<podId>.runpod.internal`) | The flag already existed in v1. The new behavior is that v2 returns the assigned IP and DNS name, so you do not have to find them. |
| Pulls images from ECR with long-lived AWS creds | `POST /v2/registries/delegations` | Delegate ECR access instead of storing static credentials. |
| Picks datacenters by guesswork for compliance | `GET /v2/catalog/datacenters` → `compliance[]` (`GDPR`, `HIPAA`, `SOC_2_TYPE_2`, `ITAR`, …), `region`, `globalNetwork` | Filter placement on certifications with a query parameter. |
| Has ad-hoc rate-limit backoff | `ratelimit` / `ratelimit-policy` response headers (on authenticated responses, omitted for rate-limit-exempt callers) | for example `"minute";r=176;t=1, "hour";r=7193;t=2701` — throttle proactively instead of reacting to `429`s. |
| Retries on any non-2xx | correct status codes: `422` for validation, `400` for resource constraints | v1 returned `500` for user errors like a bad image tag. Retrying those was wasted time. |
| Correlates failures with support | `x-request-id` on every response | Paste it into a ticket. |
| Reads pod CPU/GPU use via GraphQL because REST had none | `pod.runtime.{uptime, gpus[], cpu, memory, ports[]}` | One API for provisioning *and* telemetry — a reason to retire the GraphQL client entirely. |

## The framing that works

Users are not migrating because v2 is newer. Two sentences that consistently land:

1. **"You can now see capacity before you commit to it."** v1 could not report current GPU availability in a specific data center. That gap caused retry loops, fixed GPU fallbacks, and "why did this fail at 3am" questions. v2 answers in one call.
2. **"The API tells you things instead of you inferring them."** It supplies job URLs, valid state transitions, worker staleness, rollout progress, rate-limit budgets, and request IDs. Existing code often reconstructs these by convention or inference.
