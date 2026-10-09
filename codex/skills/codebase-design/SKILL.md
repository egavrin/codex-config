---
name: codebase-design
description: "Design or evaluate module interfaces, architectural seams, dependency strategies, and structural refactors that preserve behavior. Apply deep-module principles. Use for substantive architecture and interface decisions or shared architecture terminology. Exclude routine tiny code cleanups."
---

# Codebase Design

Design **deep modules**. Put meaningful behavior behind an interface that hides complexity, gives callers leverage, and keeps related changes local. Apply these principles within the user's scope, existing contracts, repository instructions, and permitted mode. Use English unless the user explicitly requests another output language. Retain project identifiers. Design alternatives do not authorize implementation.

## Shared vocabulary

Map these terms to actual project terminology. Keep existing service, component, API, and domain-boundary names. Use this vocabulary to explain architectural roles. Do not rename items merely to match it.

- **Module**: a function, class, package, or larger slice with an interface and an implementation.
- **Interface**: everything a caller must know: signatures, invariants, ordering, errors, configuration, performance, and other behavioral contracts. It is broader than a language's `interface` declaration. Consider all entry points and caller groups without an arbitrary limit of one formal interface.
- **Implementation**: the behavior and machinery hidden inside the module.
- **Depth**: leverage at the interface, not a ratio of implementation lines to interface lines. A deep module hides substantial complexity. A shallow module exposes nearly as much complexity as it handles.
- **Seam**: a place where behavior can vary without editing the consuming logic. Placement of a seam is distinct from what it hides.
- **Adapter**: a concrete implementation of an interface at a seam. The term describes its role, not its size.
- **Leverage**: capability callers gain per amount of necessary interface knowledge.
- **Locality**: related changes, knowledge, failures, and verification concentrate in a coherent place instead of spreading across callers.

## Design criteria

**Preserve behavior and existing contracts.** Structural improvements must account for ordering, errors, side effects, compatibility, performance, and operational constraints. Make any intended contract change explicit and keep it within the authorized task.

**Apply the deletion test.** Imagine removing a module. Complexity disappearing can indicate redundant forwarding. Complexity reappearing across callers indicates useful depth. Examine domain responsibilities and compatibility obligations before recommending removal.

**Treat the interface as the primary test surface.** Prefer observable complete workflows and behavior through the interface. Use internal tests when needed to reliably cover or diagnose a failure, according to repository testing instructions. A test of internals is evidence to assess, not automatic proof of bad design.

**Use small interfaces where they reduce caller burden.** Fewer methods and parameters can help. But an interface can become worse if it hides required distinctions or combines too many purposes. Depth is not a mandate to merge unrelated responsibilities.

**Introduce seams for real variation or constraints.** Two justified adapters can demonstrate useful variation, but adapter count is not a rule. One adapter can support a real external or architectural contract. Never invent an adapter merely to meet a slogan.

**Use dependency injection selectively.** Accept a dependency when controlled variation, external effects, or test setup justify it. A stable dependency that the module creates internally can be simpler. Do not expose every implementation detail in the public interface.

**Isolate computation when it improves reasoning.** Returning values can simplify deterministic checks, while workflows legitimately perform side effects. Do not extract pure functions solely to make isolated tests easy when doing so scatters the workflow's logic.

## Focused guidance

- Read [DEEPENING.md](DEEPENING.md) when restructuring a cluster: dependency categories, internal/external seams, and preserving meaningful verification.
- Read [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) when contrasting alternative interfaces: sequential designs, contract comparisons, usage, and tradeoffs.

## Source and adaptation

Locally adapted from Matt Pocock's skills for Codex. See [PROVENANCE.md](PROVENANCE.md) for the upstream source, pinned revision, adaptation details, and license.
