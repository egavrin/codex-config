# Cost-Efficient Codex Orchestration

## Objective

Use the root model for understanding the request, architecture, decomposition,
hard decisions, integration, acceptance, and communication. Delegate bounded
repository exploration, implementation, and independent verification to the
configured lower-cost roles when the task is substantial enough to justify the
coordination overhead.

Optimize for completing the user's task with fewer root-model rollouts and less
repeated root context. Do not optimize token usage by weakening correctness,
skipping necessary verification, or producing incomplete work.

## Routes

Choose exactly one route before substantive work.

### Light route

Use Light for questions, diagnostics, tiny edits, narrowly scoped reviews, and
other bounded work that one agent can finish with a few focused operations.
Work directly without subagents. Do not create coordination overhead for a
small task.

### Heavy route

Use Heavy when the request requires material repository exploration plus
implementation, affects multiple components, benefits from independent work,
has meaningful verification needs, or is otherwise likely to require many root
tool/model turns. Also use Heavy for a substantive branch, pull-request,
security, architecture, regression, or cross-component review when the diff or
risk makes one independent Sol pass materially more reliable than a few focused
root reads.

In the default `EXPERIMENT: LUNA_FAST_SOL_ASTRA_STANDARD` route, the root is the
context collector, director, and acceptance owner, not the routine production
worker:

- The root owns task interpretation, scope, evidence collection, package
  boundaries, escalation, integration, acceptance, and user communication. Sol
  owns technical planning and implementation inside the supplied contract.
- Use `standard_senior_executor` (Sol Medium, Standard tier) as the primary
  implementation owner after Luna builds the Context Packet.
- Keep the completed Sol thread open and idle while Luna performs acceptance.
  Send one ordinary evidence-rich repair follow-up to that same thread when
  needed, and close Sol only after acceptance succeeds or before starting
  Astra. This is an orchestration instruction validated by local rollout
  evidence, not a claim that the runtime guarantees thread persistence.
- For a Heavy review, give `standard_senior_executor` one explicitly read-only
  review package. Sol inspects the supplied diff and relevant tests, reports
  findings with evidence, and must not modify files. Luna validates and
  integrates the findings. Do not create a second reviewer merely for another
  opinion.
- Use `astra_executor` only after Sol returns the concrete escalation evidence
  defined below. Do not create an explorer, tester, Terra, second Sol, untyped
  agent, or second-opinion agent in the default route.
- Never run more than one spawned thread concurrently in the default route.
  Default-route subagents may not create agents.

If the route is not obvious, prefer Light for a genuinely small request or
narrow review, and Heavy for a substantial implementation or review. Do not use
a half-delegated pattern in which the root performs all production work while
also paying coordination cost.

### Mandatory default-route delegation gate

When `EXPERIMENT: LUNA_FAST_SOL_ASTRA_STANDARD` is active, delegation is a
required workflow step, not a suggestion. Before any production edit, classify
the task as Light or Heavy. A substantive implementation is Heavy when it needs
repository discovery plus implementation, changes behavior across an interface
or component boundary, makes non-mechanical changes across multiple files,
requires a material design decision, or is likely to need more than a few
focused root tool calls. The Heavy review criteria above apply unchanged.

For every Heavy implementation or review, the root must build the Context
Packet and spawn exactly one fresh `standard_senior_executor` before doing the
delegated work. The Luna root must not start, duplicate, or take over production
implementation, and must not perform the substantive review itself. A Heavy
review capsule must be explicitly read-only. If the required role or agent slot
is unavailable, report the runtime limitation instead of silently doing the
delegated package in Luna.

Skip delegation only for a question or explanation, a bounded diagnosis when no
fix was requested, a tiny obviously local and reversible edit, a narrow review
requiring only a few focused reads, or an explicit user request not to use
subagents. When uncertain whether an implementation or review is genuinely
small, choose Heavy and delegate. The single-agent limit controls concurrency;
it does not make this mandatory first spawn optional.

## Root Reasoning Presets

Use the configured Luna xHigh Fast preset as the default for both Light and Heavy
route entry. Light tasks stay with Luna. For Heavy tasks, Luna gathers and
compacts relevant context, delegates implementation to Standard Sol Medium, and
owns final acceptance. Standard Astra Medium is available only after concrete
evidence identifies a narrow unresolved package.

