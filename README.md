# Codex config

Personal Codex configuration for `egavrin`. This repository contains a macOS
configuration snapshot updated on September 11, 2026.

## Contents

- `codex/config.toml` — model, MCP, plugin, trusted-project, application, and
  multi-agent settings.
- `codex/AGENTS.md` — the global English-language guide for cost-efficient
  orchestration, including Light and Heavy routes, compact task capsules,
  batching, event-driven waits without polling, and separate implementation and
  verification ownership.
- `codex/agents/` — `worker` (Terra High), `explorer` (Luna Medium), `tester`
  (Luna High), the strictly gated `senior_executor` (Sol Medium), plus
  Standard-tier `senior_executor_standard` (Sol Medium) and
  `astra_executor_standard` (Astra Medium) for the default route, and dedicated
  `terra_context_compactor_fast` (Terra Medium Fast) for conditional context
  compaction, plus dedicated Luna Medium Fast collector, light-worker, and
  acceptance-verifier roles for the Terra-Luna-Sol-Astra experiment.
- `codex/astra-sol-research.config.toml` — an opt-in CLI overlay for the
  experimental Astra Extra High and Sol-primary research route.
- `codex/astra-terra-standard.config.toml` — the previous Astra Medium / Terra
  High default, retained as an explicit fallback and comparison route.
- `codex/luna-astra-implementer.config.toml` — an opt-in comparison route with
  Luna xHigh as root and one fresh-context Astra Medium implementer.
- `codex/luna-sol-astra-escalation.config.toml` — an opt-in comparison route
  with Luna xHigh as root, Sol Medium as implementer, and Astra Medium only as
  an evidence-gated escalation.
- `codex/luna-fast-sol-astra-standard.config.toml` — the same Context Packet
  route with only Luna on Fast service tier and Sol/Astra forced to Standard.
- `codex/luna-terra-context-sol-astra.config.toml` — an opt-in comparison route
  that conditionally inserts Terra Medium Fast context compaction before the
  same Standard Sol and evidence-gated Astra owners.
- `codex/terra-luna-sol-astra.config.toml` — an opt-in sequential experiment
  with Terra Medium Fast as glue, dedicated Luna Medium Fast evidence and
  acceptance roles, Standard Sol implementation, and evidence-gated Astra.
- `codex/rules/` — local command-execution rules.
- `codex/skills/` — selected user skills: `gh-address-comments`, `gh-fix-ci`,
  `hatch-pet`, and `repo-modernizer`, including their scripts, resources, and
  bundled licenses where present.

The active default is `gpt-5.6-luna` with xHigh reasoning on Fast service tier;
both `service_tier = "fast"` and `[features].fast_mode = true` are set.
For substantial implementation, Luna compacts relevant evidence into a Context
Packet and gives it to one fresh Standard-tier Sol Medium agent. Luna owns final
acceptance; Standard-tier Astra Medium is used only for a narrowly isolated
remainder after concrete escalation evidence. The default permits one live
spawned thread and a V1 maximum depth of one. Approval remains `never`, and the
sandbox remains `danger-full-access`.

The repository intentionally excludes authentication data, tokens, task
history, databases, memories, attachments, automations, downloaded plugins,
system skills, and project-specific instructions or skills from other
repositories. The assets for the selected `custom:rivet` pet are not included;
only its selection remains in the configuration snapshot.

## Orchestration model

The default execution model is:

```text
Root                     Luna xHigh Fast        context collection and acceptance
standard_senior_executor Sol Medium Standard   primary implementation owner
astra_executor           Astra Medium Standard evidence-gated escalation only
```

Small bounded tasks and narrow reviews use Luna directly without subagents.
Substantial implementation tasks and material branch, pull-request, security,
architecture, regression, or cross-component reviews use one bounded discovery
pass, a task-proportional Context Packet without a fixed word limit, and one
fresh Sol context. Implementation packages receive a lightweight worker-owned
check; review packages are explicitly read-only and report evidence-backed
findings. Luna owns acceptance in both cases. Sol and Astra never overlap, and
neither may spawn another agent.

In the default Luna route, the first Sol spawn is mandatory for every
substantive implementation or review. Luna may work directly only on the
documented Light exceptions; if classification is uncertain, it chooses Heavy.
The root must report an unavailable role or slot instead of silently taking over
the delegated package. The one-agent concurrency and depth guards remain in
place because they permit Luna to call Sol while preventing nested or overlapping
agent chains.

