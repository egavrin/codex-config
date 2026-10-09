# Building container images for Runpod

Select a Runpod base image and organize layers for speed. Decide which content belongs in the image and which content uses a runtime mount. Match the **image contract** to the target: pod, serverless queue, or serverless load-balanced endpoint. CLI mechanics (login, tag,
push) live in [companion-clis docker](../../companion-clis/reference/docker.md) and
[docker.md](docker.md). This is the strategy layer.

## Start from an official Runpod base image

**For a GPU workload, build `FROM` an official `runpod/pytorch:<tag>` image.** Two reasons:

- **torch/CUDA already match Runpod hosts**, so you do not fight driver/toolkit mismatches.
- **Runpod pre-caches official base images on its hosts.** The host already has these base layers. Image pulls download only the layers that you add. Starting from a random public base throws that away.

**Exceptions (both shown in the golden paths):** a trivial CPU-only workload may use a slim base (for example `python:3.11-slim`). See [GP23](../../runpod/golden-paths/23-minimal-queue-image/README.md). For pods with a **non-Runpod base, you must supply SSH**. See the SSH section below and [GP22](../../runpod/golden-paths/22-minimal-pod-image/README.md).

Then, whatever the base:

- **Pin an exact tag**, for example `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` — for
  reproducible builds.
- **Build for x86_64:** `docker build --platform=linux/amd64 …` — Runpod hosts are x86_64
  (see [docker.md](docker.md)).

## Layer for fast, cacheable pulls

Order layers from least to most frequently changed. Code edits then preserve large dependency layers, and independent layers download concurrently:

1. base image (`FROM runpod/pytorch:…`)
2. system dependencies (`apt-get …`)
3. Python dependencies (`pip install …`)
4. **your code last**

Unchanged layers are reused from cache. Only the layers after your edit rebuild/re-pull.

## Dockerfile best practices

- **`.dockerignore`** — exclude `.git`, virtualenvs, datasets, local caches so the build context stays small and pushes fast.
- Cache the dependency layer. Run `COPY requirements.txt` and `pip install` before you `COPY` code. A code edit then avoids full reinstallation:
  ```dockerfile
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  ```
- **Shrink the image** (smaller = faster pull + cold start) with concrete steps: `apt-get install --no-install-recommends …` then `rm -rf /var/lib/apt/lists/*`. `pip install --no-cache-dir`. Use a **multi-stage** build when heavy build tools are not needed at runtime.
- **BuildKit cache mounts** for fast rebuilds: `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`.
- **Never bake secrets** into layers (API keys, tokens) — layers are extractable. Pass secrets as runtime env.
- **`ENV PYTHONUNBUFFERED=1`** — so logs stream unbuffered. (Pin the base image tag too — see above.)

## Do not clobber the base image's startup (SSH / web terminal) — **pods**

Official `runpod/pytorch` images include `CMD ["/start.sh"]`. That script reads `$PUBLIC_KEY` into `~/.ssh/authorized_keys`, runs `ssh-keygen -A`, and starts `sshd`. It also starts the web terminal / Jupyter. It also runs `/pre_start.sh` before
and `/post_start.sh` after, if those exist.

**Rule (pods):** any custom `CMD`/`ENTRYPOINT` **must invoke `/start.sh`** — inherit it, or run
`/start.sh &` before your workload. **Exception:** serverless images are exempt (no SSH).

If a custom `CMD`/`ENTRYPOINT` does not call `/start.sh`, these startup actions do not occur. The pod has **no SSH or web terminal**, which can prevent access. For a pod this is the #1
footgun.

Three safe patterns, in order of preference:

1. **Do not override `CMD` at all** (default — use this unless the task calls for your own foreground
   process). Add your layers, leave `CMD ["/start.sh"]`. Do per-pod work via the env-driven
   hooks the base already runs:
   ```dockerfile
   FROM runpod/pytorch:<tag>
   COPY post_start.sh /post_start.sh   # base runs this AFTER sshd is up
   RUN chmod +x /post_start.sh
   # no CMD — inherit the base's /start.sh
   ```
