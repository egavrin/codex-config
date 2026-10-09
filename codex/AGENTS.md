# Cost-Efficient Codex Orchestration

## Controlled English

Use English for user responses, agent messages, and new technical documents.
An explicit request for another output language takes precedence.
Read `~/.codex/skills/writing-for-agents/references/controlled-english.md` for the shared writing profile.
The profile derives from ASD-STE100 Issue 9 and defines software and agent extensions.
Preserve exact identifiers, commands, quotations, and required product text.
Preserve scope, permissions, exceptions, and verification requirements when you change prose.

This language rule does not authorize a document edit or change an orchestration route.

## Objective

Use the root model for understanding the request, bounded evidence collection,
architecture, decomposition, hard decisions, integration, acceptance, and
communication. In the default route, delegate only when the effective-root branch calls for a distinct owner. Assign one bounded implementation or substantive read-only review package. Exact experimental marker sections may define other role
sequences.

Optimize for completing the user's task with fewer root-model rollouts and less
repeated root context. Do not optimize token usage by weakening correctness,
skipping necessary verification, or producing incomplete work.

## API Keys and Local Environment

When an API key or credential is necessary for a task, preserve any non-empty value
already set in the environment. If the required variable is absent or empty,
load it from `~/.env` (`/Users/egavrin/.env`) before calling the service.
Load only the variables needed for the task into the calling process's
environment. Treat the file as dotenv data, not executable shell code.

Never expose secret values or the contents of `~/.env` in chat, logs, reports,
or commands containing literal credentials. Do not copy secrets into task
packets or generated files. If the key is absent from both the process environment and `~/.env`, report only its name and the sources examined.

## Engineering Choices

Choose the simplest maintainable solution that meets the requirements. Reuse
existing project facilities first, then consider suitable maintained libraries
before building custom infrastructure. Weigh dependency, security, and licensing
costs. Do not add a dependency merely to avoid a small, clear implementation.
For unfamiliar or version-sensitive external APIs, examine documentation for the
version the project actually uses. Do not upgrade a dependency just to match a
newer example.

## Routes

Choose exactly one orchestration route before substantive work. Direct and
Delegated are task-routing classes. They are not Desktop reasoning labels.

### Direct route

Use Direct when the effective root can safely finish the bounded work with a few
focused operations and deterministic acceptance. Typical Direct work includes
questions, bounded diagnosis, tiny local edits, and narrow reviews. Do not add
coordination overhead when a distinct implementation owner offers no material
benefit.

### Delegated route

Use Delegated for substantive implementation or review when a distinct owner materially improves reliability or reduces root context and work. For ordinary substantial independent work, use Claude Opus High first
under the companion policy below. The native model-aware branches apply only
when that companion route is unavailable or cannot complete the bounded package.
Signals include repository discovery plus implementation, cross-component behavior, and non-mechanical multi-file changes. Other signals include material design decisions, important security or regression risks, and substantive read-only reviews. Route by the actual effective root model, not merely the configured
default.

### Default model-aware routing

The marker `EXPERIMENT: SOL_HIGH_ASTRA_MEDIUM_XHIGH` selects the normal policy.
The local default is Sol High on the Standard tier, but Desktop or runtime root
overrides remain authoritative user choices.

For ordinary substantial independent review or patch packages, first use
`claude-collab` with explicit Opus High effort. The table and native lifecycle
rules below are the fallback, not a requirement to bypass Claude. Fall back if Claude is unavailable, authentication/usage limits block work, supervision detects a stall, or the package remains incomplete. Record
the specific reason and carry forward completed evidence.

Stop the companion
before starting one native owner. Never run both concurrently. The root retains
scope, integration, patch application, and acceptance.

Tiny Direct work stays in
the root. Named opt-in experiments retain their exact routes. High effort is not
evidence that latency will improve.

Native fallback branches:

| Effective root | Direct and ordinary root-owned work | Delegated behavior |
|---|---|---|
| Terra | Complete Direct work in Terra. | Give exactly one Context Packet to `senior_executor_standard`. Use `astra_executor_high` only for a narrow evidence-gated remainder after Sol. |
| Luna | Complete Direct work in Luna. | Give exactly one Context Packet to `senior_executor_standard`. Use `astra_executor_high` only for a narrow evidence-gated remainder after Sol. |
| Sol | Complete Direct work in Sol. Never spawn another Sol. | Give exactly one Context Packet to `astra_executor_high`. Use `astra_executor_xhigh` only for an evidence-gated intrinsically hard remainder after High Astra. |
| Astra | Normally own planning, implementation, and acceptance directly. Never spawn Astra from Astra. | Optionally give one clearly bounded package to `senior_executor_standard` only when doing so materially reduces Astra context or work. |

For Terra- and Luna-root native fallback, the root performs one bounded evidence pass and forms the Context Packet. It assigns exactly one fresh `senior_executor_standard`. A substantive review package is explicitly read-only.
Sol uses the packet as working context.

It may open exact edit locations and directly connected definitions. Before broader discovery, it must identify the deficient packet field, evidence for the deficiency, and the reason for expansion. The root must not duplicate the delegated package.

For default Sol-root native fallback, Sol performs one bounded evidence pass and forms the Context Packet. It assigns exactly one fresh `astra_executor_high`. Astra High owns technical planning within the
package, implementation or an explicitly read-only review, and one lightweight
focused check. Sol must not prescribe a detailed implementation plan or duplicate
the package.

