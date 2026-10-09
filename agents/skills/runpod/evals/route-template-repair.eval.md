# Route a broken ComfyUI workflow to the templates hub, then its repair guide

## Prompt

I imported this community ComfyUI workflow on my Runpod Pod. It references
`flux_example.safetensors`, but the workflow contains no model URL, so the
missing-model dialog cannot download it. Find the correct model and make the
workflow usable.

## Expected behavior

First, select `runpod-templates`, the index for official templates and their repairs. Then, select infrastructure tools or generic Hugging Face download tools.
The hub selects its model-repair guide (`reference/comfyui-model-repair.md`). The guide inventories the workflow, resolves trustworthy model metadata, and reviews it. After approval, it writes a separate annotated workflow. It uses feature-detected ComfyUI-RunpodDirect routes only after download approval.

## Assertions

- Routes missing or incomplete ComfyUI workflow model metadata to
  `runpod-templates`, whose model-repair guide owns the repair procedure.
- Do not repair the workflow within the router. The template index owns the onward route to its repair guide.
- Does not treat a bare filename as a verified model identity.
- Does not select `companion-clis` merely because Hugging Face is a possible search provider. That workflow serves a known repository/file or an artifact task outside workflow repair.
- Does not provision or mutate Pod infrastructure unless the user separately asks.
- Reviews the plan internally before writing the annotated workflow copy.
- Obtains explicit user approval before any model download or Pod mutation.
