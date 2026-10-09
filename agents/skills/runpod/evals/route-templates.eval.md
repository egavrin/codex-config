# Route "run X on a pod" to the templates lane when an official template covers it

## Prompt

I want ComfyUI running on a Runpod pod with a web UI I can open in my browser.
Set it up for me.

## Expected behavior

The router maps "run a common workload on a pod" to `runpod-templates`. An official prebuilt template covers ComfyUI. The agent deploys that template through the matching golden path instead of a custom image build.
Fixing an already-running template pod also lands in `runpod-templates` first,
which routes onward.

## Assertions

- Route "run ComfyUI on a pod" to `runpod-templates` and its ComfyUI reference / golden path 02 variant B. Do not build a custom image through docker/companion-clis for that request.
- Distinguishes pod templates from Hub serverless repositories. When the user asks for a pod, it does not answer with the `worker-comfyui` Hub listing.
- For an official-template "my pod is Running but the URL 502s" task, first use `runpod-templates` (the reference's Readiness section). If the cause is independent of the template, continue to runpod-usage known problems.
- For an imported ComfyUI workflow with missing model metadata, use the templates skill's model-repair guide. Do not improvise repairs.
