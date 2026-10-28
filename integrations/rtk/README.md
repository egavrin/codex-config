# RTK integration

This snapshot pins RTK OSS 1.1.0 at revision `753a3b0e939f2e4490fc24e3a1984010f40a103c`.
`provenance.json` records the upstream archive, source archive, binary, and license hashes.
`checksums.txt` is the published release checksum list. `LICENSE` preserves the upstream license.
No binary, proxy, full engine, automatic updater, private database, trust record, or raw command history is included.

The installed binary is `~/.local/bin/rtk`.
The configuration is `~/Library/Application Support/rtk/config.toml` on macOS.
It disables telemetry, selects high awareness, and uses the local exclusion list in `config.toml`.
The awareness files use a local adaptation that distinguishes filtered summaries from complete evidence.
Source reads, searches, full diffs, structured output, mutating Git commands, and bridge commands remain raw.
For other commands that require exact output, follow the raw-output guidance in `codex/RTK.md`.
Do not treat filtered output as exact machine data.
Recovery uses the upstream SQLite recall store. Recovery availability depends on the command and output size.

Install with the pinned archive URL and verify its SHA-256 against both provenance and the published checksums.
Keep the license and provenance under `~/.local/share/rtk/releases/1.1.0/`.
Use upstream global init after project-local pretesting and dry-run review:

```sh
rtk init --codex --no-trust-filters --dry-run
rtk init --codex --no-trust-filters
rtk init --auto-patch --no-trust-filters --dry-run
rtk init --auto-patch --no-trust-filters
rtk init -g --codex --no-trust-filters --dry-run
rtk init -g --auto-patch --no-trust-filters --dry-run
rtk init -g --codex --no-trust-filters
rtk init -g --auto-patch --no-trust-filters
```

Run project-local commands in a disposable project, never by repurposing `HOME` or `CODEX_HOME`.
The Codex init command does not accept `--auto-patch`.
The local Claude init adds project awareness. Its global init registers the ordinary-session hook.
Use `RTK_DB_PATH` and `RTK_RECALL_DB` for disposable test data.

The two JSON files contain only the new upstream hook definitions.
Merge them into existing settings. Never replace an existing complete hooks or settings file with these fragments.
Use the installed binary's absolute path in each command.
Codex native approval and sandbox checks still apply to rewritten commands.
New Codex hook definitions require native review and trust for their exact hashes.
Do not edit the trust database or use a trust bypass.
Review the pending RTK entry in the native `/hooks` interface before activation.
After upstream init, restore the adapted `codex/RTK.md` and `claude/RTK.md` files to their live directories.
Merge the personal `claude/CLAUDE.md` instructions without replacing unrelated user instructions or settings.
Validate the adaptation because upstream init can replace it.
Restart ordinary Claude sessions after installation. Restricted bridge calls suppress ambient hooks.

Run `python3.12 tests/check_rtk.py` from the repository root for black-box command checks.
The command saves a private report with inputs, revision, hashes, expected behavior, and observed output.
The checks do not establish native hook activation or subscription-review success.