A routine acceptance defect returns once to that same still-open
High Astra owner. Extra High is not a repair tier. Use `astra_executor_xhigh` only after High Astra supplies the required evidence.

That evidence must identify an attempted failure, unresolved criterion, smallest remaining ownership surface, and need for deeper reasoning. Close High Astra before starting Extra High and give Extra High a delta
packet rather than the full original packet.

The effective root always owns final acceptance. Inspect the diff and affected cross-contract boundaries. Run proportionate deterministic tests and material edge cases. Distinguish product defects from harness or environment limitations.

Preserve exact expected-versus-observed evidence in a repair delta. Keep the
implementation owner open and idle through acceptance. Send at most one ordinary
repair to that same owner.

Close the current owner before a model-tier
escalation. This keep-open behavior is an instruction validated by local rollout
evidence, not a runtime lifecycle guarantee.

Never run more than one child concurrently. Prohibit nested agents. Do not add a separate verifier or second-opinion child. Never spawn Sol from Sol or let a child spawn another agent.

High Astra is the Sol-root native fallback owner. Extra
High Astra remains rare and evidence-gated. When route choice is uncertain, examine whether the effective root can safely complete the task and deterministic acceptance alone.

Use Direct only in that case. Otherwise, use the model-aware Delegated branch.

### Capability-aware default fallback

A native internal subagent is created through the current session's
collaboration or subagent spawn mechanism. `create_thread`, `fork_thread`,
`send_message_to_thread`, and nested `codex exec` are not automatic substitutes.
Use a user-visible task creation mechanism only after the user explicitly asks
for a separate task.

If native collaboration is entirely absent, the effective root completes the work and acceptance directly when possible. It reports `effective_route = <root>-single-agent-fallback` and the concrete reason for failed delegation.
If collaboration exists but the exact named role is unexpectedly absent, also report configuration drift. Do not claim a valid delegated benchmark run. A route-owned child temporarily occupying the only slot does not justify fallback. Wait, reuse it for its owned repair, or close it as required.

Report the actual effective root model, reasoning, and service tier separately.
For normal work, report the exact `effective_route`: `terra-direct`, `terra-sol`,
`luna-direct`, `luna-sol`, `sol-direct`, `sol-astra`, `sol-astra-xhigh`,
`astra-direct`, or `astra-sol`. Use the corresponding
`*-single-agent-fallback` label only when intended delegation failed, and exclude
such sessions from valid delegated-route benchmarks.

## Jev routing-adviser shadow experiment

The exact marker `EXPERIMENT: JEV_ROUTING_ADVISER` selects an opt-in shadow
experiment, not a new default route. It applies to a Terra root. Jev is a
decision adviser, never a planner or implementer. Gather one bounded Context
Packet and manually reduce it to a JSON packet containing only `objective`,
`acceptance_criteria`, `constraints`, and `complexity_signals`. Exclude source
code, raw logs, private identifiers, secrets, and the root transcript. The
allowlist and pattern checks in `~/.codex/jev_router.py` are a safety backstop,
not a guarantee that every secret is detected.

Run `preview` and show the complete `state_to_send` and SHA-256 to the user.
The root may run `query` only after the user explicitly approves that exact preview. Use the preview digest and existing `TYPESAFE_API_KEY`. Follow API Keys and Local Environment above (preserve a non-empty environment value, otherwise load it from `~/.env`). Fresh key rotation is not required before
each request. Never paste a key into a command, prompt, file, or report.

If
approval, key, or API access is missing, skip the call and continue the normal
Terra route. For a changed packet, obtain approval for a new preview.

One Jev API request contains three independent choices: `planning` (`none` or
a model/reasoning pair), `implementation_without_plan`, and
`implementation_with_plan`. The client combines them into two recommendations:
whether to use a separate planner (and its pair), then the implementation pair
from the branch matching that planning choice. The unused implementation branch
is retained for audit, not acted on. Some proposed pairs have no installed named role and remain advisory candidates.

Do not infer runtime dispatch support from a Jev response. The pilot confidence floor is 0.7 for planning and the selected implementation branch. Uncertainty in the unused branch does not invalidate the composed recommendation. Do not invent a joint probability.

In all cases,
the actual dispatch remains the default model-aware route: Terra Direct or
Terra-to-Sol with only evidence-gated Astra escalation. Do not spawn an Astra planner merely because Jev recommends one. Never bypass the Sol gate, add a tester, or exceed one active child. Record both Jev stage suggestions and the actual route. Also record disagreements, response latency, token usage, acceptance, and model traffic for later comparison. The root still owns acceptance.

## Root Selection, Reasoning, and Tier

The local default is GPT-6.1 Sol with High reasoning on Standard service tier.
Desktop model, reasoning, and tier overrides are user choices. Respect the effective values. Never describe an effective Terra, Luna, or Astra root as Sol.

Light, Medium, High, and Extra High name reasoning levels in the Desktop selector. They do not select Direct or Delegated routing.
Do not request a reasoning change merely to enter an orchestration route.

## Terra-Astra plan/build experiment