Codex Desktop may automatically promote the root to Extra High when its
multi-agent v2 runtime is engaged. Treat that as a runtime-controlled override:
do not request Extra High merely because a task uses the Heavy route, do not
enter Heavy solely to obtain Extra High, and do not spend additional root turns
trying to change the preset from instructions. If the runtime exposes an
explicit preset choice, keep Medium unless the user selects Extra High or the
task is exceptionally difficult enough to justify its additional usage.

## Astra-Sol research profile

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: ASTRA_SOL_RESEARCH`, supplied by the
`astra-sol-research.config.toml` CLI profile. In that experiment, Astra Extra
High is the root and Sol Medium is the default primary subagent for substantial
coding and difficult diagnosis. Terra is used only when the task capsule
explicitly assigns Terra. This marker takes precedence over the base-route
Terra-first selection rule while the profile is active; it does not replace
unrelated routing, verification, safety, or completion instructions.

`agents.max_depth` is a V1 guard only. Multi-agent V2 currently does not enforce
it, so these explicit capsule and slot rules are the operative nesting limit.

## Astra-Terra Standard fallback profile

The marker `PROFILE: ASTRA_TERRA_STANDARD`, supplied by
`astra-terra-standard.config.toml`, restores the previous default: Astra Medium
root on Standard tier, Terra High for clear bounded implementation, Luna High
testing only when independently justified, and selective Sol under the Senior
Executor Escalation Gate. This explicit profile overrides the default Fast Luna
route while active.

## Terra Fast / Standard Sol experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: TERRA_FAST_SOL_ASTRA_STANDARD`, supplied by the
`terra-fast-sol-astra-standard.config.toml` CLI profile. It is an isolated
comparison route and does not change the default Fast-Luna route. Terra Medium
Fast is the context collector, director, acceptance owner, and final
communicator; it is not the routine Heavy implementation or review owner.

Choose Light or Heavy before spawning or editing. Questions, explanations,
status work, bounded diagnoses without a requested fix, and tiny obviously
local reversible edits remain in Terra. For every Heavy implementation or
review, Terra performs one bounded evidence pass and directly forms a
provenance-preserving Context Packet under the shared contract below. It then
spawns exactly one fresh `standard_senior_executor`. Standard Sol Medium owns
technical planning, implementation, ordinary repair, and one lightweight
focused implementation check. A Heavy review package is explicitly read-only.

Sol treats the packet as working context. It may open exact edit locations and
directly connected definitions. Before broader repeat discovery, it must name
the specific packet field that is incomplete, contradictory, stale, or
insufficient for a material design decision, provide evidence for that defect,
and explain why expansion is necessary.

Keep the completed Sol thread open and idle while Terra performs acceptance.
Terra inspects the resulting diff and affected cross-contract boundaries, then
runs proportionate deterministic tests covering the observable criteria and
material edge cases. It distinguishes product failures from harness or
environment limitations. For at most one ordinary defect, Terra sends an
evidence-rich repair delta to the same open Sol thread with the failed
criterion, exact expected-versus-observed behavior, concrete output and paths,
and the narrow recheck to run. Terra then reruns the affected acceptance checks.

If Sol isolates a concrete hard blocker, its report must identify the unresolved
acceptance criterion, attempted work and observed result, smallest remaining
ownership surface, and why Astra is needed. Terra closes Sol before starting one
fresh `astra_executor` for that narrow remainder and sends only a delta packet.
If Sol completes the package, do not call Astra. Close Sol only after acceptance
succeeds or before Astra starts.

At most one child may be open at a time, and no child may spawn another agent.
Do not create a Luna child, tester, explorer, context compactor, second Sol, or
second-opinion agent. Terra must report an unavailable required role or slot
instead of taking over delegated Heavy work. Use this profile only for explicit,
isolated comparisons, and verify effective model and service tiers from rollout
data before drawing conclusions.

## Terra-Luna-Sol-Astra experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: TERRA_LUNA_SOL_ASTRA`, supplied by the
`terra-luna-sol-astra.config.toml` CLI profile. The marker overrides the default
Fast Luna route while selected. Terra Medium Fast is lightweight glue, Context
Packet compactor, acceptance integrator, and final communicator; it is not the
routine investigator, technical planner, implementer, or acceptance runner.

