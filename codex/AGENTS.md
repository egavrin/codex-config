# Cost-Efficient Codex Orchestration

## Controlled English

Use English for user responses, agent messages, and new technical documents.
An explicit request for another output language takes precedence.
Read `~/.codex/skills/writing-for-agents/references/controlled-english.md` for the shared writing profile.
The profile derives from ASD-STE100 Issue 9 and defines software and agent extensions.
Preserve exact identifiers, commands, quotations, and required product text.
Preserve scope, permissions, exceptions, and verification requirements when you change prose.

This language rule does not authorize a document edit or change an orchestration route.

## Ponytail compatibility

When Ponytail applies, read ~/.codex/ponytail-policy.md.
Its solution preferences supplement the active scope, language, verification, and routing instructions.
Ponytail modes do not change permissions or authorize another agent.
The off mode does not disable existing instructions.

## Objective

Use the root model to understand the request, collect bounded evidence, define scope, integrate results, and perform acceptance.
The assigned technical owner chooses the implementation approach and architecture within its package.
Follow the effective-root branch for ordinary work.
Assign one bounded implementation or substantive read-only review package when that branch requires delegation.
Exact experimental marker sections may define other role sequences.

Optimize for completing the user's task with fewer root-model rollouts and less
repeated root context. Do not optimize token usage by weakening correctness,
skipping necessary verification, or producing incomplete work.

## API Keys and Local Environment

`~/.env` contains the user's API keys for available services.
You may use the required keys for authorized tasks, subject to existing authentication and approval rules.

When an API key or credential is necessary for a task, preserve any non-empty value
already set in the environment. If the required variable is absent or empty,
load it from `~/.env` before calling the service.
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

Choose exactly one orchestration route before substantive work.
Direct and Delegated are task-routing classes, not Desktop reasoning labels.

### Normal model-aware routing

The marker `PROFILE: TERRA_SOL_CLAUDE_REVIEW` selects the normal policy.
The local default is `gpt-6.1-terra` with `high` reasoning and Standard service tier (`default`).
Desktop and runtime overrides for model, reasoning, and service tier remain authoritative.
Named opt-in experiments retain their exact routes, roles, effort, and lifecycle rules.

### Direct and Delegated work

All normal code changes, including tiny edits, require Sol ownership and the Claude completion review below.
Terra and Luna assign each code package to one fresh `sol_implementer_high` with `gpt-6.1-sol`, `high`, and `default`.
A Sol root implements directly. Do not spawn Sol from Sol.
For another effective root override, retain that root and assign normal code packages to Sol.
Keep app operations, visual/Blender artifacts, bounded prose, and questions in the effective root.
A `bpy` helper script for an app artifact remains app work. Software and addon development count as code changes.
Terra and Luna also delegate substantive debugging, architecture, and technical review to Sol.
An explicitly read-only Sol package has no duplicate Claude review gate.
Prefer APIs, CLIs, and purpose-built tools. Use GUI control when necessary or explicitly requested.

No automatic Astra fallback, separate verifier, second native opinion, or nested delegation is permitted.
Preserve Astra role files and named experiments. Their presence does not activate a normal route.
Extra High requires an explicit user request or a named experiment.

### Ownership and completion

Before delegation, collect one bounded evidence pass and form the Context Packet.
Start the owner with `fork_turns="none"` and `Research Slot: withheld`.
The owner chooses the implementation and performs one lightweight focused check.
Do not duplicate its package or prescribe its detailed implementation.
After code and self-check, follow the Claude completion review procedure.
Run bridge `preflight` before `run --mode review` with the current packet.
Use one primary review and at most one concrete retry or delta, two calls total per package.
If review cannot run, report `review_unavailable` and `failure_stage`, preserve evidence, and continue authorized work and deterministic checks.
The effective root owns integration and final acceptance.
Inspect the diff and affected contracts. Run proportionate deterministic checks and material edge cases.
Distinguish product defects from harness or environment limitations.
Keep the implementation owner available and idle through acceptance.
Send at most one ordinary repair to that same owner, with exact expected-versus-observed evidence.

### Native child lifecycle