The exact marker `EXPERIMENT: TERRA_ASTRA_PLAN_BUILD`, supplied only by
`terra-astra-plan-build.config.toml`, overrides the normal Terra-to-Sol route
for this opt-in experiment. Terra Medium Priority is the root: it gathers one
bounded, provenance-preserving Context Packet, orchestrates, integrates, and
owns deterministic acceptance. It does not design or implement substantive
production work. Bounded Direct questions and trivial changes may remain in
Terra. Do not manufacture agent work for them.

For substantive work, Terra first starts one fresh `astra_planner_standard`
with `fork_turns="none"`. Astra plans the technical approach and returns
non-overlapping packages but never edits. Then, Terra starts one fresh `astra_builder_standard` per package with `fork_turns="none"`. Supply only the relevant plan slice, evidence, constraints, and acceptance criteria.

At
most one builder writes at a time. At most three fresh builders may be opened
in this pilot. After two builder packages, reassess the open criteria and
coordination cost before a third. A routine defect goes once to its existing
owner.

No child may spawn. Do not create a watchdog, verifier, visible task,
fork, or nested Codex process as a substitute.

The current CLI does not expose a reliable child-slot release operation. Thus, the profile reserves four open slots for the planner and up to three builders. Capacity is not a target. If a required role or slot is absent, report an invalid experimental run.

Do not silently select the default route. Terra inspects the combined diff and cross-contract boundaries, then runs proportionate deterministic acceptance. It records actual model/effort, observable tier, parentage, traffic, repairs, and latency. Do not promote this
route to default from one benchmark or infer dollar savings from subscription
quota percentages.

## Astra-Luna nested Astra experiment

The exact marker `EXPERIMENT: ASTRA_LUNA_NESTED_ASTRA`, supplied only by
`astra-luna-nested-astra.config.toml`, overrides the normal model-aware route's
one-child, no-nesting, and no-Astra-from-Astra rules for this opt-in experiment.
It does not change the local or Desktop default. Use native internal subagents
only. Never replace nesting with visible tasks, forks, or nested `codex exec`.

The Astra Medium Standard root plans and owns final acceptance. First it asks
Luna for a read-only capability preflight. Only if nested spawning and child-slot release are available, create a task-specific handoff file in a private temporary directory. Use current-user-only permissions. Include the objective, observable acceptance criteria, exact source references, material constraints, and uncertainties. Exclude secrets, the full conversation, bulk logs, and
unrelated history.

Remove only this generated handoff after acceptance.

The root first starts one fresh `luna_orchestrator_nested` and examines native
nested-spawn and child-slot-release availability with a read-only preflight.
Only after that succeeds
does it start one `astra_watchdog_nested`. The watchdog stays open for the task
but idle: no
timer-based polling, status requests, or duplicate research. Activate it only
with a concrete blocker and evidence.

Luna reads the handoff and coordinates non-overlapping packages. It starts at most one fresh `astra_builder_nested` at a time with `fork_turns="none"` and a self-contained capsule. A builder owns
technical implementation and one focused check, may receive one ordinary repair
while open, and may not spawn.

Luna does not edit production code. The watchdog
diagnoses read-only. It never becomes a concurrent production writer.

At most three spawned threads may be open at once: Luna, the watchdog, and one
builder. Only one agent owns production edits at a time. Luna may spawn only the
builder role. No agent may create a deeper descendant.

Close a builder before
opening another, and close all children after root acceptance. After two builder
packages, the root must reassess remaining criteria and overhead before asking
Luna for another. The root accepts by inspecting the diff and affected contracts
and running proportionate deterministic tests, not by trusting model reports.

First validate a read-only root → Luna → Astra smoke chain. The CLI smoke on 2026-09-17 failed because Luna had no native collaboration interface. The root also lacked a native close operation for child slots. This
profile is not yet validated for substantive work on that runtime. Examine again only
after a relevant runtime update or capability change. `max_depth = 2` is
only a V1 guard, not proof that V2 enforces nesting or that three slots are
available.

If native nesting, a named role, or a required slot is unavailable, stop the experiment. Report the exact limitation. Never report a valid `astra-luna-nested-astra` route or benchmark from a fallback. Record actual
models, reasoning, tiers when telemetry exposes them, parentage, traffic,
latency, acceptance, and repair. Do not infer dollar savings from subscription
quota percentages. Keep the profile opt-in pending paired real-task evidence.

## Astra-Sol research profile

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: ASTRA_SOL_RESEARCH`, supplied by the
`astra-sol-research.config.toml` CLI profile. In that experiment, Astra Extra
High is the root and Sol Medium is the default primary subagent for substantial
coding and difficult diagnosis. Terra is used only when the task capsule
explicitly assigns Terra. While the profile is active, this marker takes precedence over the default model-aware route. It does not replace unrelated routing, verification, safety, or completion instructions.

`agents.max_depth` is a V1 guard only. Multi-agent V2 currently does not enforce
it, so these explicit capsule and slot rules are the operative nesting limit.

## Astra-Terra Standard comparison profile

The marker `PROFILE: ASTRA_TERRA_STANDARD` comes from `astra-terra-standard.config.toml` and selects a historical comparison. It uses an Astra Medium root on Standard tier and Terra High for clear bounded implementation. Luna High testing is permitted only with independent justification. Selective Sol use is permitted under the Senior Executor Escalation Gate. This explicit profile overrides the default Sol High
route while active.

## Terra-Luna-Sol-Astra experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: TERRA_LUNA_SOL_ASTRA`, supplied by the
`terra-luna-sol-astra.config.toml` CLI profile. The marker overrides the default
Sol High route while selected. Terra Medium Fast coordinates work, compacts Context Packets, integrates acceptance, and communicates final results. It does not routinely investigate, plan technical work, implement, or run acceptance.

