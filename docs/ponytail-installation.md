# Ponytail installation

This setup installs the unchanged upstream Ponytail plugin for Codex and ordinary Claude Code sessions.
The compatibility policy preserves the existing writing, verification, scope, and routing requirements.

## Source

Repository: https://github.com/DietrichGebert/ponytail
Version: 5.1.0
Revision: 9b58c1ffb790c075ca32e70a89cf1d80588f4abf
License: MIT, Copyright (c) 2026 DietrichGebert.

The source checkout is ~/.codex/third-party/ponytail.
Claude registers that directory as the ponytail marketplace.
Codex registers a local catalogue wrapper that points to the same checkout.
The wrapper avoids the upstream Codex catalogue entry that points to remote main.
It leaves upstream files unchanged.

The checkout stays detached at the reviewed revision.
Claude's user marketplace entry sets autoUpdate to false.
Codex uses a local marketplace, with no remote branch to update.
The plugin managers may keep independent installed copies.
Their registered source remains the same pinned checkout.

## Instructions and commands

Read [the compatibility policy](../codex/ponytail-policy.md) when Ponytail applies.
The six upstream skills remain unchanged.
No duplicate copies are added to the shared user-skill library.
Existing shared skill links and discovery roots remain unchanged.

Codex exposes the plugin namespace:
- $ponytail:ponytail
- $ponytail:ponytail-review
- $ponytail:ponytail-audit
- $ponytail:ponytail-debt
- $ponytail:ponytail-gain
- $ponytail:ponytail-help

Claude exposes the corresponding /ponytail:skill-name commands.
The upstream aliases include /ponytail and /ponytail-review.

The default mode is full.
The core command accepts lite, full, ultra, and off.
Review, audit, debt, gain, and help are one-shot skills.
They do not change the core mode.
The off mode does not disable the existing instructions.

## Hook review

The actual manifest contains three events:
SessionStart, SubagentStart, and UserPromptSubmit.
Codex requires native review and trust before non-managed hooks run.
Open /hooks, inspect the installed Ponytail definitions, and trust their current hashes.
Do not bypass hook trust.

Changed definitions require renewed review.
Installation and activation are separate states.

The native hooks/list response reports these installed definitions:

| Event | Native hash | State |
| --- | --- | --- |
| sessionStart | sha256:7ee5d5ae1f4a9e55f1f429f2960c2f9f32293f198c0e8e2e42b2fb3b4eeda142 | trusted |
| userPromptSubmit | sha256:8c9efc5a5e649c8cdca3f0b7bf4cba81d9717d1bc930c7dbc18b6efd66c7c58c | trusted |
| subagentStart | sha256:7954d675ef3bafd5e5a6073ae51d7de57a08f21340f241c332f99078e955675d | trusted |


The latest native registry reports all three definitions as trusted.
No hook-trust bypass or database edit formed part of this task.
Fresh-session tests examine whether they execute.

The upstream mode state has a known limit.
Concurrent sessions in the same project can share one mode.
The compatibility policy does not change that upstream behavior.

## Companion

The restricted Claude companion does not execute plugin hooks or scripts.
Selected upstream instructions reach it as text from the verified pinned source.
The existing input packet schema, authentication, tools, supervision, and acceptance remain unchanged.
The complete packet includes the selected instructions, compatibility policy, and required references.
The existing 256 KiB limit still applies.

No selected plugin means that its checkout is unnecessary for the request.

## Updates and restoration

Preserve existing settings before restoration.
Clone the source repository into the stated checkout path.
Check out the recorded revision with a detached HEAD.
Register the checkout path in Claude.
Merge claude/ponytail-settings.json into user settings without replacing existing fields.

Restore the Codex catalogue wrapper.
Create its ponytail symlink to ~/.codex/third-party/ponytail, then register the wrapper.
Install ponytail@ponytail with Claude user scope and Codex global scope.
Restore the compatibility instructions and companion changes from this snapshot.
Review hook definitions in the native trust flow after installation.

Do not restore another machine's hook-trust database.

Review a new revision before an update.
Compare source hashes, inspect changed hooks, and repeat the acceptance checks.
Refresh only this marketplace and plugin.
Do not upgrade unrelated plugins.

## Verification

The upstream suite passed 127 main tests and 28 Pi-extension tests.
It ran in an isolated home with the existing bundled Python runtime.
Initial CSV checks failed because the selected Python lacked pandas.
The corrected test environment passed without changing upstream code.

Twenty-two isolated hook workflows passed through the current launcher.
They cover both hosts, four modes, subagent context, and one-shot commands.
The hooks changed no project files.

These results do not establish savings or general model reliability.
The published benchmark describes different test conditions.

The bridge suite passed 103 workflow cases.
The new tests failed against the old helper before implementation.
A real-source gain check exposed a README navigation defect.
Its regression failed before the focused repair and passed afterward.
All six real upstream selections now bundle successfully.

Only the existing skill reader and packet builder changed.
Authentication, isolation, streaming, patch acceptance, and shared synchronization functions stayed unchanged.
