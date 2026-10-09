# Golden path 01 — Ollama server on a pod + access URL

**Goal:** Process "stand up an Ollama server on Runpod and give me the URL". Provision a GPU pod. Install and start Ollama. Pull a model and return a working HTTPS API URL. Keep model data on persistent storage.

**Status:** COVERED — live-verified 2026-07-07
**Lane(s):** runpodctl (pod) + SSH

Grounded in the official tutorial `docs/tutorials/pods/run-ollama.mdx` and the
reusable pod loop in [`../../runpod-usage/reference/pod-workflows.md`](../../runpod-usage/reference/pod-workflows.md).

## When to use this (and why a pod, not serverless)

Ollama is a **long-lived HTTP server you keep open and talk to interactively**
(`/api/generate`, `/api/chat`, `/api/tags`). That is the classic pod shape: a
service reached at a proxy URL, not a request/response job that should scale to
zero. See the workload-shape decision in
[`../../runpod-usage/reference/development-loop.md`](../../runpod-usage/reference/development-loop.md).

Use a **pod** here because:

- You want a persistent server behind one stable URL, not per-request cold starts.
- You iterate against it (pull more models, chat repeatedly) over its lifetime.
- Model weights live on a **network volume** so pulls happen once and survive
  restarts.

Reach for **serverless** instead only if you truly want a scale-to-zero
request/response inference API (that is golden path 03, Whisper) — different lane,
`endpoint-workflows.md`.

This path uses the **runpodctl** lane: it exposes every necessary flag
(`--ports`, `--env`, `--network-volume-id`, `--terminate-after`) and gives a
non-interactive SSH channel to run install commands. MCP's `create-pod` can also
set ports/env, but runpodctl is preferred for a template lookup and SSH
exec in one lane (see the router).

## Prerequisites

| Need | How |
| --- | --- |
| **Auth** (non-interactive) | `export RUNPOD_API_KEY=your_key` — runpodctl reads it. `runpodctl doctor` is the interactive human first-run (also sets up SSH keys). |
| **runpodctl** installed | `curl -sSL https://cli.runpod.net \| bash` (see [`../../runpodctl/SKILL.md`](../../runpodctl/SKILL.md)). |
| **An SSH key** registered | `runpodctl doctor` or `runpodctl ssh add-key`, needed so the agent can exec on the pod. |
| **A GPU + a co-located DC** | `runpodctl datacenter list` shows per-DC GPU availability — pick a DC that has your GPU *and* will hold the volume. |

Resolve auth **before any API call**. If human action is necessary for a step (OAuth, quota increase, payment), stop and state the exact blocked action. Do not report false progress.

## Walkthrough

Each step lists the real command and why it matters. Do them in order. Each
depends on the previous.

### 0. Auth

```bash
export RUNPOD_API_KEY=your_key     # non-interactive; runpodctl reads this
# (humans can run `runpodctl doctor` for interactive setup + SSH keys)
```

*Resolves auth once for the whole flow.*

### 1. Create a network volume for the models (default: persistent)

```bash
runpodctl datacenter list          # per-DC GPU availability → pick a DC
runpodctl network-volume create --name ollama-models --size 30 --data-center-id <dc>
#   → note the volume id (it lives in <dc>; the pod MUST go in the same <dc>)
```

*Model weights are large and slow to pull. Put them on a network volume so they
persist across stop/restart and are not re-downloaded (see
[`../../runpod-usage/reference/storage.md`](../../runpod-usage/reference/storage.md),
"prefer a network volume by default"). The volume is **DC-locked** — the pod has
to be created in the same data center or scheduling fails.*

### 2. Create the pod — ports + env + volume set AT creation

```bash
runpodctl template search pytorch          # find the official PyTorch template id

runpodctl pod create \
  --name ollama \
  --template-id <runpod-pytorch-template-id> \
  --gpu-id "<cheap available gpu>" \
  --ports "11434/http,22/tcp" \
  --env '{"OLLAMA_HOST":"0.0.0.0","OLLAMA_MODELS":"/workspace/ollama"}' \
  --network-volume-id <volume-id> \
  --volume-mount-path /workspace \
  --terminate-after <iso8601 a few hours out>   # cost guard: TERMINATES (not --stop-after)
```

*All service prerequisites are now in the configuration. **Reset a running pod before you add ports or environment settings.** Declare `11434/http` for the Ollama API and `22/tcp` for SSH at creation. `OLLAMA_MODELS` points
pulls at the volume mount. `--terminate-after` deletes the pod at the given time
(`--stop-after` only stops it and keeps billing disk/volume). Live run used an
**RTX 4090**.*