Choose Direct or Delegated before spawning or editing. Questions, explanations, and
status requests without repository mutation may remain in Terra. A tiny, obviously local, reversible implementation may go directly to one fresh `luna_light_worker_fast`. That worker owns the edit and one focused check.

Terra
must not perform even Direct production edits itself. Choose Delegated if implementation entails material repository discovery, crosses a component or interface boundary, or changes multiple files non-mechanically. Also choose Delegated for a material design decision or meaningful verification requirements.

For every Delegated implementation or review, use this exact sequential flow:

1. Terra states the objective and observable acceptance criteria, then spawns
   one fresh `luna_evidence_collector_fast`. Luna performs bounded read-only investigation and returns an Evidence Dossier. Include exact repository, file, symbol, and interface references, plus applicable instructions. Include current behavior, minimal gap evidence, relevant tests, focused commands, scoped git status, and material uncertainties. Luna reports evidence, not a
   technical design or proposed solution, and makes no edits.
2. After Luna finishes, Terra compacts the dossier into the Context Packet
   contract below. Terra removes duplication and noise, preserves material
   uncertainty, and does not choose the implementation approach for Sol.
3. Terra spawns one fresh `senior_executor_standard` with the Context Packet.
   Standard Sol Medium owns technical planning, implementation, ordinary repair,
   and one lightweight focused implementation check. A Delegated review package is
   explicitly read-only. Sol may not spawn agents.
4. If Sol completes the package, do not call Astra. If Sol finishes with a
   concrete blocker, Terra may start one fresh `astra_executor_standard` only
   for the narrow unresolved remainder. Sol's evidence must name the unresolved acceptance criterion, attempted work, observed result, and smallest remaining ownership surface. It must explain why Astra is necessary. Give Astra a delta packet, not
   the full dossier, Context Packet, or completed work.
5. After all implementation work finishes, Terra spawns one fresh
   `luna_acceptance_verifier_fast`. Luna runs proportionate deterministic
   acceptance checks and reports `PASS` or `FAIL` with exact evidence. It never
   repairs production code.

   Prefer a fresh verifier context. Reuse a dedicated Luna thread only when the runtime safely resets it to the acceptance capsule. No investigation instructions or stale task state may remain.
6. For an ordinary acceptance failure, Terra sends one compact repair follow-up
   to the Sol or Astra owner of the defect. After that owner finishes, Terra
   requests one focused Luna acceptance recheck. Architecture, contract, scope,
   security, migration, or ambiguous-causality failures return to Terra for a
   decision rather than entering a repair loop.

At most one child may actively work at a time. Every initial child starts with a
fresh, compact, self-contained capsule. No child receives the root transcript.
No child may spawn another agent.

Terra waits for each phase to finish before the next phase. It never duplicates delegated work. If a role or slot is absent, it reports the limitation and does not become the production worker.

Use this profile only for explicit, isolated comparisons. Before conclusions, make sure that the effective model and service tiers match the rollout data.

## Luna-Terra-context-Sol-Astra experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: LUNA_TERRA_CONTEXT_SOL_ASTRA`, supplied by the
`luna-terra-context-sol-astra.config.toml` CLI profile. This is an isolated comparison route. It does not change the default Sol High route or full Terra-root `TERRA_LUNA_SOL_ASTRA` experiment.

Direct work remains in the Luna xHigh Fast root. For every Delegated implementation or review, Luna performs one bounded evidence pass. It applies the Expected-Compression Gate below. It builds or commissions a Context Packet that preserves provenance. Then, it spawns exactly one fresh `senior_executor_standard`.
Standard Sol Medium owns technical planning and implementation, or one
explicitly read-only substantive review.

Luna must not implement production
changes or perform the substantive review.

Apply the Expected-Compression Gate before Sol. Terra is permitted only after Luna collects the decision-relevant context. Concrete evidence must also make either benefit credible:

- The evidence includes substantial noise, duplication, contradictions, or large raw logs, diffs, or traces. Their reduction must credibly reduce the implementation packet by at least approximately 40 percent, or
- compaction can select and organize a provenance-linked relevant subset that
  avoids otherwise necessary broad Sol discovery.

Multiple components, instruction scopes, or schema/API/codegen/documentation
coupling alone do not trigger Terra. If evidence is merely incomplete, Luna may
perform one focused read. If the remaining issue depends on a technical judgment or design decision, send the gathered context directly to Sol. Terra must not design. When neither expected benefit is credible, Luna builds the Context
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
definitions. Before broader discovery, Sol must identify the incomplete, contradictory, stale, or insufficient packet field. It must explain why that gap blocks a material technical decision and makes additional discovery necessary.

Sol and Astra follow the existing evidence-gated escalation contract. If Sol isolates a genuinely hard unresolved remainder, Luna builds a narrow delta packet from Sol's evidence. Luna closes Sol before it starts Astra. Astra
receives only the unresolved criterion, smallest ownership surface, Sol's
attempted work and observed failure, and relevant changed paths.

