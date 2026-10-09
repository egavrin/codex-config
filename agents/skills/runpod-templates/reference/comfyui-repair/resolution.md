# Resolve model identity

Use this reference when a workflow names a model but lacks a trustworthy artifact URL,
directory, or hash. The goal is an auditable identity, not merely a downloadable file
with the same basename.

## Evidence to collect first

For each occurrence, retain:

- exact widget/input value and node ID.
- node type, package ID/version when present, and nearby model-family settings.
- workflow title, source URL, notes, and any URLs elsewhere in the JSON.
- existing node `properties.models` and root `models` entries, even if incomplete.
- expected ComfyUI directory inferred from the loader, confirmed against live folder
  keys when available.
- installed same-name files and their hashes when hashing is affordable.

Search the workflow's original publisher/template before general registries. A model
link in the author's documentation or versioned workflow is stronger evidence than an
unrelated exact-filename hit.

## Source order

Use available sources. Delegation to a provider-specific agent or tool is appropriate. It must return evidence, not only a URL.

1. Existing metadata with a valid content hash or a versioned publisher reference.
2. Original workflow/template repository, release, documentation, or accompanying model
   manifest.
3. ComfyUI-Manager's model list for an exact filename and compatible save directory.
4. For Hugging Face candidates, inspect the repository tree for the exact file path. Resolve a commit revision. Record file size and LFS SHA-256 when available. Use a direct artifact URL. Use the live
   [Hub API](https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api)
   rather than a frozen filename catalog.
5. Civitai: prefer exact file-hash lookup. Otherwise compare model version, base model,
   file format, precision, size, and publisher context.

Do not treat Hugging Face repository search as a reliable global filename index. It can
find candidate repositories, after which the exact repository tree must be inspected.
Likewise, an exact basename in ComfyUI-Manager is strong only when its loader/directory
and provenance agree. Common names can still collide.

## Efficient lookup and stopping

Resolve all inventoried filenames as one task. Batch independent provider requests and
prefer provider-native connectors, MCP, or built-in web access over user-visible chains
of shell requests. Start with workflow/publisher context, not a broad mirror census.
Try the best connected provider tool once. If unavailable, make one canonical API fallback for the leading repository. Do not retry several equivalent interfaces.

Reuse repository-tree/API evidence for path, revision, LFS hash, size, access, and license.

Stop the search when a publisher or official source supplies all three items. These are an exact compatible path, immutable revision, and trusted matching SHA-256. Additional byte-identical
mirrors do not improve that identity and usually add latency and licensing noise. Search alternatives only under these conditions: source unavailability, insufficient evidence for `verified`, conflict with graph context, or unresolved ambiguity.

## Confidence policy

| Label | Minimum evidence | Permitted action |
| --- | --- | --- |
| `verified` | Artifact bytes match a trusted SHA-256, or the publisher provides an exact path, pinned revision, and matching trusted hash. | Apply to a new copy when repair was requested. Download without another question only when the opening request included downloading and no new material decision appears. |
| `high` | One exact filename/path match from a credible source, compatible loader/directory and model variant, but no independently trusted content hash. | Do not silently apply. Publish the partial workflow first, then present it for explicit confirmation in the same handoff. |
| `ambiguous` | Two or more credible artifacts fit, or critical variant/precision evidence conflicts. | Publish the partial workflow first, then present a short comparison and ask the user to choose in the same handoff. |
| `unresolved` | Only fuzzy name/family evidence, an HTML/search URL, or no credible artifact. | Do not add downloadable metadata. Publish the partial workflow and state what evidence is missing. |

Hash provenance matters. A digest from the same untrusted download URL detects corruption during future transfers. It does not prove that the artifact is the intended model. Record it as transport integrity, not independent identity evidence.

## Disambiguation checklist

Before declaring a unique match, compare all fields that are relevant to the loader:

- model family and architecture.
- checkpoint versus diffusion model, VAE, text encoder, CLIP, LoRA, ControlNet, or other
  loader class.
- full precision/quantization token (`fp16`, `bf16`, `fp8`, `Q4`, and so on).
- base versus finetune and version/revision.
- file format and exact byte size.
- folder convention and any companion files required by the same workflow.

Names such as `model.safetensors`, `ae.safetensors`, `diffusion_pytorch_model.safetensors`,
and `clip_l.safetensors` are not unique identities. Do not resolve them from basename
alone.

As of 2026-08, RunpodDirect scans `.safetensors`, `.sft`, `.ckpt`, `.pth`, and `.pt`. Upstream has no version tags to pin. Make sure that the format list matches the live extension. The helper reports `.gguf`, `.onnx`, `.engine`, `.tflite`, and `.bin` selections as unsupported warnings. It does not imply that metadata enables RunpodDirect downloads for them. Resolve and place those artifacts
through a separately verified path until the live extension contract supports them.

## Review manifest

The user-facing review should be compact but preserve, per artifact:

| Field | Meaning |
| --- | --- |
| node(s) | Every loader occurrence that will receive or consume the record. |
| name | Exact selected filename. |
| directory | Live ComfyUI folder key such as `checkpoints` or `diffusion_models`. |
| source | Publisher plus provider/repository and revision or version. |
| URL | Direct HTTPS artifact URL, preferably pinned to an immutable revision. |
| SHA-256 | Trusted digest and its provenance, or `not available`. |
| size | Expected bytes when known, useful for storage and cost review. |
| access | Public, gated, license acceptance required, or authentication required. |
| confidence | `verified`, `high`, `ambiguous`, or `unresolved`, with one-line evidence. |
| action | Already installed, add metadata, download if requested/authorized, or a decision is necessary. |

Approval of one candidate does not approve another candidate, a different revision, a
different destination, or installation of supporting custom nodes.

When a valid UI workflow is available, the review is never a substitute for the workflow
file. Finalize and report the complete or partial JSON first, then place any decision
request in that same handoff.

The MVP helper accepts full-commit Hugging Face model-file URLs. It also accepts safe branch/tag URLs when the reviewed record has SHA-256. Numeric Civitai model-version download URLs are also accepted. You may report and download a credible artifact from another host through a separately reviewed method. Do not weaken the helper's host policy. Do not present a page or mirror URL as an automatically safe handoff.
