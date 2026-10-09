---
name: runpod-mcp
description: "Manage Runpod infrastructure through structured Runpod MCP server calls. Scope includes pods, serverless endpoints, jobs, templates, network volumes, container-registry authentication, GPU/CPU catalog, and billing. Use when Runpod MCP tools (create-pod, list-endpoints, …) are connected, or to connect them through hosted OAuth or local npx. When MCP is available, prefer this skill to runpodctl for ordinary infrastructure CRUD. Use runpodctl for terminal work, file transfer, or SSH setup. This skill owns only the connection workflow. Read the server tools and task playbooks for operations."
allowed-tools: Bash(claude mcp:*)
metadata:
  compatibility: Linux, macOS, Windows
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Runpod MCP

The Runpod MCP server exposes Runpod's control plane as structured tool calls,
so an MCP-capable agent can manage infrastructure without shelling out. It is the
same Runpod REST API that `runpodctl` uses — pick MCP when its tools are
connected (typed parameters, structured errors, no shell quoting).

**For a multi-step job, read the worked example before tool calls.** Correct calls can still occur in the wrong order. Read verified end-to-end sequences in [runpod/golden-paths/README.md](../runpod/golden-paths/README.md) (image → template → endpoint, pod → volume → serverless, multi-region, autoscaling, monitoring).
They are how the job was done before, costs included. The server's own resources cover
procedure within one journey. The paths cover what order to do a whole job in.

**This skill covers connection and workflow selection only.** Read the connected server for tool definitions and accepted inputs. See [The server is the source of truth](#the-server-is-the-source-of-truth). The server releases weekly. A duplicated tool list here would become stale and still appear authoritative. Thus, the server retains those definitions.

## Connect

If you also use runpodctl/flash, connect the hosted server with **your API key as a Bearer header**. The same key authenticates MCP and the CLIs (the 80% path):

```bash
claude mcp add --transport http runpod -s user https://mcp.getrunpod.io/ \
  --header "Authorization: Bearer $RUNPOD_API_KEY"
```

Plain **OAuth** ("Sign in with Runpod", via `npx @runpod/mcp-server@latest add`) is MCP-only — the CLIs stay unauthed, so use it only for MCP-only work. Local **stdio** runs the server as a subprocess with your key. Those variants + the key-vs-OAuth tradeoff: **[reference/connect.md](reference/connect.md)**. After connecting, reconnect the client (in Claude Code, `/mcp`) so the tools load.

Before relying on MCP, make sure that it is live. In Claude Code, run `/mcp`. `runpod` should show Connected, not Needs authentication. If it shows Needs authentication, sign in there first.

The bundled plugin server registers the URL but stays inert until you authenticate. Make sure that a real call works by asking for `list-endpoints`.
If no `runpod` tools are present, the server is disconnected. Repeat the installation above or use **runpodctl** for this task.

**Examine the server version (which REST API it drives):** the MCP `initialize` handshake
returns it in `serverInfo.version`. `/mcp` in Claude Code shows it, or probe the hosted
server directly:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
| curl -s -X POST https://mcp.getrunpod.io/ \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "Authorization: Bearer $RUNPOD_API_KEY" -d @-
```

## The server is the source of truth

Once connected, read the server — do not reason about its tools from memory or from
this file.

1. **The tool list and every parameter** come from the client's own view of the
   connected server: `/mcp` in Claude Code, or `tools/list`. Each tool carries its
   own parameter descriptions, generated from Runpod's REST v2 contract. Examine the live schema before you state that a capability exists or is absent. Documentation-based absence claims become stale silently.
2. **The server also supplies task playbooks.** It publishes MCP resources under `runpod://skills/`, with a router at `runpod://skills/runpod`. Task-specific skills cover serverless deploys, pod diagnosis, endpoint operations, cost audits, catalog discovery, and API-boundary honesty. Enumerate them with `resources/list` and
   read the routed one before a multi-step job. They are versioned with the server, so
   they describe the tools you actually have.
3. **The wire contract** is the Runpod v2 OpenAPI document at
   `https://api.runpod.io/v2/openapi.json`, for fields beyond the tool surface.

Resource coverage includes pods, serverless endpoints, workers, jobs, Hub browse/deploy, and public pay-per-use endpoints. It also includes templates, network volumes, and container-registry authentication (including AWS ECR delegations). The GPU/CPU/data-center catalog and billing are also included. Use this resource-level list only to decide whether the workflow applies.

Log streaming for pods, workers, and jobs is included. Read finer details from the live schema. These include accepted creation fields, immutable tiers, and deletion results.

Delete tools can return `isError: true` with "Unexpected end of JSON input" **even after success**. The REST API returns 204 No Content. This protocol behavior can resemble a defect. Make sure that deletion succeeded with a follow-up `get-`/`list-` (a deleted resource
then 404s) rather than retrying the delete.

For concepts (pods vs serverless, GPU selection, storage), read `../runpod-usage/`.
For whole multi-resource jobs, read the golden paths linked at the top of this skill.

## Use MCP vs runpodctl

- Use runpod-mcp when its tools are connected and expose the infrastructure CRUD operation or serverless job call. Cap large job/log output to a file.
- **Use runpodctl instead** for `send`/`receive` file transfer, SSH key management, `doctor` setup, or model cache. Also use it for a shell-only agent or a user-requested reproducible command.
- Use runpodctl for pod creation with a multi-GPU priority list. v2 `create-pod` takes one GPU type. Examine the live schema and watch for a `_warning` on an otherwise successful create. Also use runpodctl for a template and CPU pod together, which v2 cannot express. Each alone is fine in MCP: `templateId` (each field you pass
  replaces the template's whole value rather than merging) or `computeType: "CPU"`.
- **Not this lane:** writing/deploying your own Python (→ flash). Downloading
  models or building/pushing images (→ companion-clis).

## Source & docs

- Server source: https://github.com/runpod/runpod-mcp
- Package (npm): https://www.npmjs.com/package/@runpod/mcp-server
- Hosted endpoint: https://mcp.getrunpod.io/
- Documentation: https://docs.runpod.io

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