Allow one active child and at most 32 retained native children per ordinary session.
Count retained children across tasks. The configured depth remains one.
Each new package may receive a fresh owner after the previous owner finishes.
The external completion reviewer is not a native child.
Sol pauses edits during its synchronous review. No other native owner works concurrently.
This is the narrow exception to the companion/native-child concurrency restriction.
Retain the completed owner for root acceptance and its one ordinary repair.
Use native close or release after acceptance when available.
If unavailable, report the limitation and retain the completed owner idle within the cap.
An interrupt is not a close or release operation.
Completion, interruption, and archiving do not prove that a slot was released.
If the retained-thread capacity is exhausted, report the actual limit.
If another owner is required and release is unavailable, prepare a concise handoff for a fresh session.
Do not create a new session without the required user request.
Do not evade the cap through visible tasks, forks, nested CLI calls, or another owner.

### Capability-aware default fallback

Use native collaboration for internal delegation.
Do not substitute `create_thread`, `fork_thread`, `send_message_to_thread`, or nested `codex exec` automatically.
If collaboration or the required role is unavailable, report the concrete limitation and configuration drift.
The effective root may complete authorized work directly when intended delegation fails.
Apply the same completion review to code changes in that fallback.
Report `effective_route = <root>-single-agent-fallback` only for failed intended delegation.
Exclude these sessions from valid delegated-route benchmarks.
A healthy active child or the retained-child cap does not justify ownership transfer.
Wait for the owner or use its permitted repair.
Report the actual root model, reasoning, and observable service tier separately.
Report normal routes as `terra-direct`, `terra-sol-claude-review`, `luna-direct`, `luna-sol-claude-review`,
`sol-claude-review`, or `<effective-root>-sol-claude-review` for another root override.
For read-only Sol packages, omit the `-claude-review` suffix.
Record the review result separately. A route name does not prove review success.
Do not infer latency, quality, or quota savings from the reasoning level.

## Claude completion review

This gate applies to all normal code changes, including tiny edits and code changes by an effective Sol root.
It excludes bounded prose, app-only artifact scripts, and read-only technical reviews.
Named experiments retain their exact procedures unless the user explicitly changes the experiment.
The named normal policy is standing authorization for this specific external completion review.
It does not authorize Claude implementation, a general automatic companion route, or broader skill selection.

1. Complete the code and one focused self-check.
2. Read `~/.codex/skills/claude-collab/SKILL.md` and its `references/bridge.md` procedure.
3. Build the existing nine-field packet from current scope, sources, instructions, diffs, acceptance criteria, and uncertainties.
4. Include required shared policies and selected skill references without changing the schema or the 256 KiB limit.
5. Run `preflight --mode review --packet FILE` and correct local validation errors before any model request.
6. Run `run --mode review --packet FILE` through the existing bridge with Opus High.
7. Require a review-only result with an empty `diff`.
8. Check each finding against the code and task evidence.
9. Fix confirmed relevant findings within scope and reject unsupported or out-of-scope findings with reasons.
10. Escalate material scope or contract decisions to the root.
11. Run the affected deterministic checks and report findings, decisions, artifacts, and remaining criteria.

Sol pauses edits while the synchronous external reviewer works.
No other native owner works concurrently. Do not create native children or invoke the bridge recursively.
Use one primary review plus at most one concrete retry or delta, two calls total per package.
A retry requires an invalid response, missing material, or a later root repair with concrete evidence.
Do not request another review merely because Sol fixed review findings.
Do not create reciprocal review loops.

If authentication, quota, CLI, or inactivity prevents review, stop that request and preserve the evidence.
Continue authorized implementation and deterministic checks with explicit `review_unavailable` and `failure_stage` disclosure.
Never claim that an unavailable review passed. Correct local preflight errors before sending.
Use only the existing subscription login. Do not read `~/.env`, use API fallback, change authentication or billing, or enable Extra Usage.
Preserve the helper's isolation, policies, progress reporting, validation, and timeout behavior.
The root owns final acceptance after Sol reports the completed work and review outcome.

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

The local default is GPT-6.1 Terra with High reasoning on Standard service tier.
The default configuration values are `gpt-6.1-terra`, `high`, and `default`.
Desktop model, reasoning, and tier overrides are user choices. Respect and report the effective values.
Never describe an effective root as a different model.