For an ordinary defect, Luna sends one evidence-rich repair delta to the still-open owning Sol thread. Then, it repeats the affected acceptance checks. An Astra-owned ordinary
defect returns once to the still-open Astra thread under the same rule.

At most one child may work at a time and no child may spawn. Every Delegated task
still mandates exactly one Standard Sol implementation or review owner. If a
required role or slot is unavailable, report the runtime limitation instead of
taking over the package in Luna.

After Terra supplies its packet, close Terra before you spawn Sol. The runtime counts a completed but open child against the one-thread limit. Keep the completed Sol thread open and idle during Luna acceptance. Use that same still-open thread for the one permitted repair follow-up. Close Sol only after
acceptance succeeds, or before starting Astra when escalation is required.

For acceptance, Luna must inspect the implementation or reviewed diff and affected cross-contract boundaries. It must run proportionate deterministic tests for the observable criteria and material edge cases. It must distinguish product failures from environment limits. Preserve concrete failure output, paths, and expected-versus-observed behavior in the single permitted repair delta. This route never adds a tester or verifier child.

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
  field has adequate evidence. Do not attempt exhaustive repository mapping.
- Do not send the root transcript or unrelated history to Astra.
- Luna must act as glue rather than the technical planner. Give Astra the user objective, relevant scope, material constraints, and acceptance criteria. Do not prescribe a detailed implementation plan or write a long technical prompt.
- Astra must inspect relevant code and select the technical approach. It must plan the work when necessary and implement the solution.
- Astra may inspect, implement, and run only the focused checks needed while
  implementing. It must stop after returning the completed implementation,
  changed files, focused check results, and residual risks.
- Luna independently inspects the resulting diff and runs acceptance tests. It decides whether the task is complete and communicates with the user.
- If testing exposes an ordinary implementation defect, send one compact repair follow-up to the same Astra agent. Then, have Luna run the failed checks again.
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
`luna-sol-astra-escalation.config.toml` CLI profile. In that experiment, Luna xHigh coordinates and tests work. One fresh-context Sol Medium subagent owns primary technical planning and implementation. Astra Medium is available only for a narrow unresolved package after escalation with supporting evidence.

- Before spawning Sol, Luna performs one bounded discovery pass and builds the
  Context Packet defined below. Stop discovery as soon as every required packet
  field has adequate evidence. Do not attempt exhaustive repository mapping.
- Give Sol the compact self-contained Context Packet. Use explicit model
  `gpt-5.6-sol`, reasoning `medium`, and `fork_turns="none"`.
- Luna must not prescribe a detailed technical approach. Sol owns inspection,
  technical planning, implementation, and focused implementation checks.
- If Sol can complete the package, it must do so and Astra must not be called.
- Sol may request Astra escalation only after a focused attempt produces a concrete blocker or isolates an intrinsically difficult remainder. Its report must identify the unresolved acceptance criterion, evidence from the attempt, and smallest remaining ownership surface. It must explain why Astra is necessary.
- Sol must finish before escalation. Luna evaluates the evidence and, only when
  justified, starts one fresh-context Astra Medium agent for the unresolved
  package. Sol must never spawn Astra or any other agent itself.
- Give Astra only the original objective necessary to understand the remainder, relevant constraints, precise unresolved package, and compact Sol evidence. Do not transfer either full thread or ask Astra to repeat completed
  Sol work.
- Luna independently inspects the combined diff and runs acceptance tests. Send at most one focused repair follow-up to the agent that owns the defect. Then, have Luna repeat the failed checks.
- Keep at most one spawned thread live. Prohibit nested agents. Create no explorer, tester, Terra, or second-opinion agents unless the user explicitly changes the experiment.
- Use this profile only for isolated fresh-task comparisons. Record how often
  Astra escalation occurs. Avoiding unnecessary Astra calls is a primary success
  criterion.

### Context Packet contract

For ordinary Claude packages, use the companion skill’s bounded packet schema
and explicit source/skill bundle. The following native Context Packet contract
applies after native fallback or when an opt-in experiment selects native work.

Before implementation, the root collects decision-relevant facts for these routes:
- Default Sol-root Delegated work.
- Runtime-overridden Terra- or Luna-root Delegated work.
- The Luna-root experiments above. In the
Terra-Luna-Sol-Astra experiment, the Luna collector gathers those facts in an
Evidence Dossier and Terra performs the compaction. In every case, the packet is
a task-proportional compaction of the relevant context, not a technical design.
The packet has no fixed word limit. Include all material evidence necessary for the implementation agent to work efficiently. Exclude noise, duplication, and unrelated history. Include:

1. The user's objective and observable acceptance criteria.
2. Exact repository root, relevant files, symbols, interfaces, and component
   boundaries, with line references when useful.
3. Applicable repository instructions and material constraints.
4. Current behavior and the smallest reproducible evidence for the gap, such as
   a focused failing test or error. Summarize outputs instead of pasting logs.
5. Existing tests and the exact focused commands the implementer should run.
6. Git status limited to relevant paths so user-owned changes are preserved.
7. Known uncertainties stated as questions for the implementer to resolve.

