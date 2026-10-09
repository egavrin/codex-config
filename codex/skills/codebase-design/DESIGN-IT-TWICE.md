# Design It Twice

Explore contrasting interfaces for a chosen candidate before committing to a structural change. Use [SKILL.md](SKILL.md) for vocabulary and [DEEPENING.md](DEEPENING.md) for dependency considerations. Keep project domain terminology and present the discussion in the user's conversation language.

## Frame the decision

State the observed problem, caller workflows, behavior and compatibility contracts, constraints, and material dependencies. A small illustrative sketch can ground the problem without choosing the answer. Resolve only uncertainties that would change the decision.

## Develop contrasting alternatives

Develop at least two meaningfully different designs sequentially. Add another only when it explores a material tradeoff. Useful contrasting priorities include:

- Minimize what callers must learn while preserving required distinctions.
- Support justified variation and extension without speculative features.
- Make the common caller's workflow simple while retaining explicit exceptional behavior.
- Move a dependency seam when that would localize real complexity.

Direct sequential analysis is sufficient. Delegate only when the active AGENTS instructions and routing allow or require it, respecting their ownership, model, concurrency, and acceptance rules. This pattern requires neither parallel agents nor a particular model, and never authorizes a child to delegate further.

For each alternative show:

1. The interface and full contract: types, parameters, invariants, ordering, errors, compatibility, and relevant operational behavior.
2. A realistic usage example for the common workflow and any material exceptional case.
3. The logic and complexity hidden behind the interface.
4. The dependency strategy, seam placement, and adapters actually justified by the task.
5. Tradeoffs in leverage, locality, testability, migration cost, and other material constraints.

## Compare and recommend

Present alternatives in sequence, then compare them against the same observable criteria. Explain depth, caller burden, locality of change, seam placement, preserved contracts, and verification implications. Recommend the strongest design with evidence; propose a hybrid only when the combination remains coherent. State assumptions and unresolved decisions explicitly.

Continue into implementation only when it is already authorized and the active mode permits writes. A design or review request alone does not expand permission to edit code or documentation.
