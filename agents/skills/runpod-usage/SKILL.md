---
name: runpod-usage
description: "Explain Runpod operation and use. Cover pods versus serverless, GPU/VRAM selection, storage, container builds, networking, and the pod development loop (provision → ssh-exec → set up → poll readiness). Include on-pod installation practices (uv/apt). Use for \"how does X work\", \"which GPU\", \"how do I build a container\", or \"how do I stand up a workload on a pod\". This skill supplies guidance. Execute through runpodctl, runpod-mcp, or flash."
metadata:
  author: runpod
  version: "1.5.0" # x-release-please-version
license: Apache-2.0
---

# Runpod usage (concepts)

Background knowledge for making the right choice before you act. This skill runs
nothing — once you know what to do, execute with **runpod-mcp**/**runpodctl**
(infra), **flash** (your own code), or **companion-clis** (models/images/data).

**This skill explains concepts. Golden paths demonstrate workflows.** For "how do I do X" rather than "how does X work", read the verified end-to-end example. The index is [runpod/golden-paths/README.md](../runpod/golden-paths/README.md). Read the concept here, then
follow the path.

Read the one reference file that matches the question:

| Question | Read |
| --- | --- |
| First-run setup / auth — get + set `RUNPOD_API_KEY`, SSH, companion creds | `reference/getting-started.md` |
| Pods vs serverless, workers, cold starts, FlashBoot, queue vs load-balanced | `reference/concepts.md` |
| **The development loop for ANY workload (start here)** — plan → prefer prebuilt → provision → test → teardown | `reference/development-loop.md` |
| **Stand up / iterate a workload on a pod** — the pod sub-loop | `reference/pod-workflows.md` |
| **Deploy / iterate a serverless endpoint** — Hub vs flash vs custom, invoke + test | `reference/endpoint-workflows.md` |
| **Install software on a pod** — package hygiene, `uv`, non-interactive, caching | `reference/on-pod-setup.md` |
| Build a Docker image Runpod can run (handler contract, Dockerfile, `--platform=linux/amd64`) | `reference/docker.md` |
| **How to build an image well** — base image, layering, bake-in vs volume, pod vs serverless (queue/LB) contract | `reference/building-images.md` |
| Where data lives — container disk vs network volume, model caching, S3 access | `reference/storage.md` |
| Which GPU / how much VRAM / cost & availability / data centers | `reference/gpu-selection.md` |
| Reaching a pod or endpoint over HTTP (proxy URLs, exposed ports) | `reference/networking.md` |
| Common mistakes and how to avoid them | `reference/gotchas.md` |

## Local adaptation

This skill contains local prose changes dated 2026-10-09.
See [PROVENANCE.md](PROVENANCE.md) for source identity and [LICENSE](LICENSE) for the original Apache-2.0 terms.