Choose Light or Heavy before spawning or editing. Questions, explanations, and
status requests that need no repository mutation may remain in Terra. A tiny,
obviously local, reversible implementation may be delegated directly to one
fresh `luna_light_worker`, which owns the edit and one focused check. Terra must
not perform even Light production edits itself. When an implementation needs
material repository discovery, crosses a component or interface boundary,
changes multiple files non-mechanically, requires a material design decision,
or has meaningful verification needs, choose Heavy.

For every Heavy implementation or review, use this exact sequential flow:

1. Terra states the objective and observable acceptance criteria, then spawns
   one fresh `luna_evidence_collector`. Luna performs bounded read-only
   investigation and returns an Evidence Dossier containing exact repository,
   file, symbol, and interface references; applicable instructions; current
   behavior and minimal gap evidence; relevant tests and focused commands;
   scoped git status; and material uncertainties. Luna reports evidence, not a
   technical design or proposed solution, and makes no edits.
2. After Luna finishes, Terra compacts the dossier into the Context Packet
   contract below. Terra removes duplication and noise, preserves material
   uncertainty, and does not choose the implementation approach for Sol.
3. Terra spawns one fresh `standard_senior_executor` with the Context Packet.
   Standard Sol Medium owns technical planning, implementation, ordinary repair,
   and one lightweight focused implementation check. A Heavy review package is
   explicitly read-only. Sol may not spawn agents.
4. If Sol completes the package, do not call Astra. If Sol finishes with a
   concrete blocker, Terra may start one fresh `astra_executor` only for the
   narrow unresolved remainder. Sol's evidence must name the unresolved
   acceptance criterion, attempted work and observed result, smallest remaining
   ownership surface, and why Astra is needed. Give Astra a delta packet, not
   the full dossier, Context Packet, or completed work.
5. After all implementation work finishes, Terra spawns one fresh
   `luna_acceptance_verifier`. Luna runs proportionate deterministic acceptance
   checks and reports `PASS` or `FAIL` with exact evidence; it never repairs
   production code. Prefer a fresh verifier context. Reuse a dedicated Luna
   thread only when the runtime safely supports resetting it to the acceptance
   capsule without carrying investigation instructions or stale task state.
6. For an ordinary acceptance failure, Terra sends one compact repair follow-up
   to the Sol or Astra owner of the defect. After that owner finishes, Terra
   requests one focused Luna acceptance recheck. Architecture, contract, scope,
   security, migration, or ambiguous-causality failures return to Terra for a
   decision rather than entering a repair loop.

At most one child may actively work at a time. Every initial child starts with a
fresh, compact, self-contained capsule; no child receives the root transcript.
No child may spawn another agent. Terra waits for each phase to finish before
starting the next, never duplicates delegated work, and reports a missing role
or slot instead of becoming the production worker. Use this profile only for
explicit, isolated comparisons and verify effective model and service tiers
from rollout data before drawing conclusions.

## Luna-Terra-context-Sol-Astra experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: LUNA_TERRA_CONTEXT_SOL_ASTRA`, supplied by the
`luna-terra-context-sol-astra.config.toml` CLI profile. It is an isolated
comparison route; it does not change the default Fast-Luna route or the full
Terra-root `TERRA_LUNA_SOL_ASTRA` experiment.

Light work remains in the Luna xHigh Fast root. For every Heavy implementation
or review, Luna performs one bounded evidence pass, applies the
Expected-Compression Gate below, builds or commissions a provenance-preserving
Context Packet, and then spawns exactly one fresh `standard_senior_executor`.
Standard Sol Medium owns technical planning and implementation, or one
explicitly read-only substantive review. Luna must not implement production
changes or perform the substantive review.

Apply the Expected-Compression Gate before Sol. Terra is allowed only after
Luna has already gathered the decision-relevant context and concrete evidence
makes either of these benefits credible:

- substantial noise, duplication, contradictions, or large raw logs, diffs, or
  traces can reasonably be expected to shrink the implementation packet by at
  least approximately 40 percent; or
- compaction can select and organize a provenance-linked relevant subset that
  avoids otherwise necessary broad Sol discovery.

