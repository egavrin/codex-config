# Claude companion reliability verification

Verified on 2026-10-12. The change covers the restricted companion bridge.
Ordinary Claude Code sessions remain outside this change.

## Behavior

The supervisor now counts increasing positive thinking-token estimates after a verified Opus message start.
Zero, repeated, decreasing, and invalid estimates do not renew inactivity.
The 900-second inactivity default remains unchanged.
Healthy progress has no default total timeout.

The new `preflight --mode review|patch --packet FILE` action validates the complete bundle locally.
It calls no Claude CLI, authentication service, or skill synchronization.
It reports safe field/index diagnostics, total encoded bytes, and sizes for bundle sections.
`run` repeats validation against current inputs.

Failure records distinguish packet, compatibility, authentication, request, response, patch, and cancellation stages.
Counters and fixed reason codes contain no provider content.
Raw streams, stderr, and thinking text remain excluded.

The root permits one focused repair. It stops after authentication failure, a quota rejection, a stall, or an unsuccessful repair.
Scope, baseline hashes, and Git checks remain required.
The bridge applies no patch.

## Verification

Run the reproducible workflow checks from the snapshot root:

```bash
python3 codex/skills/claude-collab/scripts/test_bridge.py
```

All 135 cases passed, including 32 reliability cases.
The fixtures test complete helper workflows and make no real model request.
An existing healthy-progress fixture exposed a cadence race in its heartbeat assertion.
The final fixture uses an offset cadence and preserves its timeout and progress assertions.
Unknown events also fail to renew inactivity and expose no event content.
The new tests reproduced estimate-only timeout failure before implementation.
An additional zero-estimate test reproduced false progress before the native repair.

The installed skill and snapshot passed skill validation.
Metadata, local references, and the shared Claude link passed checks.
The diff has no whitespace errors.
Authentication, isolation, cleanup, source boundaries, and patch acceptance functions retain their previous syntax trees.
Configuration hashes remain unchanged.

Two temporary real checks used Claude Code 2.1.296 and resolved to `claude-opus-5-5` with requested High effort:

| Check | Duration | Observed result |
| --- | ---: | --- |
| Review | 16.209 seconds | Identified the missing quantity check, returned no diff, and changed no source. |
| Patch | 13.150 seconds | Simplified the Boolean branch and passed baseline, Git, and CLI output checks. |

The patch workflow tested integer inputs from -4 through 4 before and after application.
Only Codex applied the patch in the temporary workspace.
Both real requests reported thinking-token estimate events through the new supervisor.
Estimates are not final token usage.

## Implementation route and limits

The effective root was GPT-6.1 Sol with High reasoning.
The runtime did not expose its service tier.
Claude produced the initial implementation.
Its one focused repair completed, but its patch failed Git validation and was not applied.
One native Astra High owner completed the zero-estimate remainder.
The root inspected that change and ran acceptance.
This companion-to-native fallback is not a pure delegated benchmark.

Two small real checks do not establish a general reliability rate or token savings.
Provider failures and invalid patches remain possible.
The new diagnostics cannot reconstruct discarded historical streams.

[Machine-readable results](claude-companion-reliability.json) contain source hashes and case outcomes.
Private artifacts remain outside this snapshot.
