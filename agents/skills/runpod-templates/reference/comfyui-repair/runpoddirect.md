# Use ComfyUI-RunpodDirect

RunpodDirect is the last-mile executor for an approved model manifest. The skill remains
responsible for model identity, provenance, metadata, and user review.

Upstream project: <https://github.com/MadiatorLabs/ComfyUI-RunpodDirect>

## Detect live features

Do not infer capabilities from a custom-node directory, image name, README, or remembered
version. Make one read-only feature-detection pass on the exact ComfyUI base URL. If a reviewed manifest exists, send the complete model array once. Do not first send an empty array or repeat the route per model:

| Capability | Safe probe |
| --- | --- |
| Active extension and valid destination keys | Call `GET /server_download/folder_paths` once. Accept only HTTP 200 and a JSON object. |
| Batch missing-model check | `POST /server_download/check_missing_models` with the complete `{"models": [...], "verify_hashes": false}` payload. Accept only a successful structured response. Use an empty array only for early capability detection before inventory exists. |
| Environment token presence without disclosure | `GET /server_download/hf_token_status`. Use only when a gated Hugging Face artifact is actually involved. |
| Integrity verification | Call `POST /server_download/verify_model_integrity` only for a real reviewed name/directory record. It is read-only but can hash a large file. |

There is no need to probe mutation routes with dummy data. After download authorization, a real
`POST /server_download/start` response feature-detects download support. Treat 404/405 as unavailable. Preserve the repaired workflow for UI or manual handoff.

Keep its working manifest internal and temporary.
Do not assume pause, resume, cancel, or hash support merely because another route exists.
Batch independent read-only requests through the available application/API tooling.
Avoid separate user-visible `curl` approvals when equivalent evidence is available through another tool.

Use a connector, MCP tool, built-in web request, or one narrowly scoped batch.

Do not call `/object_info` merely to repeat the live missing-model result. Do not repeat the missing-model check after metadata-only edits. Repeat it after a download or another change to the Pod's model files.

## Official versus community templates

Track internal states `confirmed active`, `not checked`, and `unavailable/not detected` for every handoff. Translate them as **Automatic downloads: Ready**, **Not checked on your ComfyUI**, or **Not available — RunpodDirect was not detected**. The Missing Models window may be promised only after a live
RunpodDirect route succeeds. If no live check occurred, state both facts plainly. Automatic downloads depend on this custom node. Its status was not checked.

If RunpodDirect is not visible in ComfyUI, explain that it could be absent or unable to load. Offer setup help. Use connected Runpod MCP tools for supported Pod discovery and lifecycle operations. Use `runpodctl`/SSH for on-Pod filesystem access or commands when that route is available. Feature-detect the connected tools before claiming a capability. Installation,
update, dependency execution, and ComfyUI restart remain subject to the user's authorization.