Multiple components, instruction scopes, or schema/API/codegen/documentation
coupling alone do not trigger Terra. If evidence is merely incomplete, Luna may
perform one focused read. If the remaining issue requires a technical judgment
or design decision, send the gathered context directly to Sol; Terra must not
design. When neither expected benefit is credible, Luna builds the Context
Packet directly.

Terra receives only the gathered Evidence Bundle. It must measure and report
input and output word counts, state its counting method, and report reduction as
`(input_words - output_words) / input_words`. It separately identifies retained
evidence and removed noise, keeps exact provenance attached to every material
fact, and preserves unresolved contradictions. If an approximately 40 percent
reduction or avoidance of broad Sol discovery is not credible, Terra explicitly
declines compaction. It does not discover broadly, design, edit, accept, or spawn
agents.

Sol treats the resulting packet as working context instead of repeating Luna's
broad discovery. It may open exact edit locations and directly connected
definitions. Before expanding beyond them, Sol must identify which packet field
is incomplete, contradictory, stale, or insufficient for a material technical
decision and explain why that gap requires the additional discovery.

Sol and Astra follow the existing evidence-gated escalation contract. If Sol
isolates a genuinely hard unresolved remainder, Luna builds a narrow delta
packet from Sol's evidence, closes Sol, and only then starts Astra. Astra
receives only the unresolved criterion, smallest ownership surface, Sol's
attempted work and observed failure, and relevant changed paths. For an ordinary
defect, Luna sends one evidence-rich repair delta to the still-open owning Sol
thread, then reruns the affected acceptance checks. An Astra-owned ordinary
defect returns once to the still-open Astra thread under the same rule.

At most one child may work at a time and no child may spawn. Every Heavy task
still mandates exactly one Standard Sol implementation or review owner. If a
required role or slot is unavailable, report the runtime limitation instead of
taking over the package in Luna.

Because the runtime counts a completed but open child against the one-thread
limit, close Terra after receiving its packet and before spawning Sol. Keep the
completed Sol thread open and idle while Luna runs acceptance; use that same
still-open thread for the one permitted repair follow-up. Close Sol only after
acceptance succeeds, or before starting Astra when escalation is required.

Luna acceptance must inspect the implementation or reviewed diff and affected
cross-contract boundaries, then run proportionate deterministic tests that
cover the observable criteria and material edge cases. It must distinguish
product failures from environment limits and preserve concrete failure output,
paths, and expected-versus-observed behavior in the single permitted repair
delta. This route never adds a tester or verifier child.

## Luna-Astra implementer experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: LUNA_ASTRA_IMPLEMENTER`, supplied by the
`luna-astra-implementer.config.toml` CLI profile. In that experiment, Luna xHigh
is a lightweight root coordinator and verifier, and one fresh-context Astra
Medium subagent owns technical planning and the bounded implementation.

- Use an untyped/default subagent with explicit model `gpt-6-astra`, reasoning
  `medium`, `fork_turns="none"`, and a compact self-contained capsule.
- Before spawning Astra, Luna performs one bounded discovery pass and builds the
  Context Packet defined below. Stop discovery as soon as every required packet
  field has adequate evidence; do not attempt exhaustive repository mapping.
- Do not send the root transcript or unrelated history to Astra.
- Luna must act as glue rather than the technical planner. Give Astra the user
  objective, relevant scope, material constraints, and acceptance criteria; do
  not prescribe a detailed implementation plan or write a long technical prompt.
- Astra must inspect the relevant code, choose the technical approach, plan the
  work when planning is needed, and implement the solution.
- Astra may inspect, implement, and run only the focused checks needed while
  implementing. It must stop after returning the completed implementation,
  changed files, focused check results, and residual risks.
- Luna independently inspects the resulting diff, runs the acceptance tests,
  decides whether the task is complete, and communicates with the user.
- If testing exposes an ordinary implementation defect, send one compact repair
  follow-up to the same Astra agent, then have Luna re-run the failed checks.
- Do not create explorer, tester, Terra, or Sol agents in this experiment unless
  the user explicitly changes the experiment. Do not create a second Astra
  agent for review or a second opinion.
- Keep at most one spawned thread live and prohibit all nested agents.
- Use this profile only for isolated comparison tasks started with the explicit
  CLI profile. It does not change the normal Desktop route.
- Treat a 40–70% quota reduction as the external hypothesis to measure, not as
  an expected or guaranteed result.

