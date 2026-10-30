# Codex config

Personal Codex configuration for `egavrin`. This repository contains a macOS
configuration snapshot. Routing, memory models, RTK, and Claude instructions were updated on
October 30, 2026. Unrelated machine settings retain their existing snapshot.

## Shared writing profile

The user instructions derive from ASD-STE100 Issue 9, dated 15 January 2025.
The profile applies to agent messages, responses, skills, and new technical documents.
An explicit request for another output language takes precedence.

The source is the [official Issue 9 standard](https://asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).
Its SHA-256 is recorded in the rule map.
This repository contains original explanations and software examples.
It does not contain the standard PDF or a copy of its dictionary.
The derived profile has no ASD approval or certification.

Read these documents:

- [Shared profile](codex/skills/writing-for-agents/references/controlled-english.md).
- [Map of all 53 writing rules](codex/skills/writing-for-agents/references/ste-rule-map.md).
- [Software terms and agent extensions](codex/skills/writing-for-agents/references/software-terms.md).

The instructions preserve exact commands, identifiers, source data, quotations, and required product text.
The profile does not change task scope, permissions, model settings, or routing.
Codex loads the profile through its global instructions.
Claude imports the same files through [personal instructions](claude/CLAUDE.md).
Every companion request includes the profile, rule map, and terms.
The complete bundle must fit the existing 256 KiB packet limit.

The snapshot contains 20 user skills across two discovery roots:

- `codex/skills/` contains twelve user skills, including the Film Studio snapshot.
- `agents/skills/` contains eight Runpod skills.
- `claude/CLAUDE.md` contains personal Claude instructions.

The live Film Studio skill remains linked to its original repository.
The snapshot contains its files so that publication does not depend on an external link.
No Film Studio commit or push forms part of this update.
Built-in skills, plugin caches, and Claude's provider-managed `synced` directory remain outside this snapshot.

To restore the added discovery root and personal Claude instructions, first preserve existing destination files.
Then copy `agents/skills/` to `~/.agents/skills/` and `claude/CLAUDE.md` to `~/.claude/CLAUDE.md`.
Review independent Claude instructions before replacement.
Run the bridge's `sync-skills` action after the Codex user skills are installed.
Keep existing independent Claude skills when names conflict.
Start new Codex and Claude sessions to load persistent instructions.

## Ponytail plugin

The pinned upstream Ponytail 5.1.0 plugin is installed for Codex and Claude.
Read [the installation guide](docs/ponytail-installation.md) for source, modes, hooks, restoration, and verification.
The [compatibility policy](codex/ponytail-policy.md) preserves existing writing and engineering requirements.
The companion reads selected upstream instructions from the verified source.
It executes no Ponytail scripts or hooks.
The [source lock](docs/ponytail-source-lock.json) records the reviewed revision and file hashes.

## Graphify code discovery

Graphify 0.9.95 is installed globally from revision `92741d162b2094ffc2fed58cfbd8ee823e9da62c`.
Codex and ordinary Claude sessions share the [Graphify skill](codex/skills/graphify/SKILL.md).
Its trigger covers architecture, dependency tracing, and substantial repository discovery.
Tiny edits at known locations use direct source searches.

The launcher uses local code-only extraction, guarded queries, and nonblocking per-project locks.
It uses no model backend, API keys, hooks, watcher, or MCP service.
Read [installation and verification](docs/graphify-installation.md) for restoration, evidence, and limitations.
The [source lock](docs/graphify-source-lock.json) records the revision, dependencies, and adapted file hashes.

## Mandatory Slopo commit review

Codex and ordinary Claude sessions must use the shared [Slopo review skill](codex/skills/slopo-review/SKILL.md) before commits and amendments.
The installed Slopo 0.9.0 CLI uses local Ollama code embeddings with 768 dimensions.
Failed checks, unresolved actionable new duplication, and partial staging block agent commits.
Manual commits and Git hooks remain unchanged.
Read [installation and verification](docs/slopo-installation.md) for restoration, scope, and limits.
The [source lock](docs/slopo-source-lock.json) records the pinned revision, dependencies, model digest, and skill hashes.

## Contents

- `codex/config.toml` — model, MCP, plugin, trusted-project, application, and
  multi-agent settings.
- `codex/AGENTS.md` — the global guide for normal model-aware routing, Context Packets, root acceptance, and named opt-in experiments.
- `codex/agents/` — the normal `sol_implementer_high` role and preserved experimental roles.
  Base configuration registers the read-only `astra_planner_high` and `astra_reviewer_high` roles for planned code.
  Dedicated experimental roles remain available for each named experiment.
- `codex/astra-sol-research.config.toml` — an opt-in CLI overlay for the
  experimental Astra Extra High and Sol-primary research route.
- `codex/astra-terra-standard.config.toml` — a historical comparison route with
  an Astra Medium root and Terra High implementation.
- `codex/luna-astra-implementer.config.toml` — an opt-in comparison route with
  Luna xHigh as root and one fresh-context Astra Medium implementer.
- `codex/luna-sol-astra-escalation.config.toml` — an opt-in comparison route
  with Luna xHigh as root, Sol Medium as implementer, and Astra Medium only as
  an evidence-gated escalation.
- `codex/luna-terra-context-sol-astra.config.toml` — an opt-in comparison route
  that conditionally inserts Terra Medium Fast context compaction before the
  same Standard Sol and evidence-gated Astra owners.
- `codex/terra-luna-sol-astra.config.toml` — an opt-in sequential experiment
  with Terra Medium Fast as glue, dedicated Luna Medium Fast evidence and
  acceptance roles, Standard Sol implementation, and evidence-gated Astra.
- `codex/rules/` — local command-execution rules.
- `codex/skills/` — selected user skills: `gh-address-comments`, `gh-fix-ci`,
  `hatch-pet`, `repo-modernizer`, `code-simplifier`, `codebase-design`,
  `improve-codebase-architecture`, `writing-for-agents`, `claude-collab`, `graphify`, `slopo-review`, and `film-studio-workflow`,
  including their scripts, resources, provenance, and bundled licenses where present.
- `agents/skills/` — eight Runpod skills from the existing `~/.agents/skills` discovery root.
- `claude/` — personal instructions with shared profile imports and adapted RTK awareness.
- `codex/RTK.md` and `integrations/rtk/` — adapted awareness, pinned configuration, hook fragments, license, and provenance.
- `docs/controlled-english-verification.md` — migration checks, limitations, and reproduction commands.

The normal default is `gpt-6.1-terra` with `high` reasoning and Standard service tier (`default`).
Desktop and runtime model, reasoning, and tier overrides remain authoritative.
All normal code changes go to Sol High with a focused self-check.
Planned code also uses Astra High planning and read-only review.
The root integrates changes and owns acceptance.
The configured ceiling is 32 open child threads, excluding the root, with a depth setting of one.
The ordinary policy permits one active child at a time. Completed owners can remain idle.
Named experiments retain their own route and lifecycle rules.
Approval remains `never`, and the sandbox remains `danger-full-access`.
Memory extraction uses `gpt-6-luna`. Memory consolidation uses `gpt-6.1-terra`.
The [October 21 routing audit](docs/claude-routing-audit-20261021.md) remains historical evidence for the previous policy.

The repository intentionally excludes authentication data, tokens, task
history, databases, memories, attachments, automations, downloaded plugins,
system skills, and other project-specific instructions. The requested Film Studio
skill snapshot is included. The assets for the selected `custom:rivet` pet are not included;
only its selection remains in the configuration snapshot.

The global guide favors the simplest maintainable solution that meets the
requirements, existing project facilities, and suitable maintained libraries.
It checks documentation for the project's actual API or library version when
behavior is unfamiliar or version-sensitive. Verification remains proportional
to risk; existing deterministic checks are not duplicated without a reason.

For subagents, the guide already uses role-specific model and reasoning
settings, `fork_turns="none"` with a self-contained Context Packet, and
event-driven waits without routine status polling. The external suggestion
`fork_context=false` is not the parameter used by this Codex spawn interface.
These practices reduce avoidable overhead after a native subagent starts; they
do not make `spawn_agent` available in a session where that mechanism is absent.

## Orchestration model

The normal profile is `PROFILE: TERRA_ASTRA_SOL_REVIEW`.
Terra coordinates app work, visual artifacts, bounded prose, questions, scope, and acceptance.
All normal code changes, including tiny edits, use `sol_implementer_high` with GPT-6.1 Sol High on Standard tier.
A Sol root implements directly and does not create another Sol agent.
Other effective root overrides remain authoritative.
A `bpy` helper for an app artifact remains app work. Software and add-on development count as code.
Substantive read-only technical work goes to Sol.
Small obvious edits use Sol without the planner or reviewer.

Planned code uses this sequence:

1. The root collects bounded evidence and forms the Context Packet.
2. `astra_planner_high` returns a read-only plan with bounded packages and verification criteria.
3. Sol High implements the relevant plan slice and runs a focused self-check.
4. `astra_reviewer_high` reviews the plan, completed diff, affected contracts, and check evidence without edits.
5. The root checks the findings and runs proportionate deterministic acceptance checks.

Both Astra roles use `gpt-6-astra`, `high`, and `default` with fresh contexts.
Use this route for a user-requested code plan, a material design decision, a cross-component change, or ordered implementation packages.
The planned-route triggers take precedence over the small-edit shortcut.
In Plan Mode, stop after the plan without edits or implicit implementation.
Outside Plan Mode, continue authorized implementation without an extra approval step.
Only the root dispatches agents. Sol sends planning or review requests to the root.
The root returns at most one ordinary repair to the same Sol owner, then requests a focused recheck from the same reviewer.
Astra planning and review do not authorize Astra implementation.
Report a complete planned route as `<effective-root>-astra-sol-review`.

One child works at a time. Completed owners remain idle through review and acceptance.
Preflight capacity for the planner, each required Sol owner, and the reviewer within the same 32-child cap.
In Plan Mode, reserve only the planner slot.
If the plan requires more slots than available, stop before implementation and report the missing capacity.
If native close or release is unavailable, report that limit and retain completed owners idle within the cap.
Completion, interruption, and archiving do not prove that a slot was released.
Do not evade capacity through another session, visible task, fork, or nested CLI.
Report each unavailable stage and the actual completed route.
For planned work, continue only with a user-authorized fallback and disclose every omitted stage.
Do not claim the full planned route completed when a required stage was unavailable.
Fresh sessions must load the new roles before the root can dispatch them.
Saved configuration and static checks alone do not prove runtime dispatch or sandbox enforcement.

Do not request Claude automatically.
Companion calls require an explicit Claude request or `$claude-collab` invocation.
The skill keeps `allow_implicit_invocation: false`.
Subscription-only authentication and existing bridge isolation remain required for manual requests.
The bridge uses no API fallback and does not read `~/.env` or change authentication, billing, or Extra Usage.
Companion requests cannot overlap a native child.
No automatic Astra implementation fallback, separate tester, additional reviewer, or nested delegation is permitted.
All named experiments and experimental Astra role files remain preserved.

## Routing benchmark

On September 11, 2026, six routes were run from the same clean benchmark commit
against the same deterministic deployment-planner task. Every implementation
passed the four public tests and seven external acceptance tests. `Model traffic`
below is the sum of uncached input and output tokens for the root and all spawned
agents; it is a comparison metric, not a documented Codex quota formula.

| Route | Wall time | Model traffic | Astra used | Spawned agents | Result |
|---|---:|---:|:---:|---:|:---:|
| Fast Luna → Context Packet → Standard Sol | **148.12 s** | 84,852 | No | 1 | 11/11 |
| Fast Terra → Fast Luna evidence → Standard Sol → Fast Luna acceptance | 170.89 s | 124,437 | No | 3 | 11/11 |
| Luna → Astra | 215.52 s | 83,916 | Yes | 1 | 11/11 |
| Astra → Terra → Luna tester | 243.13 s | 140,213 | Yes | 2 | 11/11 |
| Luna → Sol before Context Packet | 247.27 s | 87,863 | No | 1 | 11/11 |
| Standard Luna → Context Packet → Sol | 291.75 s | **83,486** | No | 1 | 11/11 |

In this single controlled task, the then-selected Fast-Luna candidate was 39.1%
faster than the previous Astra orchestrator route and used 39.5% less measured
model traffic.
Compared with the otherwise equivalent Standard-Luna Context Packet route, Fast
Luna was 49.2% faster with 1.6% more measured traffic. These are preliminary
single-run observations: model latency varies, the repository was intentionally
small, and the whole-percent subscription quota display cannot attribute exact
quota consumption to one run. Repeat the comparison on real medium and large
tasks before treating the percentages as general performance guarantees.

## Experimental Astra-Sol profile

`codex/astra-sol-research.config.toml` is an opt-in CLI overlay for experiments
that need Astra Extra High as root and Sol Medium as the primary subagent. It is
not activated by a normal Codex Desktop start. Invoke it explicitly after placing
the file in `~/.codex/`:

```sh
codex --profile astra-sol-research
```

The profile supplies the marker `EXPERIMENT: ASTRA_SOL_RESEARCH`, which activates
the corresponding policy in `codex/AGENTS.md`. It keeps a global cap of two live
spawned threads. A selected Sol senior executor may receive one explicitly
granted Research Slot for a Luna Medium read-only investigator; the slot is
withheld by default, counts toward the global cap, and permits no further nesting.

## Experimental Luna-Astra profile

`codex/luna-astra-implementer.config.toml` tests the inverse orchestration model:
Luna xHigh gathers a bounded Context Packet and passes it to one fresh-context
Astra Medium agent, which owns technical planning and implementation. Luna then
inspects the diff and runs acceptance testing. The experiment prohibits
additional agents and nested delegation so its quota and quality results remain
easy to attribute.

Start a new isolated CLI task with:

```sh
codex --profile luna-astra-implementer -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

Use a task that is large enough to justify implementation delegation but has
deterministic acceptance tests. For a useful comparison, run a separate task of
similar scope through the normal profile, record quota before and after each
run, and compare completion, test results, wall time, model turns, and per-model
token usage from the local session logs. Do not reuse or resume either thread;
each arm needs a fresh root context.

The external claim being tested is a 40–70% quota reduction. Treat that range as
a hypothesis rather than a guarantee; repository shape, task complexity, prompt
length, retries, and the product's quota accounting can materially change it.

## Experimental Luna-Sol-Astra profile

`codex/luna-sol-astra-escalation.config.toml` tests a cheaper primary
implementation route. Luna xHigh first gathers a bounded Context Packet with
relevant files, contracts, evidence, tests, and acceptance criteria. One
fresh-context Sol Medium agent then owns technical planning and implementation,
using that packet without repeating broad discovery. The packet has no fixed
size limit: it is proportional to the task and excludes only irrelevant or
duplicated context. Sol runs only a lightweight focused check, and Astra Medium is
called only when Sol finishes with concrete evidence for a narrowly isolated
unresolved package. Sol and Astra never overlap, neither may create nested
agents, and Luna owns final acceptance testing.

Start a new isolated CLI task with:

```sh
codex --profile luna-sol-astra-escalation -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

Compare this arm with both the normal profile and the Luna-Astra profile. In
addition to quota, quality, model turns, token usage, repairs, and wall time,
record whether Astra escalation occurred and what concrete blocker justified it.
The preferred outcome is a correct Sol implementation without any Astra call;
an Astra escalation is successful only when it resolves a documented hard
remainder without repeating completed Sol work.

## Experimental conditional Terra context profile

`codex/luna-terra-context-sol-astra.config.toml` is a historical comparison
route with a Luna xHigh Fast root, mandatory Standard Sol owner for every Delegated
package, evidence-gated Standard Astra escalation, and Luna-owned acceptance.
Its routing variable is whether a read-only Terra Medium Fast compactor
transforms Luna's Evidence Bundle into the Context Packet before Sol. It does
not change the normal Terra-root route.

The refined Expected-Compression Gate permits Terra only after Luna has gathered
the relevant context and the evidence supports an expected packet reduction of
about 40 percent or selection of a provenance-linked subset that prevents
otherwise necessary broad Sol discovery. Multiple components or
schema/API/codegen/documentation coupling alone no longer triggers Terra. An
incomplete bundle gets at most one focused Luna read; technical decisions go
directly to Sol because Terra is a read-only compactor, not a designer. Terra
must report input/output word counts, reduction ratio, retained evidence,
removed noise, and provenance, or decline when the expected benefit is not
credible.

Sol treats the packet as working context and may inspect exact edit locations
and directly connected definitions. Broader discovery requires naming the
incomplete, contradictory, stale, or decision-insufficient packet field that
justifies it. Luna keeps Sol open through acceptance, inspects affected
cross-contract boundaries, and runs proportionate deterministic checks without
a verifier child. One ordinary failure returns as an evidence-rich delta to the
same Sol thread; Sol closes only after success or before an Astra escalation.

Start a fresh isolated task with:

```sh
codex --profile luna-terra-context-sol-astra -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

The first controlled two-arm protocol used
`experiments/context-routing-ab-20260911`: start both arms
from their identical clean commit, give each the same `TASK.md` prompt, run the
then-baseline arm with `luna-fast-sol-astra-standard` and the comparison arm
with `luna-terra-context-sol-astra`, never resume a session, and evaluate each
with `python3 acceptance_test.py /absolute/path/to/arm`. Record wall time,
per-model traffic, effective service tiers, child sequence, repairs, Astra use,
and all acceptance results before adding any conclusions.

The refined policy has a separate, deliberately compression-heavy protocol in
`experiments/context-compression-ab-20260911`. Its repositories include a large
noisy incident corpus around a bounded Python fix so the gate, Terra's measured
reduction, and Sol's discovery discipline can be observed. Use that directory's
README and acceptance runner for new A/B runs.

### Refined compression-heavy A/B result (September 11, 2026)

One fresh run per arm used the same clean fixture commit
`179111c3c802e71a78ccb46ba1008cf687e14d80`, identical prompt, and no resume.
The baseline ran first at 18:48 Europe/Moscow; the refined conditional-Terra arm
ran second at 18:52. The incident corpus contained 3,090 whitespace-delimited
words around a repair bounded to two production files. These single samples are
directional, not statistically stable.

| Metric | Luna Fast -> Sol Standard | Luna Fast -> Terra Fast -> Sol Standard |
|---|---:|---:|
| Wall time | 225.10 s | 344.30 s |
| External acceptance | 8/8 | 8/8 |
| Public tests | 4 passed | 4 passed |
| Uncached input + output, root | 81,561 | 115,320 |
| Uncached input + output, implementation Sol | 35,633 | 30,550 |
| Uncached input + output, Terra | 0 | 33,466 |
| Total measured model traffic | 117,194 | 179,336 |
| Sol tool calls before first production edit | 1 | 2 |
| Repair follow-ups | 0 | 0 |
| Astra escalations | 0 | 0 |

The refined gate fired for an expected high reduction in duplicated raw traces,
stale hypotheses, and unrelated incidents. Terra measured a reduction from
3,090 input words to a 726-word provenance-linked packet, or 76.50 percent, and
retained the authoritative `CURSOR-3`, `OBS-17`, handshake, and event IDs. Sol
did not reread the evidence corpus in either arm. Its measured traffic fell by
14.3 percent with Terra, but it used two tool calls before its first edit versus
one in the baseline. Both arms passed every external acceptance check without a
repair or Astra escalation.

The reduction did not amortize the orchestration cost: total measured traffic
rose by 53.0 percent and wall time rose by 53.0 percent. Root traffic also rose
by 41.4 percent because Luna still had to read and package the complete evidence
before Terra could transform it. Coarse weekly account usage moved from 11
percent before both arms to 12 percent afterward and cannot be attributed
precisely between arms. Rollout metadata confirmed Luna xHigh, Terra Medium, and
Sol Medium; it did not emit service-tier fields, so Fast/Standard remain pinned
configuration values rather than telemetry-confirmed values.

Conclusion from the refined protocol: the Expected-Compression Gate works and
Terra can produce a materially smaller, provenance-preserving packet, but this
architecture still loses on total traffic and latency when Luna has already
read and understood the raw corpus. At that stage, the result supported the
then-current Luna-to-Sol default. Keep this profile opt-in only for cases where
the packet will be reused by several costly downstream owners, or where
compaction is expected to prevent a repair or Astra escalation; a single
bounded Sol implementation does not justify the extra hop.

### Preliminary context-heavy A/B result (September 11, 2026)

One fresh run per arm used the same clean fixture commit
`c7eab2161c5768c79bffec11f990062e6a0c13e5`, identical prompt, and no resume.
The baseline ran first at 18:13 Europe/Moscow; the conditional-Terra arm ran
second at 18:19. These single samples are directional, not statistically stable.

| Metric | Luna Fast -> Sol Standard | Luna Fast -> Terra Fast -> Sol Standard |
|---|---:|---:|
| Wall time | 353.69 s | 582.65 s |
| External acceptance | 7/8 | 8/8 |
| Public tests | 8 passed | 7 passed |
| Uncached input + output, root | 81,684 | 112,439 |
| Uncached input + output, implementation Sol thread | 56,420 | 53,561* |
| Uncached input + output, Terra | 0 | 26,255 |
| Total measured model traffic | 138,104 | 192,255 |
| Sol tool calls before first production edit | 1 | 3 |
| Repair follow-ups | 0 | 1 |
| Astra escalations | 0 | 0 |

The first-protocol conditional gate fired for multiple component/instruction scopes and for
schema/API/generated-contract/documentation coupling. Terra returned roughly
1,046 words of assistant output, so this run did not demonstrate meaningful
packet compaction. Sol performed more discovery before its first edit, total
traffic rose by 39%, and wall time rose by 65%. The extra acceptance point came
from more extensive root acceptance and a repair, not from proven lower Sol
discovery. The baseline's only external failure was documentation wording:
`must strictly increase` did not match the hidden check for `strictly
increasing`.

`*` The Sol rollout was resumed after being closed and the runtime warned that
the resumed model changed from Sol to Luna. Its aggregate traffic therefore
contains the repair under that runtime-controlled model change. The profile now
keeps Sol open through root acceptance to preserve the pinned role on repair.
Rollout metadata confirmed Luna xHigh, Terra Medium, and Sol Medium initially;
it did not emit a service-tier field, so Fast/Standard remain pinned
configuration values rather than telemetry-confirmed values. Coarse weekly
account usage moved from 10% before both arms to 11% after both arms and cannot
be attributed precisely between arms.

At that stage, the first protocol supported retaining the then-current
Luna-to-Sol default. The conditional profile remained opt-in pending the refined
protocol. The first run improved the hidden acceptance score but failed the
cost, latency, packet-compaction, and Sol discovery success criteria; later
Terra-root evidence below superseded that routing decision.

## Historical Terra Medium Fast branch

This section records the September 11 Terra Medium Fast comparison. The current
ordinary route uses native model-aware delegation as described above. In this historical branch, Direct work remained in Terra. For Delegated
work, Terra performed one
bounded evidence pass, directly forms a provenance-preserving Context Packet,
and delegates exactly once to Standard Sol Medium. Terra keeps Sol open through
root-owned acceptance for at most one evidence-rich repair. Standard Astra
Medium is available only after Sol provides concrete evidence for a narrow hard
remainder and Terra closes Sol first. This route has no Luna child, tester,
explorer, context compactor, second opinion, or nested delegation.

The historical run used the then-installed configuration (the current default
selects the ordinary route documented above):

```sh
codex -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

### Preliminary Terra-root A/B result (September 11, 2026)

One fresh run per arm used the same clean fixture commit
`179111c3c802e71a78ccb46ba1008cf687e14d80` and identical `TASK.md` prompt. The
Terra-root experiment ran first and the Luna-root baseline ran second. Both arms
used one Standard Sol Medium implementer, with no repair follow-up and no Astra
escalation.

| Metric | Terra Medium Fast → Sol Standard | Luna xHigh Fast → Sol Standard |
|---|---:|---:|
| Wall time | **122.83 s** | 200.45 s |
| Public tests | 4/4 | 4/4 |
| External acceptance | 8/8 | 8/8 |
| Root uncached input | 36,853 | 51,143 |
| Root output | 4,865 | 9,055 |
| Root measured traffic | **41,718** | 60,198 |
| Sol uncached input | 26,410 | 20,641 |
| Sol output | 3,357 | 4,900 |
| Sol measured traffic | 29,767 | **25,541** |
| Total measured traffic | **71,485** | 85,739 |
| Sol tool calls before first production edit | 2 | 3 |
| Repair follow-ups | 0 | 0 |
| Astra escalations | 0 | 0 |

Rollout metadata confirmed `gpt-5.6-terra` at Medium reasoning for the
experimental root, `gpt-5.6-luna` at xHigh reasoning for the baseline root, and
`gpt-5.6-sol` at Medium reasoning for both implementation children. The rollout
tier field was null, so Fast roots and Standard/default Sol remain configuration
pins rather than telemetry-confirmed tiers.

Both Sol runs limited inspection to exact code and tests and did not reread the
raw evidence corpus. During acceptance, the Terra root initially wrote an
incorrect focused probe assumption about a legacy scalar checkpoint. It
correctly classified the resulting failure as a harness error, corrected the
probe without a Sol repair, and then passed. The Luna-root arm additionally
prevalidated the full event batch so a later invalid cursor could not cause
partial mutation. The external eight-test suite does not cover multi-event
atomicity, so this is a qualitative robustness difference rather than a scored
acceptance advantage.

Compared with the Luna-root baseline, the Terra-root route used 16.62 percent
less total measured traffic and completed 38.72 percent faster. Terra root
traffic was 30.70 percent lower, while its Sol traffic was 16.55 percent higher.
Scored quality was identical. The coarse account quota display was 13 percent
before and after both runs, so it cannot attribute consumption to either arm.

This preliminary run met the experiment's one-run success thresholds: equal
acceptance, more than 15 percent lower total traffic, lower wall time, and no
added repair or escalation. It did not alone justify promotion, so the next
confirmation used the medium and large context-heavy tasks below, including
multi-event atomicity and acceptance quality.

### Real-task case A: symlink ancestry safety

Clean arms used seed `7882b0320fc2fcc3cbd8db0b6ab953ad033ce7ca`
and identical prompts. The Luna-root arm ran first and the Terra-root arm ran
second.

| Metric | Terra Medium Fast → Sol Standard | Luna xHigh Fast → Sol Standard |
|---|---:|---:|
| Wall time | **318.49 s** | 547.34 s |
| Root measured traffic | **65,637** | 165,327 |
| Sol measured traffic | **69,986** | 99,934 |
| Total measured traffic | **135,623** | 265,261 |
| Repair follow-ups | 1 | 1 |
| Astra escalations | 0 | 0 |
| Transaction tests | 4/4 | 6/6 |
| Full workflow tests | 61/61 | 63/63 |
| Token-report tests | 8/8 | 8/8 |
| External acceptance | **7/8** | 3/8 |

The Luna arm's repair addressed a macOS path alias, but its final protection
depended on callers supplying explicit `owned_roots`. It therefore missed all
five direct transaction-API cases involving an existing parent below a higher
ancestor symlink. The Terra arm caught all five intended symlink escapes, but
over-rejected an ordinary macOS temporary path because the system alias
`/var → /private/var` appeared in its ancestry. That failure is a real
portability defect, not a harness error. Terra used 48.87 percent less total
measured traffic and completed 41.81 percent faster; its quality was higher but
still imperfect.

### Real-task case B: observed runtime metadata reporting

Clean arms used seed `db084644ecd4303abe0447d7a05c37850d159674` and
identical prompts. The valid Terra-root arm ran first and the isolated Luna-root
arm ran second.

| Metric | Terra Medium Fast → Sol Standard | Luna xHigh Fast → Sol Standard |
|---|---:|---:|
| Wall time | **235.90 s** | 355.58 s |
| Root measured traffic | **32,481** | 112,867 |
| Sol measured traffic | 60,503 | **47,228** |
| Total measured traffic | **92,984** | 160,095 |
| Repair follow-ups | 0 | 0 |
| Astra escalations | 0 | 0 |
| Token-report tests | 10/10 | 10/10 |
| Full workflow tests | 58/58 | 58/58 |
| External acceptance | 4/4 | 4/4 |

Terra used 41.92 percent less total measured traffic and completed 33.66
percent faster with identical scored quality. A first Luna attempt is excluded
from every comparison because its root read the completed sibling Terra diff,
creating benchmark protocol leakage. It was interrupted after 108.48 seconds
and 110,969 root-reported traffic. The valid Luna rerun used an isolated
checkout.

The optional repository `companion` role was unavailable during the valid Luna
run (`unknown agent_type companion`), so Luna performed the documentation intake
directly. Terra followed its experimental route without a Companion as designed.
This is a runtime limitation to retain with the result, not an implementation
failure.

### Three-pair aggregate

The valid evidence now consists of the relay fixture above and the two real-task
cases:

| Pair | Terra traffic reduction | Terra wall-time reduction | Acceptance |
|---|---:|---:|---|
| Relay reconciliation | 16.62% | 38.72% | Equal, 8/8 each |
| Symlink ancestry safety | 48.87% | 41.81% | Terra higher, 7/8 vs 3/8 |
| Runtime metadata report | 41.92% | 33.66% | Equal, 4/4 each |
| Median | **41.92%** | **38.72%** | Terra never lower |

Repairs were identical within every pair: 0/0, 1/1, and 0/0. No valid arm used
Astra. Acceptance was equal in two pairs and higher for Terra in one, although
the security result remains imperfect at 7/8. The account's coarse quota display
moved from 14 percent before the four-arm real-task experiment to 16 percent
afterward; that interval includes the excluded contaminated Luna attempt and
cannot be attributed to an individual arm.

The predeclared promotion threshold was met empirically across these three valid
pairs, so Terra Medium Fast was promoted to the normal root route at that time. The
macOS alias portability defect remains a product finding from the security case,
and the contaminated Luna attempt remains excluded as a benchmark-isolation
failure; neither adds fixture-specific logic to the production routing policy.
Rollout `service_tier` was null throughout, so Fast and Standard/default tiers
remain configuration pins rather than telemetry-confirmed values.

## Experimental Terra-Luna-Sol-Astra profile

`codex/terra-luna-sol-astra.config.toml` tests a strictly sequential route in
which Terra Medium Fast remains lightweight glue. For Delegated work, a fresh Luna
Medium Fast collector returns an evidence-only dossier; Terra compacts it into a
Context Packet; Standard Sol Medium plans and implements; and Standard Astra
Medium is available only for a narrow remainder after concrete Sol escalation
evidence. A fresh Luna Medium Fast verifier then runs acceptance without
repairing production code. Tiny bounded edits may go directly to the dedicated
Luna light worker. All children are explicitly configured, no child may spawn,
and only one child works at a time.

The first controlled deployment-planner run completed in 170.89 seconds with
124,437 measured model-traffic tokens, no Astra escalation, and all 11 checks
passing. The intended sequence was observed: Terra root, Luna evidence
collector, Standard Sol implementer, then a fresh Luna acceptance verifier.
Compared with the earlier Fast-Luna Context Packet route on the same benchmark,
this run was 15.4% slower and used 46.7% more measured model traffic. The extra
independent evidence and acceptance phases did not improve the already-perfect
deterministic result on this small task, so this profile should remain
experimental until medium or large tasks demonstrate that the added context
discipline reduces expensive retries or failures. Model and reasoning values
were present in rollout metadata; service tiers were pinned in role
configuration but were not emitted in the inspected rollout records.

After restoring the profile and its role files, start a fresh isolated task:

```sh
codex --profile terra-luna-sol-astra -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

For a controlled comparison, copy the same clean task state into a new arm for
each route, use the same task prompt and external acceptance command, and do not
resume or reuse sessions. Record wall time, per-model rollout and token traffic,
service tier, child sequence, repairs, acceptance results, and whether Astra was
used. Do not infer general latency or quota savings from this single small-task
run.

## Shared skills and explicit Claude requests

The global user-skill library lives in `~/.codex/skills`. Codex uses `$skill-name`;
ordinary Claude Code sessions use `/skill-name` through individual symlinks under
`~/.claude/skills`. The companion creates these links after installation and before
requests, preserves independent Claude skills on name conflicts, and excludes
hidden/system directories and plugin caches.

| Skill | Purpose |
|---|---|
| [code-simplifier](codex/skills/code-simplifier/SKILL.md) | Simplify scoped code while preserving behavior and public contracts. |
| [codebase-design](codex/skills/codebase-design/SKILL.md) | Evaluate module interfaces, architectural seams, dependencies, and alternatives. |
| [improve-codebase-architecture](codex/skills/improve-codebase-architecture/SKILL.md) | Find evidenced architecture improvements and present a visual report. |
| [writing-for-agents](codex/skills/writing-for-agents/SKILL.md) | Improve skills, AGENTS.md, and linked agent instructions without dropping requirements. |
| [claude-collab](codex/skills/claude-collab/SKILL.md) | Send explicit packages to Claude Opus High. Codex owns acceptance. |

The first four skills allow automatic selection and explicit invocation. Claude Collab keeps `allow_implicit_invocation: false`.
Companion calls require an explicit request. For example:

```text
Use $claude-collab and $codebase-design to get Claude's alternative view of the architecture.
Use $claude-collab and $code-simplifier to simplify the current changes without changing behavior.
```

After restoring the skills to `~/.codex/skills`, create the shared links and check
the installed CLI without sending a model request:

```sh
python3 ~/.codex/skills/claude-collab/scripts/bridge.py sync-skills
python3 ~/.codex/skills/claude-collab/scripts/bridge.py doctor
```

Task size, quota, and native failure do not authorize companion requests.
The following requirements apply to all authorized Claude requests.
Claude Collab requires Python 3.9+, Git, a supported installed Claude Code CLI,
and an existing `claude.ai` subscription login. It explicitly requests Opus High,
fresh restricted requests without tools, explicit skill/source packets, a
15-minute inactivity watchdog, and optional total budgets.
No fixed request or retry count applies.
Use further calls for a concrete task need, including review after fixes.
Do not repeat a request while an authentication, quota, CLI, or inactivity failure still blocks it.
Codex checks returned patches before applying and testing them. Companion requests cannot overlap a native child.
Opt-in experimental routes keep their own rules. Live sanitized progress snapshots and summaries appear every
30 seconds; heartbeats never renew model inactivity. Healthy streams have no
default total wall-clock cap. Higher effort does not imply lower latency.
This external route is reported as `<effective-root>-claude`.

For other services, the global guide preserves a non-empty environment credential
and loads only missing required variables from `~/.env` as dotenv data. Claude
Collab is a subscription-only exception: it never reads that file or falls back
to API credentials. It does not change billing or enable Extra Usage; subscription
authentication cannot disable overages already enabled on the account.

The Jev shadow policy retains preview-and-digest approval and permits an existing
`TYPESAFE_API_KEY` without rotation before each request. It is opt-in and requires
the separately installed local `~/.codex/jev_router.py`; this repository does not
ship or automatically activate that experimental client.

Private companion state, results, ownership manifests, authentication data, and
machine-specific Claude symlinks are excluded from Git. Restart the relevant agent
if a new session does not discover the installed skills. See the skill references
for source revisions, licenses, packet format, and acceptance rules.

## RTK

[`integrations/rtk/`](integrations/rtk/README.md) records the pinned RTK OSS 1.1.0 integration, license, provenance, configuration, and managed hook fragments.
The upstream hooks support Codex and ordinary Claude sessions. Restricted companion calls retain their existing hook isolation.
Telemetry is disabled. High awareness does not instruct agents to prefix every command.
The local exclusion list preserves raw source evidence, diffs, structured output, Git writes, and bridge packets.
Use raw output whenever exact machine data is required.
Native Codex hook trust remains a separate review action. No trust database or bypass belongs in this snapshot.
The snapshot contains no RTK binary or private database.
`verification.json` preserves prior installation and workflow evidence. It does not record this snapshot update's checks.

## Restore personal Claude instructions

`claude/CLAUDE.md` contains the personal writing, Ponytail, Graphify, Slopo, and RTK instructions.
`claude/RTK.md` contains the local selective-output adaptation for RTK OSS 1.1.0.
These files match the live instructions and contain no credentials or runtime artifacts.

Before restoration, back up existing `~/.claude/CLAUDE.md` and `~/.claude/RTK.md` files.
Compare the saved instructions with existing files, then merge the requested sections and imports.
Preserve unrelated personal instructions. Do not replace the complete Claude settings file.
Merge only the RTK hook fragment into existing settings, as described in [the RTK instructions](integrations/rtk/README.md).
Install the referenced shared skills and `~/.codex/ponytail-policy.md` before activation.
The relative imports resolve under the live `~/.claude` directory after restoration.

Upstream RTK init can replace the awareness documents.
After init, restore `codex/RTK.md` and `claude/RTK.md` to their respective live directories, then validate the adaptation.
Preserve the Codex ownership marker. Complete native hook trust review separately.

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
copy only the contents of `codex/`, remove the two superseded route profiles
from the active directory into that backup, and leave unrelated destination
files in place:

```sh
codex_target="${CODEX_HOME:-$HOME/.codex}"
codex_backup_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-config-backup.XXXXXX")"
mkdir -p "$codex_target"
rsync -av --backup --backup-dir="$codex_backup_dir" codex/ "$codex_target/"
mkdir -p "$codex_backup_dir/obsolete-profiles"
for obsolete_profile in luna-fast-sol-astra-standard.config.toml terra-fast-sol-astra-standard.config.toml; do
  if [ -e "$codex_target/$obsolete_profile" ]; then
    mv "$codex_target/$obsolete_profile" "$codex_backup_dir/obsolete-profiles/"
  fi
done
printf 'Backup of replaced files: %s\n' "$codex_backup_dir"
```

To install only the conditional profile and its dedicated role after the base
configuration is already restored:

```sh
cp codex/luna-terra-context-sol-astra.config.toml "$codex_target/"
cp codex/agents/terra_context_compactor_fast.toml "$codex_target/agents/"
```

Validate the base configuration and every retained named profile without
starting a model session:

```sh
codex_validation_home="$(mktemp -d "${TMPDIR:-/tmp}/codex-config-validate.XXXXXX")"
cleanup_codex_validation_home() {
  if [ -d "$codex_validation_home" ]; then
    find "$codex_validation_home" -depth -delete
  fi
}
trap cleanup_codex_validation_home EXIT HUP INT TERM
cp -R codex/. "$codex_validation_home/"
CODEX_HOME="$codex_validation_home" codex mcp list >/dev/null
for profile in astra-sol-research astra-terra-standard luna-astra-implementer \
  luna-sol-astra-escalation luna-terra-context-sol-astra terra-luna-sol-astra; do
  CODEX_HOME="$codex_validation_home" codex --profile "$profile" mcp list \
    >/dev/null
done
cleanup_codex_validation_home
trap - EXIT HUP INT TERM
```

Open Codex again after the restore. Sign in and reconnect integrations if
needed. Start a new task so the new configuration and global instructions are
loaded into a fresh session.

## Update the snapshot

From the root of this clone, review configuration changes before synchronization.
Merge only intended settings into `codex/config.toml`. Do not copy the complete live configuration.
It can contain secrets, temporary project trust, and unrelated integration values.
Then copy the listed instructions, rules, roles, and selected user skills:

```sh
codex_source="${CODEX_HOME:-$HOME/.codex}"
cp "$codex_source/AGENTS.md" codex/AGENTS.md
cp "$codex_source/astra-terra-standard.config.toml" codex/astra-terra-standard.config.toml
cp "$codex_source/astra-sol-research.config.toml" codex/astra-sol-research.config.toml
cp "$codex_source/luna-astra-implementer.config.toml" codex/luna-astra-implementer.config.toml
cp "$codex_source/luna-sol-astra-escalation.config.toml" codex/luna-sol-astra-escalation.config.toml
cp "$codex_source/luna-terra-context-sol-astra.config.toml" codex/luna-terra-context-sol-astra.config.toml
cp "$codex_source/terra-luna-sol-astra.config.toml" codex/terra-luna-sol-astra.config.toml
for codex_part in agents rules skills/gh-address-comments skills/gh-fix-ci \
  skills/hatch-pet skills/repo-modernizer skills/code-simplifier \
  skills/codebase-design skills/improve-codebase-architecture \
  skills/writing-for-agents skills/claude-collab skills/film-studio-workflow; do
  mkdir -p "codex/$codex_part"
  rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' --exclude='.git' --exclude='.state' \
    "$codex_source/$codex_part/" "codex/$codex_part/"
done
mkdir -p agents/skills claude
rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
  "$HOME/.agents/skills/" agents/skills/
cp "$HOME/.claude/CLAUDE.md" claude/CLAUDE.md
cp "$HOME/.claude/RTK.md" claude/RTK.md
cp "$codex_source/RTK.md" codex/RTK.md
git diff --stat
git diff
```

After an RTK awareness or Claude instruction update, refresh the corresponding hashes in `integrations/rtk/provenance.json`.
Compare the recorded hashes with the snapshot files before committing.

These commands do not propagate deletions from the active configuration into
the snapshot. Apply intended deletions manually. Before committing, inspect the
complete diff, especially MCP environment values, HTTP headers, and command
rules. `.gitignore` excludes common generated files, but it cannot detect
secrets embedded inside tracked TOML or other text files.

```sh
git add codex agents claude docs integrations tests README.md
git commit -m "Update Codex configuration"
git push
```

Synchronization is manual. Creating or cloning this repository does not alter
the active Codex configuration and does not configure automatic GitHub uploads.
