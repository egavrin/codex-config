# Local review workflow

## Repository, state, and base

Run Git discovery inside the intended checkout:

```sh
git rev-parse --show-toplevel
git rev-parse --absolute-git-dir
git status --porcelain=v1 -z
git diff --cached --name-status --no-renames -z
```

Use the absolute top-level path as `source_dir`.
Use `<absolute-git-dir>/slopo` for all generated configuration, database, reports, logs, model identity, and review evidence.
For linked worktrees, use their own Git directory, not the common Git directory or a literal `.git` directory.
Create state with current-user-only permissions, such as `umask 077` and `mkdir -p`.

Select the base before review:

| Operation | Base |
| --- | --- |
| Normal commit with existing history | Resolved `HEAD` commit |
| Amend a commit with a parent | Resolved `HEAD^` commit |
| Initial commit or amend the initial commit | Empty-tree object from `git hash-object -t tree /dev/null` |
| Explicit review against a supplied base | Validate and resolve that base first |

Do not use the current commit as the base for an amendment.
An explicit review base does not replace the required base for a later commit.
If `HEAD` exists but `HEAD^` does not resolve, verify that `HEAD` has no parent.
A shallow checkout with an unavailable parent is not an initial commit.
Stop when a required base cannot resolve.

## Staged paths and current contents

Read staged paths with NUL-delimited Git output and rename detection disabled.
For each staged addition or modification, compare the index with the current file, including mode and deletion changes.
`git diff --quiet -- PATH` detects tracked differences between the index and working tree.
Use literal pathspecs for filenames that contain Git pathspec syntax.
For every staged deletion, also check whether any filesystem entry still occupies the path.
A recreated untracked path after a staged deletion must block the review.

If any staged path differs, stop and report partial staging before indexing or embedding.
Do not stage, unstage, reset, stash, discard, or reconstruct files to make the check pass.
Unrelated dirty paths can remain, but their findings do not become authority to edit them.
For an amendment, include retained changes from the amended commit when determining material findings.

## Local service and model identity

Read [the model pin](source-and-model.md) before starting or reusing Ollama.
All runtime model requests must use `http://127.0.0.1:11434`.
Disable proxies for these requests.
Do not use a cloud provider, remote endpoint, API key, or credential file.
Do not load `~/.env` or repository dotenv files for this workflow.

Check `GET /api/version` and `GET /api/tags` on the loopback endpoint.
Reuse an existing healthy Ollama server.
If a listener exists but is unhealthy or unidentified, stop and report the conflict.
Do not terminate or replace that listener.

If no server listens, start a temporary server:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 ollama serve
```

Keep the owned process handle or PID and its private log path.
Wait for a successful health response before model requests.
On completion, failure, or interruption, terminate only that owned process.
If another server wins a startup race, do not terminate that other server.
Do not install a persistent service or alter an existing server's configuration.

Find the exact model name in `/api/tags` and compare its full digest with the reference pin.
Before first indexing, write the checked name, digest, dimensions, and endpoint into `model-identity.json` inside private state.
Before every reuse, compare the server digest, reference pin, and state identity.
If any differ, stop and report the changed model.
If a database exists without its identity record, stop instead of assuming compatibility.
Do not silently pull another model, migrate a cache, remove a database, or rewrite its identity record.
If the model is absent, report the missing pinned model and block the commit.

## Configuration

Copy [the configuration template](../assets/config.yaml) into private state as `config.yaml` only when that file is absent.
Replace the path placeholders with absolute paths using a YAML serializer or correctly escaped JSON string values.
Preserve existing project configuration and any existing private configuration.
Before reuse, inspect existing private settings for the same source root, state paths, endpoint, model, dimensions, and exclusions.
Stop and report incompatible settings without overwriting them.

Keep the pinned upstream thresholds.
The template includes tests and excludes Git metadata, dependencies, build output, caches, credential paths, and nested agent worktrees.
Slopo does not automatically apply `.gitignore` during indexing.
Inspect project-specific ignored paths, credential locations, generated output, and symlink targets before indexing.
Add only necessary exclusion patterns to the private configuration.
Exclude source symlinks that resolve outside the checkout or into credential locations.
Do not use exclusions to hide actionable duplication or remove all tests.
Report material excluded code in the review evidence.

## Native CLI commands

Run the pinned CLI from the exact repository or worktree root.
Use a clean child environment for every Slopo command:

```sh
env -i HOME="$HOME" PATH="$PATH" \
  PYTHON_DOTENV_DISABLED=1 LITELLM_LOCAL_MODEL_COST_MAP=True \
  NO_PROXY=127.0.0.1,localhost \
  slopo --config "$SLOPO_CONFIG" show-config
```

Set `SLOPO_CONFIG` to the absolute private configuration path in the calling shell.
Inspect `show-config` before indexing.
Require an unset API key, the pinned model, 768 dimensions, the exact loopback endpoint, and absolute source and state paths.
The clean environment excludes inherited provider keys and remote endpoint overrides.
Do not run a bare Slopo command that allows its import-time dotenv load.

If the database is absent, run these native commands with that same clean environment:

```sh
slopo --config "$SLOPO_CONFIG" index
slopo --config "$SLOPO_CONFIG" embed
```

These command fragments require the clean `env -i` prefix shown above.
Check each exit code before the next command.
For an interrupted bootstrap, use explicit `index` and `embed` again after the identity and configuration checks.
The index operation creates the database and refreshes source units.
The embed operation supplies missing vectors.

Then run the native review with that same clean environment:

```sh
slopo --config "$SLOPO_CONFIG" agent-review --config-version=1 --base "$SLOPO_BASE"
```

Set `SLOPO_BASE` to the resolved comparison base.
Capture stdout, stderr, exit status, the private agent log, and the reviewed Git state.
Stop on failure and preserve its evidence.
The native command opens an existing database before it indexes.
It refuses more than 1000 pending units before indexing.
After that refusal, complete explicit `index` and `embed`, then run the native review again.
Do not reduce coverage or thresholds to bypass this limit.

If Slopo reports database, schema, source, or embedding incompatibility, preserve the database and report the conflict.
Do not delete or rebuild an incompatible database without a user decision.
Inspect parser warnings and index counts even when the review exits successfully.
Return to the commit gate in [SKILL.md](../SKILL.md) after the command completes.
