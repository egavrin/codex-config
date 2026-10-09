# On-pod setup & install hygiene

How to install and configure software on a pod so it is reproducible, survives
restarts, and does not wedge on an interactive prompt. Applies to any workload.
Run these over the SSH channel from the pod development loop (`pod-workflows.md`).

## Use package managers, not ad-hoc downloads

- **System packages → `apt`** (Debian/Ubuntu base images):
  ```bash
  DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y <pkgs>
  ```
- **Python → `uv`** (fast, reproducible, one static binary). Prefer it over bare
  `pip`/`conda` for a *fresh* environment:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv venv /workspace/.venv && . /workspace/.venv/bin/activate
  uv pip install <packages>            # or: uv pip install -r requirements.txt
  ```
  Put the venv on the volume (`/workspace/...`) so it persists.

  > **On a PyTorch template image, do not create a bare `uv venv`.**
  > Official templates include `torch`/CUDA in **system** Python. A fresh virtual environment does not inherit it.
  > A new environment must have another multi-GB torch installation, or the app cannot find CUDA.
  > Install the app's dependencies into the **existing** interpreter:
  > ```bash
  > pip install --break-system-packages -r requirements.txt   # newer images are
  >   # PEP 668 "externally-managed"; plain `pip install` errors without this flag
  > # or, to still use uv: uv venv --system-site-packages && uv pip install ...
  > ```
  > pip correctly sees the pre-installed torch as already satisfied and only adds
  > what is missing.
- **A vendor install script** (for example a service's official `install.sh`):
  - **Rule:** pin a version so the setup is reproducible (`INSTALL_VERSION=…` or the
    script's documented pin flag).
  - **Exception:** If a script cannot pin versions, an unpinned installation is permitted only as the vendor's sole supported installation path.

## Make it non-interactive

An agent cannot answer prompts. Always:

- Pass `-y` / `--yes`. Set `DEBIAN_FRONTEND=noninteractive` for apt.
- Provide required config via environment variables or flags, not TTY prompts.
- Avoid commands that open a pager or editor.
- **Pod `--env` vars are not in your SSH shell** (they go to PID 1). When you
  launch a service or script over SSH for which they are necessary, pass them explicitly:
  `ssh <host> 'env VAR=val <command>'`. See `pod-workflows.md` step 5.

## Pin versions

- Pin package and image versions (`pkg==1.2.3`, `image:tag`, not `latest`) so a
  rebuild or restart reproduces the same environment. See `gotchas.md`.

## Persist heavy artifacts on the volume

Anything large or slow to fetch goes on the network volume so it survives restarts
and is not re-downloaded (see `storage.md`). Point caches at the volume:

```bash
export HF_HOME=/workspace/hf-cache          # HuggingFace models/datasets
export UV_CACHE_DIR=/workspace/uv-cache      # uv package cache
export PIP_CACHE_DIR=/workspace/pip-cache
```

## Run long work in the background, and log

Installs, model pulls, and servers can outlast a single SSH command. Background
them and log to the volume so you can poll progress and diagnose later:

```bash
ssh <host> '(long-running-setup > /workspace/setup.log 2>&1 &) '
ssh <host> 'tail -n 20 /workspace/setup.log'   # poll in a SEPARATE ssh call
```

> **Detach a long-running server fully.** The SSH channel sends SIGHUP to its process group when it closes.
> This signal stops a process started with only `&` or a subshell. If a service must survive disconnection (a web server, `serve`, ComfyUI), start it detached and return immediately.
> Wait for readiness in a separate, later SSH call:
> ```bash
> ssh <host> 'setsid bash -c "<server-cmd>" > /workspace/svc.log 2>&1 < /dev/null &'
> ```
> `setsid` (new session, off the SSH TTY/pgroup) **and** `< /dev/null` are both
> needed. Do not `sleep` in the same invocation — it can drop the channel (exit 255).

## Be idempotent

Write setup so re-running it is safe (check-before-install, `mkdir -p`, `|| true`
on best-effort steps). You will run it again after a restart or a fix.

## Verify each step

Before the next installation, examine the previous installation's exit code and expected output. Do not chain all installations and discover failures only at the end. Surface the actual
error. Do not swallow it.
