<!-- rtk-owned: written by `rtk init --codex`, removed by `rtk init --codex --uninstall` -->

# RTK command output

RTK OSS 1.1.0 uses command hooks to filter supported output.
Filtered summaries can omit details.
Run commands normally. Do not prefix every command with RTK.
Configured exclusions keep selected commands raw.
Host approval, sandbox, and native hook trust requirements remain unchanged.

Use raw output for exact source text, searches, full diffs, machine data, bridge inputs, and complete acceptance evidence.
Use the configured exclusions or `RTK_DISABLED=1 <cmd>` for these commands.
Check exit codes and material diagnostics, including Git command results.
Do not infer success from a short summary.

When material diagnostic details are needed, recover raw output or run the command without filtering.
Recovery is not limited to empty, inconsistent, or garbled output.
Use `rtk recall <hash> --full` when the output provides a recovery reference.
Use `rtk bypass <cmd>` for an unfiltered command that retains RTK tracking.
Before repeating a mutating command, inspect its saved output and resulting state.

Recovery depends on command support and output size.
The default recall limits are 10 MiB per entry, 200 entries, and 30 days of retention.
Small failures can have no recall entry. Expired or oversized output can be unavailable.
Keep required raw acceptance evidence separately from the recall store.

`rtk gain` and `rtk gain --history` report estimated command-output token savings.
These estimates do not measure subscription charges, quota changes, or total task savings.
`rtk discover` reports commands that RTK could filter.

## Source and local policy

Local adaptation of the upstream high-awareness document for the accepted selective-output policy.
Source: RTK OSS 1.1.0, revision `753a3b0e939f2e4490fc24e3a1984010f40a103c`, `hooks/rtk-awareness-high.md`.
The upstream license and provenance remain in `~/.local/share/rtk/releases/1.1.0/`.
An upstream init rerun can replace this adaptation. Restore and validate it after that operation.