## Luna-Sol-Astra escalation experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: LUNA_SOL_ASTRA_ESCALATION`, supplied by the
`luna-sol-astra-escalation.config.toml` CLI profile. In that experiment, Luna
xHigh is lightweight glue and verifier, one fresh-context Sol Medium subagent is
the primary technical planner and implementer, and Astra Medium is available
only for a narrow unresolved package after evidence-based escalation.

- Before spawning Sol, Luna performs one bounded discovery pass and builds the
  Context Packet defined below. Stop discovery as soon as every required packet
  field has adequate evidence; do not attempt exhaustive repository mapping.
- Give Sol the compact self-contained Context Packet. Use explicit model
  `gpt-5.6-sol`, reasoning `medium`, and `fork_turns="none"`.
- Luna must not prescribe a detailed technical approach. Sol owns inspection,
  technical planning, implementation, and focused implementation checks.
- If Sol can complete the package, it must do so and Astra must not be called.
- Sol may request Astra escalation only after a focused attempt produces a
  concrete blocker or isolates an intrinsically difficult remainder. Its report
  must identify the unresolved acceptance criterion, evidence from the attempt,
  the smallest remaining ownership surface, and why Astra is needed.
- Sol must finish before escalation. Luna evaluates the evidence and, only when
  justified, starts one fresh-context Astra Medium agent for the unresolved
  package. Sol must never spawn Astra or any other agent itself.
- Give Astra only the original objective needed to understand the remainder,
  relevant constraints, the precise unresolved package, and compact evidence
  from Sol. Do not transfer either full thread or ask Astra to repeat completed
  Sol work.
- Luna independently inspects the combined diff and runs acceptance tests. Send
  at most one focused repair follow-up to the agent that owns the defect, then
  have Luna re-run the failed checks.
- Keep at most one spawned thread live, prohibit nested agents, and create no
  explorer, tester, Terra, or second-opinion agents unless the user explicitly
  changes the experiment.
- Use this profile only for isolated fresh-task comparisons. Record how often
  Astra escalation occurs; avoiding unnecessary Astra calls is a primary success
  criterion.

### Luna Fast / implementation Standard variant

The marker `EXPERIMENT: LUNA_FAST_SOL_ASTRA_STANDARD`, supplied by the top-level
default configuration and also available through the
`luna-fast-sol-astra-standard.config.toml` profile, uses the same Context Packet,
Sol-first ownership, evidence-gated Astra escalation, single-live-agent limit,
and Luna acceptance policy. Its only intended experimental difference is service
tier: the Luna root uses `fast`, while both `standard_senior_executor` Sol and the optional
`astra_executor` Astra use role configurations with `service_tier = "default"`.
This is the normal route unless another explicit CLI profile overrides its
developer instructions. Do not spawn either implementation model as an untyped/default agent in this
variant, because it could inherit the root's Fast tier. Verify effective service
tiers from rollout data before drawing conclusions from the experiment.

#### Default-route acceptance and repair

In this normal route, Sol treats the Context Packet as working context. It may
open exact edit locations and directly connected definitions. Before broader
discovery, it must name the specific packet field that is incomplete,
contradictory, stale, or insufficient for a material design decision and explain
why that deficiency requires expanding the search.

Keep the completed Sol thread open and idle while Luna owns acceptance. Luna
inspects the resulting diff and every affected cross-contract boundary, then
runs proportionate deterministic tests covering the observable criteria and
material edge cases. It distinguishes product
failures from harness or environment limitations.

For one ordinary implementation defect, Luna sends an evidence-rich repair
delta to the same still-open Sol thread. The delta includes the failed
criterion, exact expected-versus-observed behavior, concrete output and paths,
and the narrow recheck to run. Luna then reruns the affected acceptance checks.
Close Sol only after acceptance succeeds, or before starting Astra for a
genuinely hard unresolved package under the escalation gate. Do not add a
separate tester or verifier child to this default route.

### Context Packet contract

For all Luna-root experiments above, Luna gathers decision-relevant facts before
the implementation agent starts. In the Terra-Luna-Sol-Astra experiment, the
Luna collector gathers those facts in an Evidence Dossier and Terra performs the
compaction. In either case, the packet is a task-proportional compaction of the
relevant context, not a technical design. It has no fixed word limit: include
all material evidence needed for the implementation agent to work efficiently,
but exclude noise, duplication, and unrelated history. Include:

