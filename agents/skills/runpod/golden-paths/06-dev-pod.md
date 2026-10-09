# Golden path 06 — interactive dev pod (SSH / VS Code + persistent /workspace)

**Goal:** Process "give me a Runpod dev box I can SSH into / open in VS Code". Provision a PyTorch-template pod with a **network volume at `/workspace`**. Return a ready **SSH-over-TCP** connection and the `~/.ssh/config` block for VS Code / Cursor Remote-SSH. Demonstrate an interactive session and storage that **survives stop/restart**.

Unlike service pods 01/02, this workflow has no HTTP proxy URL to poll. **For success, make sure that an interactive shell works and `/workspace` persists through stop/restart.** The VS Code Remote-SSH connection string must resolve and download the server.
**Status:** COVERED — live-verified 2026-07-10. The run created an RTX 4090 pod on `runpod-torch-v280` in EU-RO-1 with a 10 GB network volume at `/workspace`. SSH-exec returned actual GPU/torch output.

A marker survived `pod stop`→`pod start`, while ephemeral `/root` was erased and the container hostname changed. VS Code Remote-SSH connected through a `~/.ssh/config` alias. The pod downloaded the **exact** `vscode-server-linux-x64.tar.gz` for the local editor commit with HTTP 200. The one thing not machine-checkable is the final GUI click (see [VS Code](#verify-it-works--vs-code--cursor-remote-ssh-what-was-verified-headlessly)).
**Lane(s):** runpodctl (pod + volume) + SSH-exec. Builds on the pod-create + readiness-poll
pattern from golden path [07](07-network-volume-handoff.md).

## When to use this
The user wants an interactive computer: an SSH shell, a VS Code / Cursor Remote-SSH window, or a scratch GPU for experiments. They do not want a served endpoint. Reach for it
whenever the task is "give me a dev machine" rather than "deploy this model". If instead you
must *serve* something over a URL, that is golden path [01](01-ollama-pod.md)/[02](02-comfyui-pod/README.md).
If you are running a *batch* training job, that is [04](04-finetune-pod.md)/[08](08-finetune-to-serverless.md).

## Prerequisites
- `RUNPOD_API_KEY` resolvable (`export RUNPOD_API_KEY=...`).
- `runpodctl` installed.
- **An SSH key registered on the account BEFORE the pod boots.** Runpod injects registered public keys into the pod's `~/.ssh/authorized_keys` at startup. A key added after the pod starts is unavailable until a restart (see [`../../runpod-usage/reference/getting-started.md`](../../runpod-usage/reference/getting-started.md)).
  Make sure that a key is registered with `runpodctl ssh list-keys`. If empty, register one:
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''          # if you don't have one
  runpodctl ssh add-key --key-file ~/.ssh/id_ed25519.pub
  runpodctl ssh list-keys                                    # confirm it's on the account
  ```
- For VS Code Remote-SSH on your machine: VS Code/Cursor with the **Remote-SSH** extension.

## Walkthrough (verified commands)

### 1. Persistent workspace — a network volume in your target DC
`/workspace` on a dev pod is backed by a network volume so your code/data survives a reset.
The volume is **pinned to one DC**. The pod must run in that same DC.
```bash
runpodctl network-volume create --name devbox-demo --size 10 --data-center-id EU-RO-1
# → id, e.g. gjj71yzmnd, in EU-RO-1
```

### 2. Create the pod — PyTorch template, volume at `/workspace`, TCP 22 exposed
Follow golden path 07's create flags. The two additions for a dev box: `--ports "22/tcp"` (so
SSH is reachable over a **public IP + external TCP port**, as necessary for VS Code Remote-SSH)
and the volume mounted at `/workspace`.
```bash
runpodctl pod create --name devbox-demo \
  --template-id runpod-torch-v280 --gpu-id "NVIDIA GeForce RTX 4090" \
  --data-center-ids EU-RO-1 \
  --network-volume-id <vol-id> --volume-mount-path /workspace \
  --ports "22/tcp" \
  --ssh --terminate-after <iso8601 ~1-2h out>       # TEST guard — see note below
```
> **`--terminate-after` vs `--stop-after`.** This live run used `--terminate-after` as a
> **cost guard for a throwaway test** (it deletes the pod at the deadline).

For a **development box that the user returns to**, use `--stop-after`. `stop` preserves the pod and `/workspace`. `terminate`/`remove` **deletes** the pod. The separate network volume survives either operation.

Verified image on `runpod-torch-v280`:
> `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`, RTX 4090 at **$0.69/hr**.

### 3. Poll until the runtime is up, then read the SSH-over-TCP connection
`ssh info` returns `"error": "pod not ready"` until the runtime is live — poll it (07's
pattern). If "pod not ready" / `runtime: false` continues past ~5–6 min, treat it as a bad machine draw. Run `pod remove` and recreate instead of waiting indefinitely ([07](07-network-volume-handoff.md), `gotchas.md`).
```bash
runpodctl ssh info <pod-id>
# → {"ip":"213.173.108.151","port":17740,
#    "ssh_command":"ssh -i /Users/you/.runpod/ssh/RunPod-Key-Go root@213.173.108.151 -p 17740", ...}
```
`ssh info` hands you the **public-IP + external-port TCP form directly** — this is the form
necessary for VS Code Remote-SSH (not the proxied `…@ssh.runpod.io` basic-SSH form). It also names the
key path to use (`ssh_key.path`). Agents should use that exact path.

### 4. Verify it is actually interactive (not just "Running")
Connect non-interactively (07's flags). Use the IP/port/key from `ssh info`:
```bash
ssh -i /Users/you/.runpod/ssh/RunPod-Key-Go \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -p 17740 root@213.173.108.151 \
    'hostname; nvidia-smi -L; python3 --version; \
     python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"; \
     df -h /workspace | tail -1'
```
Real output (2026-07-10):
```
881177e25f9d
GPU 0: NVIDIA GeForce RTX 4090 (UUID: GPU-44150745-556c-e3f1-55bc-caae92449acf)
Python 3.12.3
2.8.0+cu128 True
mfs#euro-3.runpod.net:9421  839T  315T  524T  38% /workspace     # volume-backed, network FS
```

### 5. Prove `/workspace` persistence across a stop/restart
Write a marker to `/workspace` and something to ephemeral `/root`, then `stop`→`start`:
```bash
ssh ... -p 17740 root@213.173.108.151 \
  'echo "devbox persistence $(date -u +%FT%TZ)" > /workspace/marker.txt; echo ephemeral > /root/ephemeral.txt'

runpodctl pod stop  <pod-id>          # wait for desiredStatus EXITED
runpodctl pod start <pod-id>          # then re-poll ssh info (PORT CHANGES — see gotcha)

ssh ... -p <NEW-port> root@213.173.108.151 \
  'cat /workspace/marker.txt; test -f /root/ephemeral.txt && echo EXISTS || echo GONE-wiped; hostname'
```
Real result (2026-07-10) — the marker survived, `/root` was wiped, the container is new:
```
devbox persistence 2026-07-10T20:30:06Z     # /workspace marker — SURVIVED
GONE-wiped                                    # /root/ephemeral.txt — wiped on stop
b65f1a073985                                  # hostname changed (was 881177e25f9d) → real restart
```

### 6. Hand off — the VS Code / Cursor Remote-SSH `~/.ssh/config` block
Add this to your local `~/.ssh/config`. Then, follow this VS Code/Cursor path: Command Palette → Remote-SSH: Connect to Host → `runpod-devbox` → Open Folder → `/workspace`.
```
Host runpod-devbox
    HostName 213.173.108.151          # from `ssh info` .ip
    User root
    Port 17740                        # from `ssh info` .port — RE-READ after every stop/start
    IdentityFile ~/.runpod/ssh/RunPod-Key-Go   # from `ssh info` .ssh_key.path
```

## Verify it works — VS Code / Cursor Remote-SSH (what was verified headlessly)
<a id="4-vs-code--cursor-remote-ssh-what-was-verified-headlessly"></a>
VS Code Remote-SSH runs the system `ssh` against a `~/.ssh/config` Host alias. Then, it downloads and launches the VS Code Server on the remote for your editor's commit. Both
mechanical steps were verified without a GUI:

1. **The Host-alias transport connects** — exactly the `ssh` invocation the extension makes:
   ```bash
   ssh -F /tmp/devbox.cfg runpod-devbox 'echo OK on $(hostname); uname -m'
   # → VS Code Remote-SSH transport OK on host b65f1a073985 / x86_64
   ```
2. **The remote arch matches the server build** — pod is `x86_64` → `server-linux-x64`.
3. **The pod can fetch the exact server tarball for the local editor's commit** (what
   Remote-SSH downloads on first connect):
   ```bash
   COMMIT=$(code --version | sed -n '2p')     # e.g. 4fe60c8b1cdac1c4c174f2fb180d0d758272d713
   ssh -F /tmp/devbox.cfg runpod-devbox \
     "curl -sIL -o /dev/null -w '%{http_code} %{url_effective}\n' \
      https://update.code.visualstudio.com/commit:${COMMIT}/server-linux-x64/stable"
   # → 200  https://vscode.download.prss.microsoft.com/.../vscode-server-linux-x64.tar.gz
   ```

**Verified:** The user connection string resolves through its alias. SSH authenticates with the account key, and the remote architecture is correct. The pod can access and download the VS Code Server binary. **A human GUI action remains necessary:** *Remote-SSH: Connect to Host* in the desktop editor.

This Electron action cannot run headlessly.
Everything up to that click is proven. The click itself just runs steps 1–3 above.

## Gotchas we hit
- **The external TCP port is reassigned on every stop/restart — and `ssh info` can hand you a
  STALE port right after `start`.** Live: the pod came up on port **17740**. After `pod
  stop`→`start` the *first* `ssh info` still reported 17740 (connections were refused), and a
  moment later it returned the real new port **12890**. Always read `ssh info` again after a restart. If you get connection-refused, poll `ssh info` again for a fresh port before updating your `~/.ssh/config` `Port`. (The public IP happened to stay the same here, on
  Community Cloud it can change too.)
- **"Running"/"READY" ≠ sshd is up.** After `start`, `ssh info` reported READY while sshd was
  still initializing — SSH was connection-refused for ~90s. Retry the real `ssh` (or poll a
  fresh `ssh info`) rather than trusting the first READY.
- **Only `/workspace` persists.** Proven live: the network volume at `/workspace` survived
  stop/start. Everything else (`/root`, installed apt packages, `/tmp`) is **wiped on stop**
  (the hostname even changed). Keep code, envs, and data under `/workspace`.
- **Key must exist before boot.** Registered account keys are injected at startup. Add a key
  after the pod is running and it will not work until a restart. Register first (Prerequisites).
- **Use the key path from `ssh info`.** `ssh info` reports `ssh_key.path` + whether it is
  `in_account`. The live run's working key was runpodctl's own `~/.runpod/ssh/RunPod-Key-Go`.
  Any account-registered key works, but taking the one `ssh info` names avoids guesswork.
- **Volume ↔ GPU same DC.** The volume is DC-locked (EU-RO-1 here). The pod must run in that DC.

## Cost & cleanup
```bash
runpodctl pod remove <pod-id>                 # deletes the pod (do this for bad-draw pods too)
runpodctl network-volume delete <vol-id>      # pod must be removed first
runpodctl pod list && runpodctl network-volume list   # confirm clean
```
Live cost: RTX 4090 pod at **$0.69/hr** + 10 GB volume (negligible). For a real dev box you
keep, `--stop-after` (stopped pods still bill for disk + the volume) instead of
`--terminate-after`. `remove` + volume `delete` when done for good. A CPU pod is cheaper if you
can operate without the GPU — drop `--gpu-id` and use `--compute-type cpu` (not exercised in this run).

## Skill gaps folded back
- **`getting-started.md`** already documents key-before-boot + the non-interactive
  `ssh -o StrictHostKeyChecking=no` pattern — confirmed correct in practice.
- `gotchas.md` "Pod shows Running but ports aren't reachable yet" now includes the concrete dev-pod finding. After a stop/start, `ssh info` can return a stale external TCP port and report READY before sshd is up. Read `ssh info` again and retry.
- Confirmed for this doc: `runpodctl ssh info` supplies the public-IP + external-TCP-port form directly (no Console needed), including the key path. An agent can use this information to build the VS Code Remote-SSH `~/.ssh/config` unaided.
