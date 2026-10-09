# When to use the MCP lane (and when to defer)

## Prompt

The Runpod MCP tools are connected. I need to: (1) list my serverless endpoints,
(2) deploy a vLLM worker from the Runpod Hub, and (3) grab a pod's recent logs.
Handle each.

## Expected behavior

Per `runpod-mcp/SKILL.md` for the lane choice, and the connected server's own tool
list for the tool names (the skill deliberately keeps no copy of them):

1. **(1) list endpoints → runpod-mcp** — a structured read the server exposes. MCP
   is connected, so prefer it.
2. For (2), deploy from Hub through runpod-mcp. `list-hub-repos` finds the repository. `deploy-hub-repo` deploys its listed release as an endpoint. Connected MCP supports this directly.
3. **(3) pod logs → runpod-mcp** — the server exposes pod log streaming. A
   structured read is a good fit.

## Assertions

- Routes the endpoint **list** and the **pod logs** to runpod-mcp (connected → structured reads).
- Routes the **Hub deploy** to runpod-mcp via `deploy-hub-repo` (optionally `list-hub-repos` first).
- Do not claim that MCP lacks Hub tools. When MCP is connected, do not change to runpodctl for the Hub deployment.
- Gets tool names from the connected server, not a duplicated skill list. Examines the tool list before any claim that a tool is absent.
