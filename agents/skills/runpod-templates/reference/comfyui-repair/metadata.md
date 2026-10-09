# Apply ComfyUI model metadata

Use this reference after identity resolution. A repair request authorizes `verified` records in a new copy. A separate confirmation is necessary only for a material choice. Examples include a `high`-confidence candidate or conflict replacement. Never
edit or overwrite the source. Preserve graph behavior and make the repaired workflow
independently useful.

Pending confirmation must not delay the mandatory workflow handoff. Omit that record and publish the partial workflow. Ask after the path in the same response.
Use the current Comfy
[workflow-template specification](https://github.com/Comfy-Org/workflow_templates/blob/main/docs/SPEC.md#model-metadata-format)
and [embedding guide](https://github.com/Comfy-Org/workflow_templates#9--embed-models)
as the authoritative metadata convention.

## UI workflow versus API prompt

Portable model metadata belongs to UI-format workflow JSON. API-format prompt JSON is
useful for inventory because its named inputs make model references easy to locate, but
it has no equivalent portable model-metadata contract. For API-only input, keep any reviewed resolution plan as temporary working state. If annotation is required, ask for the original UI workflow. Do not deliver the manifest as a substitute. Do not add `properties.models` to API nodes and claim that the prompt is repaired.

## Canonical node record

Attach model metadata to the consuming loader node's `properties.models` array:

```json
{
  "name": "flux1-dev.safetensors",
  "url": "https://huggingface.co/owner/repo/resolve/<commit>/diffusion_models/flux1-dev.safetensors",
  "hash": "<64 lowercase hexadecimal SHA-256 characters>",
  "hash_type": "SHA256",
  "directory": "diffusion_models"
}
```

The portable ComfyUI workflow-template convention is node-level
`properties.models`. RunpodDirect can also read a root `workflow.models` collection. Do not use that extension to omit a known node association. Use a root record only as an additional compatibility/fallback record when the node association cannot be represented reliably. Remove duplicates by exact name and URL.

Use the runtime directory key, not an absolute path. Never invent a key. Never convert a key such as `diffusion_models` into an arbitrary filesystem path. As of
2026-08, RunpodDirect requests use keys such as `checkpoints`, `diffusion_models`,
`vae`, or `text_encoders`, while some documentation displays them as
`models/checkpoints` paths. Find all accepted keys with one
`GET /server_download/folder_paths` call when a live instance is available.

## Resolution manifest consumed by the script

Start with `workflow_sha256` and `requirement_id` values from
`inventory_workflow_models.py`. Do not recalculate or invent identifiers:

```json
{
  "schema_version": 1,
  "workflow_sha256": "<value from inventory>",
  "models": [
    {
      "requirement_id": "<value from inventory>",
      "filename": "flux1-dev.safetensors",
      "directory": "diffusion_models",
      "url": "https://huggingface.co/owner/repo/resolve/<40-character-commit>/diffusion_models/flux1-dev.safetensors",
      "sha256": "<optional 64-character digest>",
      "expected_size": 2389012345,
      "source": {"provider": "huggingface", "repository": "owner/repo", "revision": "<commit>"},
      "license": "<SPDX id, provider value, or unknown>",
      "access": "public",
      "reviewed": true,
      "verified": true,
      "ambiguous": false,
      "replace_existing": false
    }
  ]
}
```

`workflow_sha256` is a canonical semantic fingerprint of the parsed JSON, not the
bytewise SHA-256 of the source file. Whitespace and object-key order therefore do not
invalidate a reviewed manifest, while any data change does.

`reviewed` means that the identity/action was compared with evidence and the existing request scope. A verified new-copy repair does not make a separate conversation round trip necessary. `verified` identifies one exact artifact through trusted evidence or explicit user selection among exact candidates. It does not mean that the file bytes passed hash validation.
Only `sha256` carries that integrity claim. Never set these booleans merely to satisfy the
script.

Leave ambiguous/unresolved requirements out and report them. For the mandatory handoff, use explicit `--allow-unresolved` mode. The apply script preserves loader selections and reports `partial`. Do not invent metadata.

The apply helper validates fields that affect workflow metadata and leaves provenance,
size, license, and access fields in the separate review manifest as audit evidence.
Set `replace_existing` to `true` only after reviewing the reported field-level conflict
for that requirement. Omit it, or leave it `false`, when adding metadata or preserving an
identical existing record.

The helper scripts use only the standard library. Run them with python3 >= 3.9.

## Patch rules

1. Always write a new output file. Never edit, replace, or overwrite the supplied JSON or
   PNG. Prefer `<workflow-stem>.repaired.json`. If it already exists, choose a
   collision-safe numbered filename rather than overwriting it.
2. Preserve node IDs, links, widget values, layout, subgraphs, unknown fields, JSON types,
   and existing object-key order. The helper reserializes the workflow with indentation, so whitespace and inline-array formatting can change. Review semantic changes instead of expecting the smallest possible byte diff.
3. Attach each record to its identified consuming loader, including loaders in nested
   subgraphs. Requirement identifiers are occurrence-specific: do not attach by filename
   alone when different nodes select same-name but different artifacts.
4. Make `name`, direct `url`, and `directory` mandatory. Add `hash` and `hash_type` when a
   trustworthy SHA-256 is available. Do not invent a digest or hash algorithm.
5. Keep `name` identical to the selected widget/input filename. A URL whose response is
   renamed by `Content-Disposition` does not justify changing the workflow silently.
   If a selected value contains a subfolder, do not reduce it to a basename. As of 2026-08, RunpodDirect accepts only a simple filename for download. Upstream has no version tags to pin.

   Report manual placement for that requirement instead of misleading metadata.
6. Reject URL fragments, credentials in URLs, local paths, and path-traversal filenames. Reject metadata whose directory is not accepted by the live instance. For new repair metadata, validate the exact pinned trusted-host URL and hash. Do not follow delivery-CDN redirects at this stage. Validate redirects at the download boundary ([runpoddirect.md](runpoddirect.md)).
7. If an existing record conflicts with the approved record, surface the diff. The helper refuses replacement until the manifest item explicitly has `"replace_existing": true`. Do not set it merely because a newly found source is more popular. When confirmation is still needed, omit the replacement, publish the
   partial workflow first, and ask in the same handoff.
8. Keep an existing record unchanged when its canonical fields already match. Preserve unknown fields such as `note` or `size`. Do not rewrite it merely to pin a revision or add a hash. Harden existing complete metadata
   only when the user asks for verification/hardening or a live failure exposes a
   problem.
9. The helper never silently keeps an unsafe existing entry. Without `--allow-unresolved`, publication fails with exit 2. With the flag, the published workflow omits that entry and reports it as unresolved. The loader selection remains unchanged. It likewise removes known invalid
   metadata that has no approved replacement while preserving the selection.
10. Re-inventory the candidate before publishing the final path. The apply helper
    performs this check in memory and refuses invalid or API-only output. In explicit `--allow-unresolved` handoff mode, it publishes a valid UI workflow with unresolved selections preserved.

    It labels that result `partial`. Otherwise, it refuses unresolved output. `complete` means the approved metadata is structurally present and
    correctly associated. It does not certify that the workflow runs.

    Runtime and
    artifact verification are separate steps.
11. For metadata added during a repair, prefer a pinned repository revision plus
    SHA-256. `main`, a search-result URL, a model card, or an HTML page is not an
    immutable artifact identity.
12. Treat `.safetensors`, `.sft`, `.ckpt`, `.pth`, and `.pt` as the supported model formats. This is the RunpodDirect scanner contract as of 2026-08 (upstream RunpodDirect ships no version tags to pin against). Report other model formats for
    a separately verified placement path.

`unsafe_url` marks unsafe existing metadata URLs. Reasons include non-HTTPS, an IP-literal host, userinfo, a fragment, or credential-shaped query keys. The normalized host must be exactly `huggingface.co` or `civitai.com`. An entry flagged `unsafe_url` makes `metadata_status`
`partial`, never `complete`.

An inventory summary of `complete_metadata` means structurally complete metadata, not
that the live folder exists, the bytes match, access is granted, or the workflow executed.

## What to deliver

The workflow file is mandatory. For completion, write exactly one new persistent `<workflow-stem>.repaired.json` or collision-safe numbered variant. This applies after added records, an already-complete workflow, or unresolved requirements.

For a recoverable UI workflow, use this order and keep it brief:

1. `Fixed workflow: <full-absolute-path>` as the only file reference. Make that same
   path clickable when supported and show no other artifact path.
2. `Status: Ready to import` when all supported model references are covered, or
   `Status: Workflow file created — <count> model(s) still need attention` when partial.
   Never imply everything is fixed when some model information remains missing.
3. `Next: Drag this JSON into ComfyUI.`
4. Exactly one automatic-download status, followed by one plain sentence explaining what
   it means: `Automatic downloads: Ready`, `Automatic downloads: Not checked on your
   ComfyUI`, or `Automatic downloads: Not available — RunpodDirect was not detected`.
5. State plainly whether model files were downloaded and whether the workflow was run.

The three automatic-download states:

- **Confirmed active** → `Automatic downloads: Ready`. Tell the user to drag the
  actionable JSON into ComfyUI. The RunpodDirect Missing Models window should appear. If
  it does not, refresh ComfyUI and import the JSON again.
- **Not checked** → `Automatic downloads: Not checked on your ComfyUI`. Say that
  Automatic direct-to-Pod download depends on
  [ComfyUI-RunpodDirect](https://github.com/MadiatorLabs/ComfyUI-RunpodDirect) and that
  its installation/load status was not verified. Do not promise that the Missing Models
  window will appear.
- **Unavailable or not detected** → `Automatic downloads: Not available — RunpodDirect
  was not detected`. Say the workflow file is ready, but automatic download depends on
  RunpodDirect to be installed, enabled, and loaded. Offer setup help. Do not install,
  update, or restart ComfyUI without authorization.

Compatible metadata does not prove extension availability. Without active RunpodDirect, the enriched workflow remains portable. It does not create the Missing Models UI or download directly to the Pod.

After a repair, summarize how many models received download information and, when the
list is short, name them. When the workflow already had complete metadata, say the final
copy is unchanged and no records were added. If attention is needed, list the affected
model filenames and the human decision in plain language after the file path. Show the
technical `Model | Directory | Source URL | SHA-256` table only when the user asks for
technical details, provenance, or an audit. After lookup failure, ambiguity, a gate, conflict, or rejected metadata, still return a partial or unchanged workflow JSON. Omit final output only if no UI workflow is recoverable or every writable collision-safe destination fails.

After a JSON patch alone, do not say "the workflow works". Use "metadata repaired" until artifact verification completes and an actual workflow execution succeeds.

Assume a non-technical audience by default. Translate internal states into user language. Avoid manifest, requirement ID, immutable revision, directory key, artifact tuple, UI-format detection, `verified`, `high`, `ambiguous`, `unresolved`, and re-inventory. If a decision depends on one of these terms, add a short explanation. Do
not include helper commands, API routes, shell transcripts, long URLs, or hashes unless
the user requests technical evidence. Do not ask the user to run extraction, `curl`, API,
or metadata-editing commands.

Keep safety checks rigorous internally. Offer deeper
technical evidence only when requested.

Preserve the original artifact without editing or overwriting it. Keep extracted/normalized JSON, inventories, and review manifests in one uniquely named task directory under the system temporary directory. Never put them beside the source or final file.
After the repaired JSON passes another inventory, remove the exact agent-created directory. Never remove the source or final file. Never recursively delete a broad or unverified path.

Use finally-style cleanup on every terminal path, including ambiguity,
gating, invalid/API-only input, cancellation, tool errors, and failed validation. Omit temporary paths from the final response. Do not attach, link, or enumerate them. Show the final repaired JSON's full absolute path as the one mandatory path. Do not
generate a second persistent audit artifact. Summarize requested audit evidence in chat.

If the task also creates or starts a Pod, first consult the [worked examples](../../../runpod/golden-paths/README.md). Route that infrastructure work through `runpod-mcp` or `runpodctl`. Return here once ComfyUI is reachable.