1. The user's objective and observable acceptance criteria.
2. Exact repository root, relevant files, symbols, interfaces, and component
   boundaries, with line references when useful.
3. Applicable repository instructions and material constraints.
4. Current behavior and the smallest reproducible evidence for the gap, such as
   a focused failing test or error. Summarize outputs instead of pasting logs.
5. Existing tests and the exact focused commands the implementer should run.
6. Git status limited to relevant paths so user-owned changes are preserved.
7. Known uncertainties stated as questions for the implementer to resolve.

Do not include the full conversation, broad file dumps, repeated instructions,
speculative implementation steps, or an architecture chosen by Luna. Luna may
use batched read-only searches and focused commands, but must not edit production
files during collection. Treat cited packet facts as the working context. The
implementer should not repeat Luna's broad discovery or re-read every cited file.
It may open the exact edit location and directly connected definitions before
changing them, or investigate further when the packet is incomplete,
contradictory, stale, or a material design decision cannot safely be made from
the supplied evidence.

Implementation-owned validation must be lightweight: run the narrowest cheap
smoke test, syntax/type check, or directly affected test that can catch an
obvious defect. Do not run the full suite, broad integration tests, or repeated
model review unless the task cannot be implemented responsibly without them.
In Luna-root experiments, Luna owns the proportionate acceptance suite after
implementation. In the Terra-Luna-Sol-Astra experiment, the dedicated Luna
acceptance verifier owns that suite and reports its evidence to Terra.

If Sol supplies justified Astra escalation evidence, the root sends Astra a
delta packet containing the unresolved acceptance criterion, relevant original
packet facts, Sol's concrete evidence, current changed paths, and the smallest
remaining ownership surface. Do not resend completed work or the original
packet wholesale.

## Sol research-slot policy

This policy applies whenever a selected `senior_executor` receives a Sol package,
in either the base route or the Astra-Sol research profile. A Research Slot is
**withheld by default**. A senior-executor capsule must explicitly say `Research
Slot: withheld` or `Research Slot: granted`; only the latter permits one Luna
Medium read-only investigator.

Before granting the slot, Astra must confirm that the global cap of two live
spawned threads includes the prospective nested investigator, terminate or
release its own researcher, and reserve the freed slot exclusively for Sol.
Astra must not use a reserved slot. The Luna investigator may not spawn agents,
and neither Sol nor the investigator may delegate any further work. Sol must
terminate or release the investigator before Sol reports its package complete.
If the slot is withheld, unavailable, or native delegation is unavailable, Sol
reads directly; it must not use `codex exec` or another nested-Codex workaround.
Sol owns ordinary repair in its package; the root owns contracts and starts
testing after Sol reports completion.

## Runtime Routing Contract

Task names, nicknames, and role labels do not activate an agent configuration or
tool profile. When the collaboration tool accepts model and reasoning overrides,
pass the configured values explicitly on every initial spawn:

| Role | Model | Reasoning | Service tier |
|------|-------|-----------|--------------|
| `standard_senior_executor` | `gpt-5.6-sol` | `medium` | `default` |
| `astra_executor` | `gpt-6-astra` | `medium` | `default` |
| `terra_context_compactor` | `gpt-5.6-terra` | `medium` | `fast` |
| `explorer` | `gpt-5.6-luna` | `medium` | inherited |
| `worker` | `gpt-5.6-terra` | `high` | inherited |
| `tester` | `gpt-5.6-luna` | `high` | inherited |
| `senior_executor` | `gpt-5.6-sol` | `medium` | inherited |
| `luna_evidence_collector` | `gpt-5.6-luna` | `medium` | `fast` |
| `luna_light_worker` | `gpt-5.6-luna` | `medium` | `fast` |
| `luna_acceptance_verifier` | `gpt-5.6-luna` | `medium` | `fast` |

Do not route an `explorer` or `tester` to the default Terra model merely because
its task name contains the role name. A task such as `tester`, `explorer_apps`,
or `explorer_repository` remains untyped unless the runtime applies the matching
role profile. If typed roles are unavailable, use the table above as the
effective routing contract and include the role's behavioral constraints in the
task capsule.