### 3. Wait for the pod, then get the SSH connection

```bash
runpodctl pod get <pod-id>                 # poll until it is running
runpodctl ssh info <pod-id>                # prints the ssh command + key (does NOT connect)
```

*`ssh info` returns connection details, not an interactive session — the agent
execs commands remotely via `ssh user@host 'command'`.*

### 4. Install and start Ollama over SSH, then pull a model

```bash
ssh <pod-ssh> 'set -e; DEBIAN_FRONTEND=noninteractive apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y lshw zstd curl && \
  curl -fsSL https://ollama.com/install.sh | sh && \
  (env OLLAMA_HOST=0.0.0.0 OLLAMA_MODELS=/workspace/ollama ollama serve \
     > /workspace/ollama.log 2>&1 &) && \
  sleep 3 && ollama pull llama3.2:1b'      # tiny model for a fast readiness check
```

*What each part does:*

- *`apt-get install -y lshw zstd curl` — Ollama's installer and GPU detection
  need these. `-y` + `DEBIAN_FRONTEND=noninteractive` keep apt from prompting (an
  agent cannot answer a TTY prompt). System dependencies go through **apt**. Any Python
  tooling would use **uv** — see
  [`../../runpod-usage/reference/on-pod-setup.md`](../../runpod-usage/reference/on-pod-setup.md).*
- *`curl -fsSL https://ollama.com/install.sh | sh` — the vendor's supported
  install path.*
- *`env OLLAMA_HOST=0.0.0.0 OLLAMA_MODELS=/workspace/ollama ollama serve …` — the
  headline fix. Step 2's `--env` values reach **PID 1**, not the SSH login shell. `OLLAMA_HOST` is empty here, so Ollama would bind to `127.0.0.1` and the proxy would return 502. **Pass environment values explicitly on the serve command.** Write logs to the volume for later diagnosis.*
- *`ollama pull llama3.2:1b` — a deliberately tiny model so readiness tests
  fast (a bigger model like `llama3` works the same way, just slower to pull).
  Because `OLLAMA_MODELS=/workspace/ollama`, the weights land on the network
  volume and survive restarts.*

> **Detachment guidance:** the confirmed run started `ollama serve` in a subshell (`( … & )`).
> The same SSH command then continued to `pull`.
> For a server that must survive the SSH session independently, use full detachment.
> See [`../../runpod-usage/reference/on-pod-setup.md`](../../runpod-usage/reference/on-pod-setup.md).
>
> Its command is `setsid bash -c "…" > /workspace/ollama.log 2>&1 <
> /dev/null &`. This prevents channel-close SIGHUP from stopping the server.
> In either case, pass the environment explicitly.

### 5. Return the URL

```bash
echo "Ollama: https://<pod-id>-11434.proxy.runpod.net  (POST /api/generate)"
```

*Proxy URL shape is `https://<pod-id>-<internal-port>.proxy.runpod.net` — HTTPS
only, port `11434` (see
[`../../runpod-usage/reference/networking.md`](../../runpod-usage/reference/networking.md)).*

## Verify it works

"Running" is not "ready." Test from outside through the proxy. This shows that the proxy, `0.0.0.0` binding, and exposed port operate together.

**1. Readiness poll** (`GET /api/tags` → `200`):

```bash
for i in $(seq 1 120); do curl -sf https://<pod-id>-11434.proxy.runpod.net/api/tags && break; sleep 5; done  # bounded ~10min
```

*The proxy commonly returns `502` for the first 30–60s while the server starts. Continue to poll during normal startup, with a timeout. When it
returns `200`, the JSON lists the pulled model (`llama3.2:1b`).*

**2. Hello-world generation** (`POST /api/generate`):

```bash
curl -s https://<pod-id>-11434.proxy.runpod.net/api/generate \
  -d '{"model":"llama3.2:1b","prompt":"Say hello in one sentence.","stream":false}'
```

*Live result: `/api/generate` returned a JSON completion containing generated
text — the server is serving end to end. Prefer `stream` or short validation prompts. Cloudflare imposes a **100s cap** on the proxy, so long generation can return `524`.*

Only report success once a real request returns the right result.

## Gotchas we hit (live)

