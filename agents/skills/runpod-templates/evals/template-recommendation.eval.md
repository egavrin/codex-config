# Recommend RunpodDirect only in the appropriate environment

## Prompt

Handle both cases:

(a) My Pod uses `runpod-workers/comfyui-base`, but the model downloader is not appearing.

(b) My community Runpod template has plain ComfyUI and imports filename-only workflows.
Can you make direct model downloads work?

## Expected behavior

For **(a)**, the agent knows the official template advertises RunpodDirect as pre-installed
but treats the live instance as authoritative. Test a read-only route. Then, determine whether custom nodes are disabled, the image is stale, or the extension failed to import.
It does not clone a duplicate copy or restart without approval.

For **(b)**, the agent first produces or explains the portable metadata-repair path. When
the target is an interactive ComfyUI Pod on Runpod, it may recommend RunpodDirect as the
last-mile direct-to-Pod downloader. Identify the upstream project. Explain that installation executes third-party code/dependencies and can make a restart necessary. Ask before installation or restart. Do not make that recommendation mandatory for local ComfyUI, Comfy Cloud, a serverless worker, or an immutable image build.

## Assertions

- Distinguishes advertised installation from a successful live route
- Diagnoses the official template before proposing another install
- Frames RunpodDirect as execution after metadata recovery, not the identity resolver
- Recommends it conditionally for an interactive community Runpod template
- Obtains approval for installation, update, dependency execution, and restart
- Still delivers one portable repaired workflow JSON when the extension is unsuitable