Use `codex --profile astra-terra-standard` when a task benefits from the previous
Astra Medium orchestrator, Terra High implementation, and an independently
justified Luna High tester. Use `astra-sol-research` only for its explicitly
defined research experiment.

Because a task name alone does not activate a role profile in every collaboration
runtime, `codex/AGENTS.md` also defines explicit model, reasoning, service-tier,
context-transfer, concurrency, and escalation contracts.

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

In this single controlled task, the selected default was 39.1% faster than the
previous Astra orchestrator route and used 39.5% less measured model traffic.
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

### Fast Luna variant

`codex/luna-fast-sol-astra-standard.config.toml` isolates service-tier latency:
Luna xHigh uses Fast, while the Sol Medium implementer and optional Astra Medium
escalation use dedicated role files pinned to Standard. Start it with:

```sh
codex --profile luna-fast-sol-astra-standard -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

Verify the effective service tier of every rollout before comparing results;
otherwise inherited Fast settings could invalidate the experiment.

## Experimental conditional Terra context profile

`codex/luna-terra-context-sol-astra.config.toml` preserves the default route's
Luna xHigh Fast root, mandatory Standard Sol owner for every Heavy package,
evidence-gated Standard Astra escalation, and Luna-owned acceptance. Its only
routing variable is whether a read-only Terra Medium Fast compactor transforms
Luna's Evidence Bundle into the Context Packet before Sol. The existing default
and the full Terra-root profile remain unchanged.

The deterministic Context Complexity Gate requires Terra when evidence crosses
multiple component or instruction scopes; the change couples schema, API,
codegen, or documentation; sources conflict or are stale; a large diff, log, or
trace has a small relevant subset; ownership remains unclear after the bounded
pass; or a direct packet would force Sol to repeat broad discovery. Terra is
skipped for one cohesive component with clear paths, constraints, and tests. An
uncertain case gets one extra focused Luna read; remaining ownership or
constraint ambiguity requires Terra.

Start a fresh isolated task with:

```sh
codex --profile luna-terra-context-sol-astra -C /absolute/path/to/project \
  "Implement the bounded task described here."
```

This profile is experimental. Its controlled two-arm protocol uses
`experiments/context-routing-ab-20260911`: start both arms
from their identical clean commit, give each the same `TASK.md` prompt, run the
default profile against `luna-fast-sol-astra-standard` and this profile against
`luna-terra-context-sol-astra`, never resume a session, and evaluate each with
`python3 acceptance_test.py /absolute/path/to/arm`. Record wall time, per-model
traffic, effective service tiers, child sequence, repairs, Astra use, and all
acceptance results before adding any conclusions.

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

The conditional gate fired for multiple component/instruction scopes and for
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

Conclusion: retain the current Luna-to-Sol default. Keep conditional Terra as an
opt-in experiment for additional medium/large real tasks; this run improved the
hidden acceptance score but failed the cost, latency, packet-compaction, and Sol
discovery success criteria.

## Experimental Terra-Luna-Sol-Astra profile

`codex/terra-luna-sol-astra.config.toml` tests a strictly sequential route in
which Terra Medium Fast remains lightweight glue. For Heavy work, a fresh Luna
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

To install only the conditional profile and its dedicated role after the base
configuration is already restored:

```sh
cp codex/luna-terra-context-sol-astra.config.toml "$codex_target/"
cp codex/agents/terra_context_compactor_fast.toml "$codex_target/agents/"
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
cp "$codex_source/astra-terra-standard.config.toml" codex/astra-terra-standard.config.toml
cp "$codex_source/astra-sol-research.config.toml" codex/astra-sol-research.config.toml
cp "$codex_source/luna-astra-implementer.config.toml" codex/luna-astra-implementer.config.toml
cp "$codex_source/luna-sol-astra-escalation.config.toml" codex/luna-sol-astra-escalation.config.toml
cp "$codex_source/luna-fast-sol-astra-standard.config.toml" codex/luna-fast-sol-astra-standard.config.toml
cp "$codex_source/luna-terra-context-sol-astra.config.toml" codex/luna-terra-context-sol-astra.config.toml
cp "$codex_source/terra-luna-sol-astra.config.toml" codex/terra-luna-sol-astra.config.toml
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
