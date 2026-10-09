# Design It Twice

Compare different interfaces for the selected candidate before a structural change.
Use [SKILL.md](SKILL.md) for vocabulary and [DEEPENING.md](DEEPENING.md) for dependency decisions.
Keep project domain terms.
Use English unless the user explicitly requests another output language.

## Frame the decision

State the observed problem, caller workflows, behavior and compatibility contracts, constraints, and material dependencies.
A small example can explain the problem without selection of a solution.
Resolve only uncertainties that would change the decision.

## Develop contrasting alternatives

Develop at least two meaningfully different designs, one after another.
Add another design only to examine a material design difference.
Possible priorities include these items:

- Reduce the knowledge necessary for callers. Preserve necessary distinctions.
- Support justified variation and extension. Do not invent features.
- Simplify the common caller workflow. Keep exceptional behavior explicit.
- Move a dependency seam when that change concentrates real complexity in one location.

Direct sequential analysis is sufficient.
Delegate only when delegation is permitted or mandatory under the active AGENTS instructions and routing.
Follow their ownership, model, concurrency, and acceptance rules.
This pattern mandates neither parallel agents nor a particular model.
It never gives a child permission to delegate further.

For each alternative, show these items:

1. The interface and complete contract. Include types, parameters, invariants, order, errors, compatibility, and relevant operational behavior.
2. A realistic example of the common workflow and each material exceptional case.
3. The logic and complexity behind the interface.
4. The dependency strategy, seam placement, and adapters justified by the task.
5. Differences in leverage, locality, testability, migration cost, and other material constraints.

## Compare and recommend

Present the alternatives in sequence.
Then, compare them against the same observable criteria.
Explain depth, caller burden, locality of change, seam placement, preserved contracts, and verification effects.
Recommend the strongest design with evidence.
Propose a hybrid only when the combination remains coherent.
State assumptions and unresolved decisions explicitly.

Continue to implementation only with existing authorization and a mode in which writes are permitted.
A design or review request alone gives no additional permission to edit code or documentation.
