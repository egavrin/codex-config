# Hand a repaired workflow to a non-technical ComfyUI user

## Prompt

I do not really understand models or metadata. This old ComfyUI workflow says things are
missing. Please fix it and tell me what to do.

## Expected behavior

Perform the technical work. Do not ask the user to identify models, extract PNG metadata, run commands, understand hashes, or edit JSON. For a recoverable workflow,
it creates exactly one repaired JSON and leads with its full absolute path.

States readiness or the number of unresolved models. Tells the user to drag the JSON into ComfyUI. Explains automatic-download availability in one plain sentence. It may name affected model files. It omits manifests, requirement IDs, directory keys, revision hashes, API routes, command logs, and long source URLs unless requested.

## Assertions

- Uses `Ready to import` or `needs attention` rather than unexplained internal confidence
  labels, and does not imply the workflow has already run.
- Gives one direct next action: drag the JSON into ComfyUI.
- Explains RunpodDirect in plain language and does not imply metadata alone downloads files.
- Does not ask the user to run shell/API commands or edit metadata manually.
- Keeps the default handoff short, with technical details only on request.
- (handoff-contract assertions owned by always-output-workflow.eval.md)
