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
  compaction, plus `luna_evidence_collector_fast`, `luna_light_worker_fast`, and
  `luna_acceptance_verifier_fast` for the Terra-Luna-Sol-Astra experiment.
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
  `hatch-pet`, and `repo-modernizer`, including their scripts, resources, and
  bundled licenses where present.

The active default is `gpt-5.6-terra` with Medium reasoning on Fast service tier;
both `service_tier = "fast"` and `[features].fast_mode = true` are set.
For substantial implementation, Terra compacts relevant evidence into a Context
Packet and gives it to one fresh Standard-tier Sol Medium agent. Terra owns final
acceptance while keeping Sol open and idle for one evidence-rich ordinary repair
if needed; Standard-tier Astra Medium is used only for a narrowly isolated
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
Root                       Terra Medium Fast     context collection and acceptance
senior_executor_standard   Sol Medium Standard   primary implementation owner
astra_executor_standard    Astra Medium Standard evidence-gated escalation only
```

Small bounded tasks and narrow reviews use Terra directly without subagents.
Substantial implementation tasks and material branch, pull-request, security,
architecture, regression, or cross-component reviews use one bounded discovery
pass, a task-proportional Context Packet without a fixed word limit, and one
fresh Sol context. Implementation packages receive a lightweight worker-owned
check; review packages are explicitly read-only and report evidence-backed
findings. Terra owns acceptance in both cases. Sol and Astra never overlap, and
neither may spawn another agent.

Sol treats the Context Packet as working context: it may inspect exact edit
locations and directly connected definitions, while broader repeat discovery
requires identifying a specific incomplete, contradictory, stale, or
decision-insufficient packet field. During acceptance, Terra keeps Sol open and
idle, inspects the diff and affected contract boundaries, and runs proportionate
deterministic tests and material edge cases. Terra separates product failures
from harness or environment limitations and, for one ordinary defect, returns
exact expected-versus-observed evidence to the same Sol thread before rerunning
the affected checks. Sol closes after acceptance succeeds or before an Astra
escalation; the default route does not add a separate tester.

Terra Medium Fast was promoted to the normal route after the three valid paired
results documented below. The default is now Terra → Sol → Terra acceptance →
optional Astra, with no Luna child or separate tester.

In the default Terra route, `[agents].enabled = true`, and the first
`senior_executor_standard` spawn is mandatory for every substantive
implementation or review when the session exposes native collaboration and that
exact role. Native collaboration means the session's internal subagent spawn
mechanism. User-visible `create_thread`, `fork_thread`, and
`send_message_to_thread` operations, as well as nested `codex exec`, are not
automatic substitutes; a separate user-visible task is created only when the
user explicitly requests one.

If native collaboration is entirely absent, Terra completes Heavy work and
acceptance directly and discloses
`effective_route = terra-single-agent-fallback` with the reason. If
collaboration exists but the exact role is missing, Terra also labels the
condition as configuration drift and uses that fallback. Temporary occupation
of the one-child slot is not fallback justification: the route waits, reuses,
or closes its own child as appropriate. Normal completion reports
`effective_route = terra-sol-astra`, even when Astra is unused. Fallback
sessions are excluded from valid Terra-to-Sol benchmark comparisons.

The `astra-terra-standard` profile remains available only as a historical
comparison with an Astra Medium orchestrator, Terra High implementation, and an
independently justified Luna High tester. Use `astra-sol-research` only for its
explicitly defined research experiment.

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
route with a Luna xHigh Fast root, mandatory Standard Sol owner for every Heavy
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

## Default Terra Fast to Standard Sol route

`codex/config.toml` is the single source of truth for the normal Terra Medium
Fast route. Light work remains in Terra. For Heavy work, Terra performs one
bounded evidence pass, directly forms a provenance-preserving Context Packet,
and delegates exactly once to Standard Sol Medium. Terra keeps Sol open through
root-owned acceptance for at most one evidence-rich repair. Standard Astra
Medium is available only after Sol provides concrete evidence for a narrow hard
remainder and Terra closes Sol first. This route has no Luna child, tester,
explorer, context compactor, second opinion, or nested delegation.

Start a fresh task with the installed default configuration:

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
pairs, so Terra Medium Fast was promoted to the sole normal root route. The
macOS alias portability defect remains a product finding from the security case,
and the contaminated Luna attempt remains excluded as a benchmark-isolation
failure; neither adds fixture-specific logic to the production routing policy.
Rollout `service_tier` was null throughout, so Fast and Standard/default tiers
remain configuration pins rather than telemetry-confirmed values.

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