Light, Medium, High, Extra High, and MAX name reasoning levels where the selected model and runtime support them. They do not select Direct or Delegated routing.
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
one-active-child, no-nesting, and no-Astra-from-Astra rules for this opt-in experiment.
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

The marker `PROFILE: ASTRA_TERRA_STANDARD` comes from `astra-terra-standard.config.toml` and selects a historical comparison. It uses an Astra Medium root on Standard tier and Terra High for clear bounded implementation. Luna High testing is permitted only with independent justification. Selective Sol use is permitted under the Senior Executor Escalation Gate. This explicit profile overrides the normal routing policy while active.

## Terra-Luna-Sol-Astra experiment

This policy changes only when the root developer instructions contain the exact
marker `EXPERIMENT: TERRA_LUNA_SOL_ASTRA`, supplied by the
`terra-luna-sol-astra.config.toml` CLI profile. The marker overrides the normal routing policy while selected. Terra Medium Fast coordinates work, compacts Context Packets, integrates acceptance, and communicates final results. It does not routinely investigate, plan technical work, implement, or run acceptance.

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
`luna-terra-context-sol-astra.config.toml` CLI profile. This is an isolated comparison route. It does not change the normal routing policy or full Terra-root `TERRA_LUNA_SOL_ASTRA` experiment.

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

This native Context Packet contract applies to ordinary Delegated work and the named native experiments.

Before implementation, the root collects decision-relevant facts for these routes:
- Normal Terra- or Luna-root delegation to `sol_implementer_high`.
- Normal code delegation from another effective root to `sol_implementer_high`.
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

Only when a named experiment explicitly permits Astra escalation, the root sends Astra a delta packet. Include the unresolved acceptance criterion, relevant original packet facts, and Sol's concrete evidence. Include current changed paths and the smallest remaining ownership surface. Do not resend completed work or the original
packet wholesale.

## Sol research-slot policy

This policy applies whenever a selected `senior_executor` receives a Sol package,
in an explicit profile that permits this role and nested research.
The normal `sol_implementer_high` role never receives a Research Slot. A Research Slot is
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
| `sol_implementer_high` | `gpt-6.1-sol` | `high` | `default` |
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

Astra rows describe preserved experimental roles only. Base configuration does not register automatic Astra owners.

The standalone agent files document intended restrictions but do not by
themselves prove that a runtime tool or sandbox profile was applied. State a sandbox guarantee only after a check of the effective restriction. Otherwise, supply explicit model, reasoning, and behavioral constraints in the capsule.

These tester and concurrent-package rules apply only to explicit experimental
profiles where those roles are permitted. Do not start a tester while the implementation
it must test is still running. Wait for the relevant worker to finish, then
give the tester the completed state and acceptance criteria. A tester must not
poll, wait for, coordinate, or inspect the status of sibling agents. The default
route never creates a tester. It permits one active child and at most 32 retained children per ordinary session.

## Delegated Route Entry

Follow the normal effective-root branch unless an exact experimental marker selects another route.
The root owns integration and acceptance.

1. State the outcome and observable acceptance criteria.
2. Collect one bounded evidence pass and form the Context Packet.
3. Assign normal code changes, including tiny edits, to a fresh `sol_implementer_high` with no inherited history.
4. Require the Claude completion review after code and self-check, before the owner reports completion.
5. Keep Sol idle and available during root acceptance.
6. Return at most one ordinary repair with concrete evidence to that owner.
7. Apply the native lifecycle rules before dispatch and after acceptance.

A Sol root owns implementation directly and performs the same Claude completion review.
Explicitly read-only technical packages do not require a duplicate Claude gate.
No automatic Astra fallback is permitted. Preserve named experiments and explicit user overrides.

## Adaptive Delegation Budget

This section applies only to explicit profiles with permission for multiple agents or waves. It does not override the normal route's one-active-child and 32-retained-child limits per ordinary session.
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

The native capsules below apply to ordinary Delegated work and the named native experiments.

Initial subagents should normally start without inherited conversation history.
Use `fork_turns="none"` and provide a compact, self-contained task capsule. Do
not fork the full root transcript merely for convenience.
Use the selected role's configured model and reasoning effort rather than
inheriting the root's effort or reflexively selecting the maximum. Override a
role's effort only when the specific subtask and supported runtime justify it.