2. **Override only when your own foreground process is necessary** (a long-running service as PID 1):
   call the base start first, then `exec` your workload:
   ```dockerfile
   COPY run.sh /run.sh
   RUN chmod +x /run.sh
   CMD ["/run.sh"]
   ```
   ```bash
   #!/usr/bin/env bash
   /start.sh &        # SSH + web terminal (base startup), backgrounded
   sleep 2
   exec python -u my_service.py   # your long-running workload in the foreground
   ```
3. **From a non-Runpod base, reproduce SSH yourself** (only if you cannot start from
   `runpod/pytorch`). Minimum to not get locked out of a pod:
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends openssh-server \
       && rm -rf /var/lib/apt/lists/*
   COPY start.sh /start.sh
   RUN chmod +x /start.sh
   CMD ["/start.sh"]
   ```
   ```bash
   #!/usr/bin/env bash
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   [ -n "$PUBLIC_KEY" ] && echo "$PUBLIC_KEY" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
   ssh-keygen -A                       # host keys
   service ssh start                   # or: /usr/sbin/sshd -D
   exec "$@"                            # then your workload (or keep sshd in foreground)
   ```

Reference implementation: `justinwlin/Runpod-GPU-And-Serverless-Base` (a dual pod+serverless
base) and the vendored `start.sh` in
[golden path 09](../../runpod/golden-paths/09-custom-serverless-dev-loop/README.md). Worked
end-to-end in [golden path 22 — minimal pod image](../../runpod/golden-paths/22-minimal-pod-image/README.md).

## Bake in vs mount at runtime (this drives startup speed)

Only the **image** (and whatever is baked into it) lands on the host's **local disk** — fast.
An attached **network volume** replaces the working directory (`/workspace` on a pod, `/runpod-volume` on serverless). Writes to that directory use network storage, which is slower, especially for many small files.

Live proof that this is a real filesystem boundary (baked = `overlay`/local, volume =
`fuse`/MooseFS network mount): [golden path 25 — bake vs mount](../../runpod/golden-paths/25-bake-vs-mount/README.md).

- **Bake into the image:** packages, libraries, and lots of small static files → local, fast.
- **Mount a volume:** large/few files (model weights, datasets), anything that must persist
  across pods, or data you stream/live-load.
- **High-throughput / I/O-bound training:**
  - **temporary / one-off run** → a **pod using local (non-network) storage** is fastest.
  - **persistent, many small files, or I/O-bound** → a **high-performance network volume**.

  See [golden path 21 — storage tiers](../../runpod/golden-paths/21-storage-tiers.md).

## Match the image contract to the target

| Target | Handler necessary? | Entry point |
| --- | --- | --- |
| **Pod** | No | your `CMD`/entrypoint — a long-running service. Bind `0.0.0.0`, expose ports |
| **Serverless — queue-based** | **Yes** | `runpod.serverless.start({"handler": handler})` |
| **Serverless — load-balanced** | No (different contract) | your own **HTTP server** exposing routes (no queue handler) |

Minimal runnable image per contract (each built + deployed live): pod →
[golden path 22](../../runpod/golden-paths/22-minimal-pod-image/README.md), queue →
[golden path 23](../../runpod/golden-paths/23-minimal-queue-image/README.md), load-balanced →
[golden path 14](../../runpod/golden-paths/14-load-balancing-endpoint.md).

Queue vs load-balanced request/response shapes and when to pick each are covered in
[endpoint-workflows.md](endpoint-workflows.md) and golden paths
[12 (streaming)](../../runpod/golden-paths/12-serverless-streaming.md),
[14 (load-balancing)](../../runpod/golden-paths/14-load-balancing-endpoint.md), and
[17 (WebSocket)](../../runpod/golden-paths/17-serverless-websocket.md). One image can be
**dual-mode** (pod dev + serverless) — see
[golden path 09](../../runpod/golden-paths/09-custom-serverless-dev-loop/README.md).

## Test locally before deploying

- Build for the right platform: `docker build --platform=linux/amd64 …`.
- **Queue handler:** run the container and invoke `handler.py` locally (the dual-mode
  `python handler.py` loop in [golden path 09](../../runpod/golden-paths/09-custom-serverless-dev-loop/README.md))
  before pushing.
- **Load-balanced:** run the container and hit the HTTP routes locally.
- Then push ([companion-clis docker](../../companion-clis/reference/docker.md)) and deploy
  (runpodctl or runpod-mcp).