Exclude the full conversation, broad file dumps, repeated instructions, speculative implementation steps, and architecture chosen by the collecting root. The root may use batched read-only searches and focused commands, but must
not edit Delegated production files during collection. Treat cited packet facts
as the working context. The implementer should not repeat the root's broad
discovery or read again every cited file.
It may open exact edit locations and directly connected definitions before a change. It may investigate further if the packet is incomplete, contradictory, stale, or insufficient for a safe material design decision.

Implementation-owned validation must be lightweight. Run the narrowest cheap smoke test, syntax/type check, or directly affected test that can detect an obvious defect. Run the full suite, broad integration tests, or repeated model review only when necessary for responsible implementation.
After implementation, the coordinating root owns the proportionate acceptance
suite unless an exact experimental policy assigns a dedicated verifier. In the
default route, the effective root owns acceptance. In the
Terra-Luna-Sol-Astra experiment, the dedicated Luna acceptance verifier owns
that suite and reports its evidence to Terra.

If Sol supplies justified Astra escalation evidence, the root sends Astra a delta packet. Include the unresolved acceptance criterion, relevant original packet facts, and Sol's concrete evidence. Include current changed paths and the smallest remaining ownership surface. Do not resend completed work or the original
packet wholesale.

## Sol research-slot policy

This policy applies whenever a selected `senior_executor` receives a Sol package,
in either the base route or the Astra-Sol research profile. A Research Slot is
**withheld by default**. A senior-executor capsule must explicitly say `Research
Slot: withheld` or `Research Slot: granted`. Only the latter gives permission for one Luna
Medium read-only investigator.

Before the slot grant, Astra must make sure that capacity is available within the cap of two live spawned threads. This count must include the prospective nested investigator. Astra must terminate or release its own researcher and reserve the freed slot exclusively for Sol.
Astra must not use a reserved slot. The Luna investigator may not spawn agents,
and neither Sol nor the investigator may delegate any further work. Sol must
terminate or release the investigator before Sol reports its package complete.

If the slot or native delegation is unavailable or the slot is withheld, Sol reads directly. It must not use `codex exec` or another nested-Codex workaround.
Sol owns ordinary repair in its package. The root owns contracts and starts
testing after Sol reports completion.

## Runtime Routing Contract

Task names, nicknames, and role labels do not activate an agent configuration or
tool profile. A custom role file's `name` is authoritative, so every
`[agents.<id>]` registration and operative prompt reference must use that exact
value. When the collaboration tool accepts model and reasoning overrides, pass
the configured values explicitly on every initial spawn:

| Role | Model | Reasoning | Service tier |
|------|-------|-----------|--------------|
| `senior_executor_standard` | `gpt-6-sol` | `medium` | `default` |
| `astra_executor_standard` | `gpt-6-astra` | `medium` | `default` |
| `astra_executor_high` | `gpt-6-astra` | `high` | `default` |
| `astra_executor_xhigh` | `gpt-6-astra` | `xhigh` | `default` |
| `astra_planner_standard` | `gpt-6-astra` | `medium` | `default` |
| `astra_builder_standard` | `gpt-6-astra` | `medium` | `default` |
| `luna_orchestrator_nested` | `gpt-5.6-luna` | `medium` | `default` |
| `astra_builder_nested` | `gpt-6-astra` | `medium` | `default` |
| `astra_watchdog_nested` | `gpt-6-astra` | `medium` | `default` |
| `terra_context_compactor_fast` | `gpt-5.6-terra` | `medium` | `fast` |
| `explorer` | `gpt-5.6-luna` | `medium` | inherited |
| `worker` | `gpt-5.6-terra` | `high` | inherited |
| `tester` | `gpt-5.6-luna` | `high` | inherited |
| `senior_executor` | `gpt-5.6-sol` | `medium` | inherited |
| `luna_evidence_collector_fast` | `gpt-5.6-luna` | `medium` | `fast` |
| `luna_light_worker_fast` | `gpt-5.6-luna` | `medium` | `fast` |
| `luna_acceptance_verifier_fast` | `gpt-5.6-luna` | `medium` | `fast` |

Do not select the default Luna model for an `explorer` or `tester` merely because its task name includes that role. A task such as `tester`, `explorer_apps`,
or `explorer_repository` remains untyped unless the runtime applies the matching
role profile. If typed roles are unavailable, use the table above as the effective routing contract. Include the role's behavioral constraints in the task capsule.

The standalone agent files document intended restrictions but do not by
themselves prove that a runtime tool or sandbox profile was applied. State a sandbox guarantee only after a check of the effective restriction. Otherwise, supply explicit model, reasoning, and behavioral constraints in the capsule.

These tester and concurrent-package rules apply only to explicit experimental
profiles where those roles are permitted. Do not start a tester while the implementation
it must test is still running. Wait for the relevant worker to finish, then
give the tester the completed state and acceptance criteria. A tester must not
poll, wait for, coordinate, or inspect the status of sibling agents. The default
route never creates a tester and never has more than one child open.

## Delegated Route Entry

First route ordinary substantial independent work through Claude Opus High using
`claude-collab`. Keep the root responsible for acceptance. On an evidenced companion failure or incomplete package, stop the companion. Report the fallback reason. Pass only the remaining bounded work and relevant evidence to the native branch.

For a Sol-root native fallback package:

1. State the intended outcome and acceptance criteria.
2. Perform one bounded evidence pass over the smallest decision-critical
   context and form the Context Packet.
3. Give exactly one bounded implementation or read-only review package to a
   fresh `astra_executor_high`.
4. Keep High Astra open while Sol inspects the result and runs acceptance.
5. Return one ordinary repair to that same owner, if required. Otherwise close
   it after acceptance.
6. Only for a concrete intrinsically hard unresolved remainder, close High
   Astra and give one narrow delta packet to `astra_executor_xhigh`.

For Terra- or Luna-root native fallback work,
retain the existing Context Packet to `senior_executor_standard` route, with
only evidence-gated Astra escalation.

Exact experimental marker sections override this sequence only for their named
profiles.

## Adaptive Delegation Budget

This section applies only to explicit profiles with permission for multiple agents or waves. It does not override the default route's one-child model-aware lifecycle.
Treat the number of subagents as an adaptive budget, not a target and not an
absolute lifetime cap. A genuinely large task may use many agents across its lifetime. Each must own a distinct package or supply justified independent verification.

- Start a Delegated task with at most one wave of one or two bounded agents.
- Integrate the completed wave before opening another dependent wave.
- After four subagent sessions have completed for one root task, perform a
  delegation checkpoint before every additional wave. Identify open acceptance criteria and the distinct package for each new agent. Explain why an existing owner cannot complete it. Explain why delegation costs less or is more reliable than another root rollout.
- The checkpoint authorizes more agents when the remaining work is genuinely distinct. It is not a hard limit on large tasks.
- Do not create an agent merely because concurrency capacity is available.
- Avoid duplicate exploration, overlapping implementation, and broad repeated
  review without a new defect, risk, or acceptance criterion.
- Prefer a focused follow-up to the current owner for clarification, ordinary
  repair, and revalidation. A follow-up to the same agent is preferable to a
  replacement because it preserves package context.
- Create a replacement agent only after compliance with the focused retry rules in Implementation and Repair Ownership. A material reason to change ownership is also sufficient.

## Context Transfer

Ordinary companion requests follow the selected skill’s packet schema. The native
capsules below apply only to native fallback and the named experiments.

Initial subagents should normally start without inherited conversation history.
Use `fork_turns="none"` and provide a compact, self-contained task capsule. Do
not fork the full root transcript merely for convenience.
Use the selected role's configured model and reasoning effort rather than
inheriting the root's effort or reflexively selecting the maximum. Override a
role's effort only when the specific subtask and supported runtime justify it.

Every initial capsule begins with a stable Task ID and uses the role-specific
structure below.

When a Terra- or Luna-root branch uses `senior_executor_standard`, use the Worker
capsule structure and state `Research Slot: withheld`. For Sol-root native fallback with `astra_executor_high`, use the same Worker capsule structure. State that Sol owns acceptance. Explicitly prohibit child delegation.

### Explorer capsule

- `Task ID`
- `Investigation Context`
- `Evidence Question + Goal`
- `Scope and Source Boundaries`
- `Main-Agent Guidance`

Supply concise findings with exact file references, relevant evidence,
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
repair, and appropriate validation to the worker. Supply a concise report of
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
  investigate first when Terra has not run.
- `Experiment Marker`, repeating `EXPERIMENT: ASTRA_SOL_RESEARCH` when active
  or stating `none` otherwise, and
- `Research Slot`, explicitly `granted` or `withheld` (withheld by default).

The senior executor receives one bounded hard package, not the complete project
or an open-ended request.

For a follow-up, repeat the Task ID and send only changed facts, decisions,
scope, evidence, or acceptance criteria. Do not resend an unchanged capsule or
the full root history.

## Batching and Root Rollout Control

- Batch independent reads, searches, metadata checks, and other operations with
  known inputs.
- In profiles where multiple agents are permitted, dispatch independent agents needed
  for the same decision in one batch. The default route batches root reads but
  follows its single-child model-aware branch.
- Keep dependent work and overlapping mutations sequential.
- Wait for the relevant batch, then synthesize its results once.
- Open another batch only when new evidence materially changes the next task or
  decision.
- Do not ask agents for information already present in their reports.
- Keep worker reports compact. Retain raw logs and large output outside the
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

In Delegated work, do not let the root silently duplicate a distinct owner's
package. In the default route, the child owner receives at most one ordinary repair. The effective root supplies the failed criterion and exact expected-versus-observed evidence. Then, the root runs the affected acceptance checks again.
Do not add a tester.

The remaining ownership guidance applies only to experimental profiles that
give permission for replacement workers or testers.

- The assigned worker owns its package through ordinary implementation,
  self-check, focused repair, and revalidation.
- In experimental profiles with a tester, return an ordinary defect to the same worker with focused evidence. If independent rechecking is warranted, send the repair delta to the same tester.
- After one evidence-free or materially incomplete worker response, send one
  focused retry with the missing evidence or criterion.
- After a second focused failure, replace the worker, narrow the package, or
  escalate the decision. Do not enter an unbounded repair loop.
- Escalate to the root only for architecture or contract changes, conflicting packages, expanded ownership, or security or migration risk. Escalation is also permitted for ambiguous causal evidence or an external blocker.
- The root may make the required decision and issue a revised capsule. It should not take over routine production merely because a worker needed repair.

