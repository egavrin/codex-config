---
name: companion-clis
description: "Use HuggingFace, GitHub, Docker, and AWS companion CLIs for Runpod workflows. If an imported ComfyUI workflow lacks model download metadata, use the ComfyUI model-repair guide in runpod-templates instead."
allowed-tools: Bash(hf:*), Bash(gh:*), Bash(docker:*), Bash(aws:*), Bash(ssh-keygen:*), Bash(ssh-add:*), Bash(ssh-agent:*)
metadata:
  compatibility: Linux, macOS, Windows
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Companion CLIs

Four CLIs commonly needed alongside Runpod. Each has its own **credentials + command reference** in [`reference/`](reference/) — plus a one-time `<cli>-setup.md` for install (only opened if the CLI is not installed). Load only the tool reference necessary for the task.

If an imported ComfyUI workflow's model filenames lack verified URLs or hashes, use runpod-templates. Follow its [ComfyUI model-repair guide](../runpod-templates/reference/comfyui-model-repair.md). Return here for download, cache, or image inclusion of an artifact whose exact Hugging Face repository/file is already known.

| CLI | Use it to | Full reference |
|-----|-----------|----------------|
| `hf` (HuggingFace) | Download models from the Hub to cache/bake into images | [reference/huggingface.md](reference/huggingface.md) |
| `gh` (GitHub) | Manage worker repositories + cut releases (Hub indexes releases) | [reference/github.md](reference/github.md) |
| `docker` | Build/validate/push images to Docker Hub for Runpod to pull | [reference/docker.md](reference/docker.md) |
| `aws` (S3) | Read/write network-volume storage over Runpod's S3 API | [reference/aws.md](reference/aws.md) |

Before use, supply credentials for each tool. Read the per-tool reference for auth steps and commands. Install is a separate one-time `<cli>-setup.md`.

These CLIs are usually one step inside a larger job. Read the verified complete workflow in [runpod/golden-paths/README.md](../runpod/golden-paths/README.md). Examples cover model baking versus mounting ([25](../runpod/golden-paths/25-bake-vs-mount/README.md)), minimal image builds ([22](../runpod/golden-paths/22-minimal-pod-image/README.md)), and network-volume transfers ([07](../runpod/golden-paths/07-network-volume-handoff.md)).

These third-party CLIs have independent releases. **`<cli> --help` defines their flags and subcommands.** These references cover Runpod-specific use and known problems. They do not describe every tool capability. Examine `--help` before reporting that one of them cannot do
something.

## Windows: Install WSL2 First

On Windows, install WSL2 before you continue. It supplies the native Linux environment that these CLIs target. In PowerShell as Administrator, then restart:

```powershell
wsl --install
```

Afterward open the Ubuntu app to finish setup, then follow the **Linux** instructions in each reference.

## HuggingFace CLI

Download models locally so they are cached for a Docker build/run. Auth and `hf download` recipes: **[reference/huggingface.md](reference/huggingface.md)** (install: [reference/huggingface-setup.md](reference/huggingface-setup.md)).

- Use the standalone `hf` CLI, **not** `pip install huggingface_hub` (that is the older `huggingface-cli` with different syntax).
- Auth via `hf auth login`, or `export HF_TOKEN=hf_...` (environment variable wins over saved token).

## GitHub CLI

Manage worker repositories and cut releases. Auth and commands: **[reference/github.md](reference/github.md)** (install + SSH-key setup: [reference/github-setup.md](reference/github-setup.md)).

- **The Hub indexes releases, not commits** — for every Hub listing update, run a new `gh release create`.
- One SSH key (`ssh-keygen -t ed25519`) registers with both GitHub (`gh ssh-key add`) and HuggingFace (paste in browser).

## Docker

Build, validate, and push images to Docker Hub. Credentials and commands: **[reference/docker.md](reference/docker.md)** (install: [reference/docker-setup.md](reference/docker-setup.md)).

- **Always build `--platform=linux/amd64`** — Runpod runs on x86 Linux.
- Always use explicit semantic tags. Never use `latest`. `latest` does not track the newest push, so workers can silently pull the incorrect image.
- Docker Hub auth uses a **personal access token**, not your password. For private images, register the credential once in Console → Container Registry Settings.

## AWS CLI

Access network-volume storage over Runpod's S3-compatible API (bucket name = network volume ID). Credentials, region rules, and commands: **[reference/aws.md](reference/aws.md)** (install: [reference/aws-setup.md](reference/aws-setup.md)).

- Runpod's S3 API, **not AWS**: access key = Runpod **user id** (`user_...`), secret = S3 API key (`rps_...`).
- **S3 API keys are Console-only.** `runpodctl`/REST/GraphQL cannot create them. If S3 access is necessary and no key exists in `~/.aws/credentials`/env, **stop and ask the user**. The user generates the key at Settings > S3 API Keys.
- For every command, supply `--region DATACENTER --endpoint-url https://s3api-DATACENTER.runpod.io/` (datacenter = the volume's DC, not an AWS region).
- For large/many-file transfers with reliable resume, see [reference/aws.md → optional resumable volume transfers](reference/aws.md#optional-resumable-volume-transfers-community-tool).

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
