# Codex config

Personal Codex configuration for `egavrin`. This repository contains a macOS
configuration snapshot updated on September 10, 2026.

## Contents

- `codex/config.toml` — model, MCP, plugin, trusted-project, application, and
  multi-agent settings.
- `codex/AGENTS.md` — the global English-language guide for cost-efficient
  orchestration, including Light and Heavy routes, compact task capsules,
  batching, event-driven waits without polling, and separate implementation and
  verification ownership.
- `codex/agents/` — `worker` (Terra High), `explorer` (Luna Medium), `tester`
  (Luna High), and the strictly gated `senior_executor` (Sol Medium).
- `codex/rules/` — local command-execution rules.
- `codex/skills/` — selected user skills: `gh-address-comments`, `gh-fix-ci`,
  `hatch-pet`, and `repo-modernizer`, including their scripts, resources, and
  bundled licenses where present.

The snapshot preserves the active values, including `gpt-6-astra` with Medium
reasoning, `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`,
Standard service tier, at most two concurrent subagents, and a maximum subagent
depth of one. Routine implementation is routed to Terra High. Sol Medium is
available only through the escalation gate documented in `codex/AGENTS.md`.

The repository intentionally excludes authentication data, tokens, task
history, databases, memories, attachments, automations, downloaded plugins,
system skills, and project-specific instructions or skills from other
repositories. The assets for the selected `custom:rivet` pet are not included;
only its selection remains in the configuration snapshot.

## Orchestration model

The default execution model is:

```text
Root                   GPT-6 Astra Medium architecture, decisions, integration
worker                 Terra High         implementation and ordinary repair
explorer               Luna Medium        bounded read-only investigation
tester                 Luna High          independent verification
senior_executor        Sol Medium         strictly gated hard implementation
```

Small bounded tasks use the Light route without subagents. Substantial work uses
the Heavy route: the root directs bounded agents, transfers compact context,
batches independent work, waits without status polling, and synthesizes each
batch once. After four completed subagent sessions, an adaptive delegation
checkpoint requires a concrete reason for every additional wave without imposing
a hard lifetime cap on genuinely large tasks. The root must not silently take
routine production work back from a healthy worker.

The Desktop UI currently exposes Medium and Extra High as the practical Astra
presets. Medium is the configured default. The multi-agent v2 runtime may promote
the root to Extra High automatically; route instructions do not force that
transition, and Heavy should be selected because delegation is justified rather
than as a way to obtain a higher reasoning preset.

Because a task name alone does not activate a role profile in every collaboration
runtime, `codex/AGENTS.md` also defines an explicit runtime routing contract. The
root passes the role's model and reasoning effort when spawning an agent. A
dependent tester starts only after the relevant worker finishes and never polls
or waits for sibling agents.

## Restore

The active user configuration normally lives at `~/.codex/config.toml`. See the
[official Codex configuration documentation](https://learn.chatgpt.com/docs/config-file/config-basic)
for the current platform behavior.

Install Codex and any required plugins first, then clone this repository:

```sh
gh repo clone egavrin/codex-config
cd codex-config
```

This is a snapshot of one Mac. Before restoring it on another machine, review
`codex/config.toml` for absolute `/Users/egavrin` paths, the
`/Applications/ChatGPT.app` location, bundled-plugin paths and versions, trusted
projects, and MCP settings. Plugin files, MCP authentication, and pet assets must
be installed separately; a plugin entry in `config.toml` does not install the
plugin itself.

Quit Codex before restoring so that the running application cannot overwrite the
files. The following commands back up replaced files to a temporary directory,
copy only the contents of `codex/`, and leave unrelated destination files in
place:

```sh
codex_target="${CODEX_HOME:-$HOME/.codex}"
codex_backup_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-config-backup.XXXXXX")"
mkdir -p "$codex_target"
rsync -av --backup --backup-dir="$codex_backup_dir" codex/ "$codex_target/"
printf 'Backup of replaced files: %s\n' "$codex_backup_dir"
```

Open Codex again after the restore. Sign in and reconnect integrations if
needed. Start a new task so the new configuration and global instructions are
loaded into a fresh session.

## Update the snapshot

From the root of this clone, copy only the listed configuration, rules, and
selected user skills:

```sh
codex_source="${CODEX_HOME:-$HOME/.codex}"
cp "$codex_source/config.toml" codex/config.toml
cp "$codex_source/AGENTS.md" codex/AGENTS.md
for codex_part in agents rules skills/gh-address-comments skills/gh-fix-ci skills/hatch-pet skills/repo-modernizer; do
  mkdir -p "codex/$codex_part"
  rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' --exclude='.git' \
    "$codex_source/$codex_part/" "codex/$codex_part/"
done
git diff --stat
git diff
```

These commands do not propagate deletions from the active configuration into
the snapshot. Apply intended deletions manually. Before committing, inspect the
complete diff, especially MCP environment values, HTTP headers, and command
rules. `.gitignore` excludes common generated files, but it cannot detect
secrets embedded inside tracked TOML or other text files.

```sh
git add codex README.md
git commit -m "Update Codex configuration"
git push
```

Synchronization is manual. Creating or cloning this repository does not alter
the active Codex configuration and does not configure automatic GitHub uploads.
