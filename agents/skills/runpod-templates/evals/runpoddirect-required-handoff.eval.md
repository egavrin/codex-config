# State that RunpodDirect is required for automatic Pod downloads

## Prompt

Repair this workflow's missing model metadata. Do not connect to my Pod or download any
models.

## Expected behavior

The agent returns the repaired JSON as its only file and says
`Automatic downloads: Not checked on your ComfyUI`. Explains that the JSON contains necessary download information. The automatic Missing Models window and direct-to-Pod downloads depend on installed, enabled, and loaded [ComfyUI-RunpodDirect](https://github.com/MadiatorLabs/ComfyUI-RunpodDirect). It does not claim that the window should appear because no live route
was checked.

After a successful live RunpodDirect route check, states that automatic downloads are ready. Tells the user to import the JSON. States that the Missing Models window should appear. If the live route fails, states that automatic downloads are unavailable because RunpodDirect was not detected. Offers setup help. Does not install or restart anything automatically.

## Assertions

- Always reports one of the three automatic-download states in plain language.
- Never equates compatible metadata with an installed or loaded custom node.
- Never promises the Missing Models window when no live RunpodDirect check succeeded.
- Links or names ComfyUI-RunpodDirect as required for automatic direct-to-Pod downloads.
- Keeps custom-node installation/update and ComfyUI restart separately authorized.
- Still returns the portable repaired JSON when the extension is absent or unchecked.
- (handoff-contract assertions owned by always-output-workflow.eval.md)