| Symptom | Cause | Fix |
| --- | --- | --- |
| **Proxy 502s even though the server "started"** (the headline) | `--env` values land in **PID 1, not the SSH shell**, so `OLLAMA_HOST` is empty over SSH and Ollama binds to `127.0.0.1` | **Pass env explicitly** on the launch: `env OLLAMA_HOST=0.0.0.0 … ollama serve`. Verified — this is the one step the naive version gets wrong. |
| Cannot expose port 11434 after the pod is up | **Ports are set at creation**. Reset before you add an HTTP port | Declare `11434/http` in `--ports` up front. |
| Proxy 502 with no obvious error | Ollama defaults to `127.0.0.1` | **Bind `0.0.0.0`** via `OLLAMA_HOST=0.0.0.0`. |
| Long single generation dies at ~100s (`524`) | Proxy is **HTTPS + Cloudflare, 100s cap** | Fine for normal API use. For long work stream or keep prompts short. |
| Models vanish after stop | Default model dir is container disk (wiped on stop) | Set `OLLAMA_MODELS=/workspace/ollama` onto the **network volume**. |
| Pod will not schedule after attaching the volume | Network volume is **DC-locked** | Create the pod in the **same DC** as the volume (`datacenter list` to co-locate). |
| Pod stopped but still billing | Used `--stop-after` (only stops) | Use **`--terminate-after`** as the real cost guard — it deletes the pod. |
| Endpoint is wide open | The proxy URL is **public and Ollama has no built-in auth** | Warn the user. Do not expose sensitive models unprotected. Add your own auth if needed. |

## Cost & cleanup

- **Cost guard at creation:** `--terminate-after <iso8601>` deletes the pod at
  that time. `--stop-after` only *stops* it, so disk/volume keep billing — prefer
  terminate.
- **Live cost reference:** the verified run used an **RTX 4090** GPU pod.
- **Tear down when done:**
  ```bash
  runpodctl pod remove <pod-id>              # aliases: rm / delete
  runpodctl network-volume delete <volume-id>   # remove the pod first
  ```
  Delete the pod before the volume. Keep the volume only if you want the pulled
  models to persist for a future pod (its models survive termination).

## Reference: skill gaps found / folded back

Capability was mostly present (runpodctl has every flag). The **skill guidance**
to run this agentically was what was thin. Everything below is now closed by
generic, reusable capabilities — not Ollama-specific recipes.

| Requirement | Covered today |
| --- | --- |
| Auth | router + runpodctl `doctor` / `RUNPOD_API_KEY` |
| Pod: pytorch template + GPU | `pod create --template-id --gpu-id` |
| Expose port + env at creation | `--ports` / `--env`, documented in `pod-workflows.md` + runpodctl |
| SSH enabled | `--ssh` defaults on. `ssh info` |
| Agent runs commands on the pod | `pod-workflows.md` — non-interactive `ssh <host> '…'` exec loop |
| Install hygiene / **uv** | `on-pod-setup.md` (apt for system, uv for Python, pin, background + log) |
| Poll readiness + escalate | `pod-workflows.md` steps 6 + 8 |
| Storage: default network volume | `storage.md` "prefer a network volume by default" |
| Return access URL | `networking.md` proxy format |

**Skill changes folded back (done):**

1. [`../../runpod-usage/reference/pod-workflows.md`](../../runpod-usage/reference/pod-workflows.md)
   — the reusable pod development loop (provision → ssh-exec → set up → run → poll
   readiness → escalate → deliver).
2. [`../../runpod-usage/reference/on-pod-setup.md`](../../runpod-usage/reference/on-pod-setup.md)
   — install hygiene (uv/apt, pin, non-interactive, cache on volume, background +
   log, detach long-lived servers).
3. [`../../runpod-usage/reference/storage.md`](../../runpod-usage/reference/storage.md)
   — "prefer a network volume by default" policy.
4. **Router + runpodctl** — service pods declare port + env at creation. Both
   point at the pod development loop.

**Live-verification note:** This workflow ran end to end on a real account. It created a network volume and pod (RTX 4090, PyTorch template, port 11434 + env at creation). It installed through SSH and ran `ollama serve` with explicit environment values. `ollama pull llama3.2:1b` stored the model on the volume. An external `/api/tags` poll returned 200, and `/api/generate` returned text. The run's
findings (env over SSH, `--terminate-after` vs `--stop-after`, `datacenter list`
for GPU/DC co-location, `uv`, non-interactive auth) are folded into the flow above
and the skill references.
