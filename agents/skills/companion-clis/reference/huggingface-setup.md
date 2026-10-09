# HuggingFace CLI — one-time setup

If `hf version` fails, install the `hf` CLI once. See [`huggingface.md`](huggingface.md) for authentication and `hf download` procedures.

```bash
# macOS / Linux (standalone installer — recommended)
curl -LsSf https://hf.co/cli/install.sh | bash

# macOS (Homebrew)
brew install hf

# Windows (WSL2): use the Linux standalone installer above
```

> **Note:** `pip install huggingface_hub` installs the older Python CLI (`huggingface-cli`),
> which uses different command syntax.

Use the standalone `hf` CLI installed above.
