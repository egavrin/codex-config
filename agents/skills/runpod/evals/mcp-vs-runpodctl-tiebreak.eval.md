# Tie-break: runpod-mcp vs runpodctl on overlapping infra CRUD

## Prompt

The Runpod MCP tools are connected in my session. Two things: (a) list my pods,
and (b) create a pod from my saved template `tmpl-abc` with a CPU flavor. Which
tool for each, and why?

## Expected behavior

Per the capability matrix in `runpod/SKILL.md` (choose by capability first,
environment second):

1. **(a) list pods → runpod-mcp** — a simple structured read, and MCP is connected.
2. **For (b), create a pod from a template with a CPU flavor through runpodctl.** MCP `create-pod` supports `templateId` and `computeType: "CPU"` separately, but not together. Template deployment is GPU-and-v2-only. The combination returns 400.
   `runpodctl pod create --template-id … --compute-type cpu` does it in one call.

   This is the "hand pod creation to runpodctl when it needs a capability MCP lacks"
   rule — note the capability is the *combination*, not either half.

## Assertions

- Routes the **list** to runpod-mcp (MCP connected → prefer it for simple reads/CRUD).
- Selects runpodctl for **template + CPU pod create** because MCP rejects the combination. Does not claim that MCP lacks its existing `templateId` or CPU support.
- Does not blanket-route everything to MCP just because it is connected.