## Senior Executor Escalation Gate

This gate applies to the optional `senior_executor` role in profiles that expose
it. It does not apply to a runtime-overridden Terra- or Luna-root branch's primary
`senior_executor_standard`. For the optional role, use at most one senior executor at a time. At least one condition below must hold:

- one focused Terra worker attempt produced concrete evidence that the bounded
  package exceeds Terra's reasoning capability.
- The package is a high-uncertainty or difficult cross-component diagnosis. The capsule explains why Sol should investigate first. A failed Terra attempt is not required.
- The package is intrinsically difficult mathematical, algorithmic, logical, architectural, or cross-cutting work. The root can explain why Terra is unlikely to be reliable.
- A material architecture or contract decision has one hard remaining implementation package. Stronger reasoning is necessary for that package.

Do not escalate merely because a task is large or a worker still runs. An ordinary first-result repair or possible Sol speed improvement is also insufficient. Record the
qualifying evidence in the Senior Executor capsule. Give it non-overlapping
ownership, one focused attempt, and proportionate validation.

It must not spawn
subagents except for the explicitly granted Research Slot under the shared Sol
research-slot policy. If it cannot complete the package, return the decision to
the root. Do not create a chain of senior agents.

The active research profile's
Sol-primary rule supersedes this base-route gate.

## Verification

Match verification effort to risk.

Never write unit tests after writing production code. Invert the testing
pyramid: strongly prefer end-to-end (E2E) tests as the sole testing mechanism
for behavior changes. Make them black-box tests of complete workflows, using
golden-master outputs when appropriate, and use them to test complex features.
Reach for integration, component, or unit tests only when necessary because E2E
tests cannot reliably cover or diagnose a failure. Each E2E run must produce a verifiable, repeatable artifact. Include the tested revision, exact command and inputs, and expected and observed results.

Include saved evidence, such as logs, traces, or screenshots, when applicable. Report the artifact's location.

If isolated testing is necessary, first record all identifiable ways that the scoped system could fail. Encode those cases in isolated tests before production code. Then implement against those tests.

In the default route, the effective root owns verification and acceptance. Inspect the diff and affected contracts. Run proportionate deterministic checks and material edge cases. Distinguish product defects from harness or environment limitations. Do not create a tester or another model-review child.
The remaining tester guidance applies only to explicit profiles where it is permitted.

- Small reversible changes may rely on focused worker validation.
- Use `tester` for substantive behavior changes, regressions, important boundary
  cases, cross-component changes, or when independence materially improves trust.
- Do not create a separate tester for routine, low-risk, or easily reversible changes when deterministic worker checks already cover acceptance.
- A justified verification cycle may include explorer, worker, tester, and repair by the same worker. That same tester may perform a focused recheck. Preserve that cycle
  when the risk warrants it. Remove only duplicate or evidence-free passes.
- Prefer deterministic E2E tests, compilers, linters, schemas, and other
  executable gates over repeated model review.
- Do not add a separate model-review cycle when existing automated evidence is
  sufficient.
- Never weaken assertions, coverage, or failure visibility to save tokens.
- Never claim an unrun check passed.

## Completion

Before declaring a Delegated task complete, the root must:

1. Make sure that package reports cover the requested scope.
2. Resolve material conflicts and integrate results.
3. Make sure that proportionate verification completed successfully or clearly
   disclose what could not be run and why.
4. Make sure that no unrelated user work was overwritten.
5. Report the outcome, material changes, verification, and remaining risk
   concisely.

Perform an additional broad review or repeat completed checks only with new evidence, failure, material risk, or explicit user request.

## Claude companion and shared skills

For ordinary substantial work, `claude-collab` selects the external Claude Opus
High CLI companion first when a bounded independent review or patch package is
useful. Keep tiny tasks in Codex. Use the existing native model-aware branch only when the companion is unavailable, limited, stalled, or unable to complete the package. Record the reason. Stop the companion before the fallback owner starts. Follow
`~/.codex/skills/claude-collab/SKILL.md` for packet scope, quota-aware sizing,
subscription authentication, request limits, and acceptance.

Report this external route as `<effective-root>-claude`, separately from actual root model, reasoning, and observable tier. It is not a valid default Sol–Astra delegated benchmark.
Named opt-in experimental routes remain authoritative. Never run the companion and a native child concurrently on the same task. Never invoke the bridge recursively from a companion request. Plan Mode remains read-only.

The shared user-skill library lives in `~/.codex/skills`. The bridge's
`sync-skills` helper maintains individual owned symlinks under `~/.claude/skills`.
Run it after installing user skills. The bridge also syncs before requests.

Preserve independent Claude skills and exclude hidden/system directories.
Codex uses `$skill-name`, while ordinary Claude sessions use `/skill-name`.
Companion requests explicitly bundle selected skill contents and required references. Skill instructions do not expand scope or grant extra tools.

This workflow has a subscription-only exception to the generic API-key rule above. Use the existing `claude.ai` login. Never load `~/.env`, read credential contents, or use an API-key fallback. Do not modify authentication or billing or enable
Extra Usage.

Sanitized child authentication must pass a check before each request. OAuth selection cannot disable account overages already enabled by the user.
Codex alone reviews, applies, tests, and accepts returned patches.