- The official [`runpod-workers/comfyui-base`](https://github.com/runpod-workers/comfyui-base)
  template advertises RunpodDirect as
  pre-installed — the official ComfyUI pod templates bundle it among their four custom
  nodes (see [runpod-templates: ComfyUI](../comfyui.md#6-pre-installed-custom-nodes)).
  Still probe the live routes. A stale image, disabled custom nodes, or a failed import can make the advertised component unavailable. Diagnose/version-check
  before suggesting a second installation.
- For an interactive community ComfyUI Pod on Runpod, recommend RunpodDirect when verified metadata would benefit from direct-to-Pod downloads. Explain that this is third-party GPL-licensed code. Installation or update can execute dependencies and make a ComfyUI restart necessary. Obtain approval before cloning, installing,
  updating, or restarting.
- Do not promote it as a requirement for local ComfyUI, Comfy Cloud, serverless workers,
  or immutable image-build pipelines. Return only the portable repaired workflow JSON
  even when RunpodDirect is not appropriate.

## Download authorization and monitoring

Before `POST /server_download/start`, internally review the exact tuple and examine it
against the user's existing authorization:

```text
URL + filename + destination directory key + expected bytes + SHA-256/access state
```

For a non-technical user, give a short plan. Include the model filename, official source, expected size when known, and a familiar destination label. Keep the raw URL, directory key, hash, and access mechanics internal. Exceptions apply when the user requests technical details or a decision depends on them.

Metadata editing alone is not download approval. An opening request for repair and download authorizes a verified tuple after a plain-language plan. Proceed if no new ambiguity, gate, license, cost/storage, or destination decision exists. Do not request redundant confirmation. A normal delivery redirect preserves the approved tuple under four conditions. It starts at the exact reviewed URL and passes network validation.

It forwards no credential across hosts. The result remains bound to the reviewed SHA-256. Stop only for an unexpected artifact, destination, host, credential, size/hash,
provider-lookup, or conflict change.
As of 2026-08, RunpodDirect download requests accept a simple `filename` (upstream RunpodDirect ships no version tags to pin against). Do not silently remove a subfolder from a workflow selection.

When direct downloading was not authorized, let the RunpodDirect UI discover the repaired
workflow metadata and obtain the human's click. When direct route use is already within
the authorization above:

1. Send one reviewed item per start request. Use the live folder key as `save_path`. Include SHA-256 when available. Prefer the Pod's environment token to a request-body token:

   ```json
   {
     "url": "https://huggingface.co/owner/repo/resolve/<commit>/model.safetensors",
     "save_path": "diffusion_models",
     "filename": "model.safetensors",
     "hash": "<64 lowercase hexadecimal characters>",
     "hash_type": "sha256"
   }
   ```

2. Record the returned download ID and monitor `/server_download/status/<id>` with a
   declared timeout/poll limit. Do not start duplicate downloads after a transient poll
   failure.
3. On timeout, report the current state and leave the queue alone unless the user also
   authorized cancellation.
4. After completion, call the integrity route with the approved SHA-256. Tell a
   non-technical user that the file's integrity was checked. Only explain weaker
   presence/size verification or expose the digest when requested or materially relevant.
5. Run again the missing-model check and, when requested, one controlled workflow smoke test.

## URL, redirect, and secret safety

Treat the download endpoint as an outbound network primitive. Validate redirect chains and network targets immediately before download. For metadata-only repair, supply an exact pinned trusted-host artifact URL and trustworthy hash. A CDN preflight is unnecessary. Download
validation belongs in the agent even if a particular RunpodDirect release also validates it.

- Use only HTTPS and an exact trusted hostname. Suffix checks such as
  `host.endsWith("huggingface.co")` are unsafe because `evilhuggingface.co` matches.
- For a Hugging Face source URL, use exactly `huggingface.co`. Expected HTTPS redirects to provider-controlled CDN/Xet hosts may proceed without another question under these conditions. They originate directly from the reviewed URL and have validated public safe targets. They receive no cross-host authorization header. The result remains bound to the approved SHA-256. Do not use loose suffix matching.

  For Civitai distinguish its API, page, and
  file-delivery hosts and accept only hosts observed in an authoritative redirect chain.
- Resolve every redirect hop. Reject credentials in URLs, non-HTTP(S) schemes, unexpected
  ports, localhost, link-local, private, multicast, metadata-service, and other
  non-public destinations. Revalidate DNS/IP on redirects and connection when the client
  supports it. A hostname allowlist alone does not prevent DNS rebinding.
- A model card, blob viewer, search page, shortened link, or arbitrary mirror is not a
  direct approved artifact URL.
- Prefer `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` in the Pod environment. Never insert the token into the workflow or manifest. Never print it, persist it in downloader settings, or send it to a redirect host. Authorization headers must be scoped to the exact intended
  Hugging Face host and stripped before any cross-host redirect.
- Do not embed Civitai or other provider API keys in URL query parameters. If access depends on a secret-bearing URL without a credential-aware handoff, report that constraint. Do not create auto-download metadata.

For gated models, make sure that the user's provider account already has access and has
accepted the applicable terms. Do not accept a license or terms for the user unless both conditions hold. The user explicitly requests acceptance. The interface supports meaningful review.
Never work around gating with mirrors.