Every initial capsule begins with a stable Task ID and uses the role-specific
structure below.

For normal `sol_implementer_high` delegation, use the Worker capsule and state `Research Slot: withheld`.
For normal code packages, include the Claude completion review requirement and the remaining two-call budget.
Use Astra delta capsules only when a named experiment explicitly permits them.
State that the effective root owns integration and acceptance. Explicitly prohibit child delegation.
Named experiments that use `senior_executor_standard` retain their Worker capsule and `Research Slot: withheld` requirements.

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
  follows its one-active-child model-aware branch.
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
it. It does not apply to normal `sol_implementer_high` delegation or a named experiment's primary `senior_executor_standard`. For the optional role, use at most one senior executor at a time. At least one condition below must hold:

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

For normal code changes, record the Claude completion review outcome and artifacts before root acceptance.
If unavailable, disclose `review_unavailable` and `failure_stage`. Never substitute that disclosure for deterministic checks.

Before declaring a Delegated task complete, the root must:

1. Make sure that package reports cover the requested scope.
2. Resolve material conflicts and integrate results.
3. Make sure that proportionate verification completed successfully or clearly
   disclose what could not be run and why.
4. Make sure that no unrelated user work was overwritten.
5. Report the outcome, material changes, verification, and remaining risk
   concisely.

Perform an additional broad review or repeat completed checks only with new evidence, failure, material risk, or explicit user request.

## Shared skills and explicit Claude requests

The normal `PROFILE: TERRA_SOL_CLAUDE_REVIEW` policy authorizes only its specific completion review through `claude-collab`.
Read the Claude completion review section for its trigger, procedure, concurrency exception, and failure handling.
Other companion calls require an explicit Claude request or `$claude-collab` invocation.
Task size, Codex quota, and a native failure do not independently authorize Claude.
The skill must keep `allow_implicit_invocation: false`.

For an explicit Claude request, follow `~/.codex/skills/claude-collab/SKILL.md`.
Report that manual external route as `<effective-root>-claude`, separately from root model, reasoning, and observable tier.
It is not a default native-route benchmark.
Except for the synchronous Sol completion review, never run the companion and a native child concurrently on the same task.
Never invoke the bridge recursively from a companion request.
Plan Mode remains read-only.
Codex owns scope, integration, patch application, tests, and final acceptance.

The shared user-skill library lives in `~/.codex/skills`.
The bridge's `sync-skills` action maintains owned symlinks under `~/.claude/skills` without a model request.
Run it after installing user skills.
Preserve independent Claude skills and exclude hidden/system directories.
Codex uses `$skill-name`, while ordinary Claude sessions use `/skill-name`.
Explicit companion requests bundle selected skill contents and required references.
Skill instructions do not expand scope or grant extra tools.

All authorized companion requests have a subscription-only exception to the generic API-key rule.
Use the existing `claude.ai` login.
Never load `~/.env`, read credential contents, or use an API-key fallback.
Do not modify authentication or billing or enable Extra Usage.
Sanitized child authentication must pass a check before each request.
OAuth selection cannot disable account overages already enabled by the user.
Codex alone reviews, applies, tests, and accepts returned patches.

## Graphify code discovery

For architecture, dependency tracing, or substantial repository discovery, use the shared `graphify` skill when appropriate.
Read `~/.codex/skills/graphify/SKILL.md` before its first use.
For a small edit at a known location, use focused source searches directly.
Graphify does not change routing, permissions, or Plan Mode.

## Mandatory Slopo commit review

Before creating or amending any Git commit, follow `~/.codex/skills/slopo-review/SKILL.md`.
Complete the review and resolve blocking findings before committing.
This requirement includes documentation-only commits.
It does not authorize commits or change Plan Mode, Git hooks, or manual workflows.

## RTK command output

@/Users/egavrin/.codex/RTK.md

Use raw output for exact machine data, source evidence, searches, full diffs, mutating Git commands, and bridge packets.
Use the configured hook exclusions or `RTK_DISABLED=1` for these commands.
Do not prefix every command with RTK.
