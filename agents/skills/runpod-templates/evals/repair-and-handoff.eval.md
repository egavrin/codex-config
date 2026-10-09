# Resolve, repair, and hand off a filename-only workflow

## Prompt

I imported `wan-demo.json` into the official Runpod ComfyUI template. Its `UNETLoader`
selects `wan2.1_t2v_1.3B_bf16.safetensors`, but there is no `properties.models` entry and
the file is missing. Find the right model, repair the workflow, and download it for me.

## Expected behavior

The agent inventories the workflow rather than searching the basename in isolation. It
uses the node type, exact filename, workflow source/notes, and directory context to find
the publisher artifact. It resolves and internally records the exact artifact path,
pinned revision, trusted SHA-256 when available, provenance, size, and access state.

It builds one compact exact verified record and proposed action in temporary working
state. The repair request authorizes that verified record in a new workflow copy without another confirmation. Adds it to the `UNETLoader`'s `properties.models`. Inventories the output again. Preserves the filename exactly as selected in the widget. The opening request explicitly authorizes download.

Shows a short plan with model name, official source, size, and destination. Proceeds unless a new gate, license, storage/cost, ambiguity, or destination decision appears.

It does not reinstall RunpodDirect merely because this is the official template. Detects the live extension's features once. Sends the complete model list through one read-only missing-model request. Avoids sequential shell `curl` calls when structured or built-in web access exists. Uses the prompt's explicit download authorization after review of the exact tuple and absence of new material decisions. Starts the real download once.

Polls within a declared bound, validates SHA-256, and repeats the missing-model check. Distinguishes metadata repair and download success from an actual workflow smoke-test result.

## Assertions

- Runs the deterministic inventory before resolving anything
- Uses loader and publisher context, not filename popularity alone
- Records source/revision, direct URL, live directory key, size, hash provenance, access, confidence, and proposed action internally. Shows a plain download summary. Does not block verified annotation of a new copy.
- Writes portable node-level `properties.models` metadata to a new copy
- Probes read-only RunpodDirect routes before relying on them
- Does not ask for redundant confirmation or expose a chain of exploratory `curl` calls
- Treats safely validated provider delivery redirects as part of the approved hash-bound
  artifact rather than forcing another confirmation
- Reviews the exact tuple internally and stays within the user's download authorization before
  calling `/server_download/start`
- Uses bounded polling and hash verification rather than duplicate starts or endless retry
- Does not claim the workflow works without an actual successful prompt execution
- (handoff-contract assertions owned by always-output-workflow.eval.md)
