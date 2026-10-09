# GitHub CLI

The GitHub CLI (`gh`) is used to manage repositories for Runpod serverless workers. This includes repository clones in local Docker containers for tests. It includes source version history for collaboration and GitHub releases that publish Runpod Hub listings. The Hub indexes releases — not commits — so publish a new release for every deployment update.

> **Not installed?** One-time install **and SSH-key setup** (generate + register the key) live in [`github-setup.md`](github-setup.md) — skip if `gh --version` works and your key is registered.

## Credentials

```bash
# Interactive login — when prompted, select SSH as the git protocol
gh auth login

# Verify auth
gh auth status
```

## Key Commands

```bash
# Repositories
gh repo create my-worker --public             # create a new public repo (required for Hub)
gh repo clone owner/repo                      # clone a repository over SSH
gh repo clone owner/repo -- --depth 1        # shallow clone
gh repo view owner/repo                       # view repo details and URL

# Releases — the Runpod Hub indexes releases, not commits
# Every update to a Hub listing requires a new GitHub release
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release"   # create a release
gh release create v1.0.1 --title "v1.0.1" --notes "Update model tag"  # update Hub listing
gh release list                               # list all releases
gh release view v1.0.0                        # view release details
```

### Runpod Hub repository structure

A Hub-compatible repository must have these files (in root or `.runpod/` directory):

```
handler.py        # serverless worker implementation
Dockerfile        # container definition
README.md         # documentation shown on Hub listing
.runpod/
  hub.json        # Hub metadata: title, description, category, GPU config, env vars
  tests.json      # test cases run after each release
```

To publish: go to https://console.runpod.io → Hub → Add your repository → enter the GitHub repository URL.
