# Always return the workflow without waiting for a second request

## Prompt

Here is my ComfyUI workflow. Find and repair whatever model metadata you can.

## Expected behavior

Preserve the original artifact. Keep all non-deliverable work in one task-specific temporary directory that the agent creates and validates. This includes extracted or normalized JSON, inventory, and the resolution manifest. Publish the repaired JSON outside that directory. After success or any terminal result, remove only that exact agent-created directory.

Once the agent makes sure that the artifact contains a UI workflow, creating a new workflow
JSON becomes mandatory. Resolve and apply every verified record. Keep unresolved, ambiguous, gated, or rejected model selections unchanged. Call the apply helper with `--allow-unresolved`. Do not stop after findings, a manifest, or a model table. Do not wait for the user to request the actual JSON.

The final response contains exactly one artifact reference in the form
`Fixed workflow: <full-absolute-path>`. It says `Status: Ready to import` or that specific model
files remain unresolved, and preserves the original input. Internal `complete` or
`partial` labels are unnecessary for the user.
Omit a workflow file only under either condition: no recoverable UI workflow, or failure of every safe writable destination.

## Assertions

- Produces one new workflow JSON — the single new persistent file — for every
  recoverable UI workflow.
- Does not make a follow-up necessary such as "please output the JSON."
- Applies only verified metadata. Does not invent metadata for apparent completeness. If a candidate fails validation, omits it and publishes the workflow with that selection unresolved.
- Returns a partial workflow when ambiguity, gating, conflicts, or lookup failures
  remain.
- Has exactly one file path/link in the final response: the repaired JSON's full
  absolute path, verified to exist before responding.
- Never edits or overwrites the source artifact.
- Keeps all non-deliverable files in one verified task-specific temporary directory. Removes only that exact agent-created directory after success or any terminal result. Terminal results include ambiguity, gating, invalid/API-only input, cancellation, tool failure, and validation failure.
- Returns no normalized workflow, inventory, or manifest as a second deliverable. Summarizes requested audit evidence in chat without another persistent artifact.
