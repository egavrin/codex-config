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

Use Light for questions, reviews, diagnostics, tiny edits, and other bounded work
that one agent can finish with a few focused operations. Work directly without
subagents. Do not create coordination overhead for a small task.

### Heavy route

Use Heavy when the request requires material repository exploration plus
implementation, affects multiple components, benefits from independent work,
has meaningful verification needs, or is otherwise likely to require many root
tool/model turns.

In Heavy, the root is the director, not the routine production worker:

- The root owns task interpretation, scope, architecture, causal and strategic
  decisions, package boundaries, integration, acceptance, and user communication.
- Use `explorer` for bounded read-only repository investigation.
- Use `worker` for bounded implementation, ordinary debugging, repair, and
  implementation-owned validation.
- Use `tester` for independent verification when the change is substantive,
  risky, cross-cutting, or has important acceptance criteria.
- Use `senior_executor` only for one exceptionally difficult bounded package
  that requires stronger mathematical, logical, architectural, or cross-cutting
  reasoning, subject to the escalation gate below.
- An untyped/default subagent is acceptable only when neither named role fits;
  it must still receive a bounded task and must not spawn subagents.
- Do not use Sol or Astra as subagents unless the user explicitly requests it or
  one focused Terra attempt proves that the package requires stronger reasoning.
- Never run more than two subagents concurrently. Subagents must not create
  nested subagents.

If the route is not obvious, prefer Light for a genuinely small request and
Heavy for a substantial implementation. Do not use a half-delegated pattern in
which the root performs all production work while also paying coordination cost.

## Root Reasoning Presets

Use the configured Astra Medium preset as the default for both Light and Heavy
route entry. Route selection determines whether delegation is justified; it does
not require the root to change its own reasoning effort.

Codex Desktop may automatically promote the root to Extra High when its
multi-agent v2 runtime is engaged. Treat that as a runtime-controlled override:
do not request Extra High merely because a task uses the Heavy route, do not
enter Heavy solely to obtain Extra High, and do not spend additional root turns
trying to change the preset from instructions. If the runtime exposes an
explicit preset choice, keep Medium unless the user selects Extra High or the
task is exceptionally difficult enough to justify its additional usage.

## Runtime Routing Contract

Task names do not activate the role profiles in `~/.codex/agents/`. When the
collaboration tool accepts model and reasoning overrides, pass the configured
values explicitly on every initial spawn:

| Role | Model | Reasoning |
|------|-------|-----------|
| `explorer` | `gpt-5.6-luna` | `medium` |
| `worker` | `gpt-5.6-terra` | `high` |
| `tester` | `gpt-5.6-luna` | `high` |
| `senior_executor` | `gpt-5.6-sol` | `medium` |

Do not route an `explorer` or `tester` to the default Terra model merely because
its task name contains the role name. A task such as `tester`, `explorer_apps`,
or `explorer_repository` remains untyped unless the runtime applies the matching
role profile. If typed roles are unavailable, use the table above as the
effective routing contract and include the role's behavioral constraints in the
task capsule.

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

Use the Worker capsule structure, but explicitly add `Escalation Evidence` that
states why Terra is insufficient. The senior executor receives one bounded hard
package, not the complete project or an open-ended request.

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

`senior_executor` is a costly exception, never the default implementation path.
Use at most one senior executor at a time and only when at least one condition is
true:

- one focused Terra worker attempt produced concrete evidence that the bounded
  package exceeds Terra's reasoning capability;
- the package is intrinsically difficult mathematical, algorithmic, logical,
  architectural, or cross-cutting work and the root can explain why Terra is
  unlikely to be reliable;
- a material architecture or contract decision has been narrowed to one hard
  implementation package that genuinely needs stronger reasoning.

Do not escalate merely because a task is large, a worker is still running, the
first result needs an ordinary repair, or Sol might be faster. Record the
qualifying evidence in the Senior Executor capsule. Give it non-overlapping
ownership, one focused attempt, and proportionate validation. It must not spawn
subagents. If it cannot complete the package, return the decision to the root;
do not create a chain of senior agents.

## Verification

Match verification effort to risk.

- Small reversible changes may rely on focused worker validation.
- Use `tester` for substantive behavior changes, regressions, important boundary
  cases, cross-component changes, or when independence materially improves trust.
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
