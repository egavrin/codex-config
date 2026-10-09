# Prefer a prebuilt/known option before building from scratch

## Prompt

Get ComfyUI running on Runpod for me and give me the URL.

## Expected behavior

Per the development loop's "prefer prebuilt" step (`runpod/SKILL.md`,
`runpod-usage/reference/development-loop.md`):

1. First, look for an official prebuilt ComfyUI template/image (`runpodctl template search comfyui` → the Runpod-official `ComfyUI - CUDA 12.8`). Do not immediately git-clone and `pip install` ComfyUI on a bare PyTorch template.
2. It should deploy the pod from that template with the ComfyUI port exposed. It should test the proxy URL through repeated requests (expect startup 502s). It must not report success from "pod Running" alone.
3. Installation from source is permitted only when no suitable prebuilt option exists.

## Assertions

- Searches for / uses a prebuilt ComfyUI template or Hub entry before any from-scratch install.
- Exposes the ComfyUI port at creation and returns a `…proxy.runpod.net` URL.
- Makes sure that the service is ready with a real request through repeated URL polls. Does not rely on a status field.
- Uses git-clone + pip install only after it explains why no prebuilt option fits.