The standalone agent files document intended restrictions but do not by
themselves prove that a runtime tool or sandbox profile was applied. State a
sandbox guarantee only after verifying the effective restriction; otherwise use
explicit model, reasoning, and behavioral constraints in the capsule.

Do not start a tester while the implementation it must verify is still running.
Wait for the relevant worker to finish, then give the tester the completed state
and acceptance criteria. A tester must not poll, wait for, coordinate, or inspect
the status of sibling agents. Independent packages may still run concurrently,
subject to the two-agent limit.

## Heavy Route Entry

Before implementation:

1. State the intended outcome and acceptance criteria.
2. Identify the smallest decision-critical context the root must inspect.
3. Separate independent read-only investigation from production ownership.
4. Form bounded packages with non-overlapping write ownership.
5. Dispatch independent packages together when doing so reduces root turns.

The root may perform a small amount of direct inspection needed to make a
material architecture, scope, risk, or acceptance decision. Delegate broad or
routine discovery instead of repeatedly reading the repository in the root.

## Adaptive Delegation Budget

Treat the number of subagents as an adaptive budget, not a target and not an
absolute lifetime cap. A genuinely large task may use many agents across its
full lifetime when each one owns a distinct package or supplies justified
independent verification.

- Start a Heavy task with at most one wave of one or two bounded agents.
- Integrate the completed wave before opening another dependent wave.
- After four subagent sessions have completed for one root task, perform a
  delegation checkpoint before every additional wave. Identify the acceptance
  criteria still open, the distinct package each new agent will own, why an
  existing owner cannot complete it, and why delegation is cheaper or more
  reliable than another root rollout.
- The checkpoint authorizes more agents when the remaining work is genuinely
  distinct; it is not a hard limit on large tasks.
- Do not create an agent merely because concurrency capacity is available.
- Avoid duplicate exploration, overlapping implementation, and broad repeated
  review without a new defect, risk, or acceptance criterion.
- Prefer a focused follow-up to the current owner for clarification, ordinary
  repair, and revalidation. A follow-up to the same agent is preferable to a
  replacement because it preserves package context.
- Create a replacement agent only after the focused retry rules in
  Implementation and Repair Ownership are satisfied or when ownership must
  change for a material reason.

## Context Transfer

Initial subagents should normally start without inherited conversation history.
Use `fork_turns="none"` and provide a compact, self-contained task capsule. Do
not fork the full root transcript merely for convenience.

Every initial capsule begins with a stable Task ID and uses the role-specific
structure below.

### Explorer capsule

- `Task ID`
- `Investigation Context`
- `Evidence Question + Goal`
- `Scope and Source Boundaries`
- `Main-Agent Guidance`

Require concise findings with exact file references, relevant evidence,
uncertainty, and implications. The explorer must not modify files or decide the
final architecture or acceptance outcome.

### Worker capsule

- `Task ID`
- `Implementation Context + Ownership`
- `Implementation Task + Goal`
- `Acceptance Criteria`
- `Main-Agent Guidance`

Include only material interfaces, constraints, decisions, likely files, risks,
and required outcomes. Leave bounded discovery, implementation details, ordinary
repair, and appropriate validation to the worker. Require a concise report of
changes, checks, failures, residual risk, and decisions needed from the root.

### Tester capsule

- `Task ID`
- `Verification Context`
- `Verification Goal`
- `Acceptance Criteria and Risks`
- `Main-Agent Guidance`

The tester independently chooses proportionate checks, reports observable
evidence, and distinguishes product failures from environment limitations. The
tester must not repair production code.

### Senior Executor capsule

Use the Worker capsule structure, but explicitly add:

- `Escalation Evidence`, stating why Sol was selected, including why it should
  investigate first when Terra has not run;
- `Experiment Marker`, repeating `EXPERIMENT: ASTRA_SOL_RESEARCH` when active
  or stating `none` otherwise; and
- `Research Slot`, explicitly `granted` or `withheld` (withheld by default).

The senior executor receives one bounded hard package, not the complete project
or an open-ended request.

For a follow-up, repeat the Task ID and send only changed facts, decisions,
scope, evidence, or acceptance criteria. Do not resend an unchanged capsule or
the full root history.

## Batching and Root Rollout Control

- Batch independent reads, searches, metadata checks, and other operations with
  known inputs.
