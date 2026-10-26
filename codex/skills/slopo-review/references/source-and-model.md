# Source and model pins

## Upstream source

- Project: [rafal-qa/slopo](https://github.com/rafal-qa/slopo).
- Source revision: `cb63e8ee4c27d40f47999c96e75b18bd5816b249`.
- CLI version: `0.9.0`.
- Python requirement: `>=3.12`.
- License: `AGPL-3.0-or-later`, with the exact upstream [LICENSE](../LICENSE).
- Original skill: [pinned SKILL.md](https://github.com/rafal-qa/slopo/blob/cb63e8ee4c27d40f47999c96e75b18bd5816b249/src/slopo/agent/configs/codex-skills/slopo-review/SKILL.md).

This local adaptation retains Slopo's native review command and similarity judgment.
It adds shared Codex and Claude discovery, local-only execution, worktree state, explicit bootstrap, and the user-approved commit gate.
It replaces the upstream first-response restriction with scoped remediation for authorized implementation tasks.
Explicit review-only requests remain read-only for source code.
No Slopo analysis engine or production launcher is copied or replaced.

The installation resolved `python-dotenv==1.2.4` and `litellm==1.102.4`.
The workflow requires `PYTHON_DOTENV_DISABLED=1` before the CLI starts.
The pinned CLI sets `LITELLM_LOCAL_MODEL_COST_MAP=True` before it imports LiteLLM for embeddings.
These facts describe the inspected installation, not a complete dependency lock.

## Model identity

| Field | Pinned value |
| --- | --- |
| Slopo model | `ollama/unclemusclez/jina-embeddings-v2-base-code:latest` |
| Ollama model | `unclemusclez/jina-embeddings-v2-base-code:latest` |
| Digest from `/api/tags` | `9fe680d4d58b475099d91e0d08a1eaea6cef087b0a0770f4165581a7e366afec` |
| Dimensions | `768` |
| Runtime endpoint | `http://127.0.0.1:11434` |
| Observed model size | `322997591` bytes |
| Validated Ollama version | `0.21.1` |

The installation obtained one real embedding with 768 dimensions from this model.
The tag is mutable, so the workflow compares the full digest before each reuse.
A changed digest requires an explicit model and cache decision.
It must not cause silent migration or deletion.

## Verification

The black-box checks use the installed Slopo executable and temporary Git repositories.
A synthetic loopback server supplies deterministic vectors on a free port.
Only this test fixture uses a different local port.
The production template remains fixed at port `11434`.
The tests do not evaluate the model's semantic accuracy or automate commit-policy judgment.

Run this command with a new, private output directory:

```sh
python3 ~/.codex/skills/slopo-review/tests/workflow.py \
  --output /absolute/private/new-evidence-directory \
  --slopo ~/.local/bin/slopo
```

The output contains fixture repositories, exact commands, results, HTTP request metadata, and upstream and fixture revisions.
The fixture creates local commits only inside its new evidence directory.
The tests disable global Git configuration and do not load credentials.
The checks cover bootstrap, pending embeddings, clean changes, duplicate code, documentation-only changes, initial and amendment bases, exclusions, and linked worktrees.
They also cover invalid bases, incompatible dimensions, wrong agent configuration versions, and disabled dotenv loading.
Host acceptance must separately check real-model behavior, model identity changes, service ownership, partial staging, and unrelated dirty changes.
