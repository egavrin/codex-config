# Verify readiness with a real request — "up" ≠ "ready"

## Prompt

I started a web server on my Runpod pod and `runpodctl pod get` says it's RUNNING,
but requests to the proxy URL are failing. Is it broken? How should I confirm it's
actually ready?

## Expected behavior

Per `runpod-usage/reference/development-loop.md` (step 6) + `pod-workflows.md`:

1. The agent should explain that **"RUNNING" means the container exists**. It does not mean the service accepts requests. The proxy commonly returns **502 for ~30–60s** during initialization. Requests that fail immediately after boot are expected during this interval.
2. The agent should make sure that the service is ready through real requests to the proxy URL (for example `until curl -sf https://<pod-id>-<port>.proxy.runpod.net/<health>; do sleep 5; done`). It should use a timeout. It should not trust only the status field.
3. If the service stays unavailable, examine the likely causes. The service is not bound to `0.0.0.0`, or it stopped because it lacked detachment (`setsid`).

## Assertions

- States that RUNNING/ready is not the same as serving. Expects a warm-up 502 window.
- Recommends polling a real request against the proxy URL to make sure that the service is ready.
- Mentions the `0.0.0.0` bind and/or detached-start (`setsid`) as the usual culprits if it stays down.
- Does not conclude "it's broken" from the RUNNING status alone.