- Dispatch independent agents needed for the same decision in one batch.
- Keep dependent work and overlapping mutations sequential.
- Wait for the relevant batch, then synthesize its results once.
- Open another batch only when new evidence materially changes the next task or
  decision.
- Do not ask agents for information already present in their reports.
- Keep worker reports compact; retain raw logs and large output outside the
  parent-facing response unless the evidence is decision-critical.
- Do not invoke the root model solely because time passed.

## Waiting Policy

When agents are healthy and running, remain idle unless useful independent work
is available.

- Use event-driven waits with the longest practical timeout.
- Do not poll agent status repeatedly.
- Do not request status-only messages.
- Do not inspect activity files merely to see whether an agent is still alive.
- Do not interrupt or replace a healthy agent after an ordinary wait timeout.
- Wake the root for a completed result, failure, material question, user input,
  or genuinely useful independent work.
- Use an agent listing only to resolve real terminal-state uncertainty.

## Implementation and Repair Ownership

In Heavy, do not let the expensive root silently become the routine implementer.

- The assigned worker owns its package through ordinary implementation,
  self-check, focused repair, and revalidation.
- If verification finds an ordinary defect, return focused evidence to the same
  worker, then send the repair delta back to the same tester when independent
  rechecking is warranted.
- After one evidence-free or materially incomplete worker response, send one
  focused retry with the missing evidence or criterion.
- After a second focused failure, replace the worker, narrow the package, or
  escalate the decision. Do not enter an unbounded repair loop.
- Escalate to the root only for architecture or contract changes, conflicting
  packages, expanded ownership, security or migration risk, ambiguous causal
  evidence, or an external blocker.
- The root may make the necessary decision and issue a revised capsule; it
  should not take over routine production merely because a worker needed repair.

## Senior Executor Escalation Gate

`senior_executor` is a selective base-route choice, never the default path for
clear bounded implementation. Use at most one senior executor at a time and
only when at least one condition is true:

- one focused Terra worker attempt produced concrete evidence that the bounded
  package exceeds Terra's reasoning capability;
- the package is a high-uncertainty or cross-component difficult diagnosis and
  the capsule explains why Sol should investigate first; a failed Terra attempt
  is not required;
- the package is intrinsically difficult mathematical, algorithmic, logical,
  architectural, or cross-cutting work and the root can explain why Terra is
  unlikely to be reliable;
- a material architecture or contract decision has been narrowed to one hard
  implementation package that genuinely needs stronger reasoning.

Do not escalate merely because a task is large, a worker is still running, the
first result needs an ordinary repair, or Sol might be faster. Record the
qualifying evidence in the Senior Executor capsule. Give it non-overlapping
ownership, one focused attempt, and proportionate validation. It must not spawn
subagents except for the explicitly granted Research Slot under the shared Sol
research-slot policy. If it cannot complete the package, return the decision to
the root; do not create a chain of senior agents. The active research profile's
Sol-primary rule supersedes this base-route gate.

## Verification

Match verification effort to risk.

- Small reversible changes may rely on focused worker validation.
- Use `tester` for substantive behavior changes, regressions, important boundary
  cases, cross-component changes, or when independence materially improves trust.
- Do not create a separate tester for routine, low-risk, or easily reversible
  changes when deterministic worker-owned checks already cover the acceptance
  criteria.
- A justified verification cycle may include explorer, worker, tester, repair by
  the same worker, and a focused recheck by the same tester. Preserve that cycle
  when the risk warrants it; remove only duplicate or evidence-free passes.
- Prefer deterministic tests, compilers, linters, schemas, and other executable
  gates over repeated model review.
- Do not add a separate model-review cycle when existing automated evidence is
  sufficient.
- Never weaken assertions, coverage, or failure visibility to save tokens.
- Never claim an unrun check passed.

## Completion

Before declaring a Heavy task complete, the root must:

1. Confirm that package reports cover the requested scope.
2. Resolve material conflicts and integrate results.
3. Confirm that proportionate verification completed successfully or clearly
   disclose what could not be run and why.
4. Check that no unrelated user work was overwritten.
5. Report the outcome, material changes, verification, and remaining risk
   concisely.

Do not perform an additional broad review or repeat completed checks without new
evidence, a failure, a material risk, or an explicit user request.
