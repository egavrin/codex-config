---
name: codebase-design
description: Design or evaluate module interfaces, architectural seams, dependency strategies, and behavior-preserving structural refactors using deep-module principles. Use for substantive architecture and interface decisions or shared architecture vocabulary, not routine tiny code cleanups.
---

# Codebase Design

Design **deep modules**: meaningful behavior behind an interface that hides complexity, gives callers leverage, and keeps related changes local. Apply these principles within the user's scope, existing contracts, repository instructions, and permitted mode. Report in the user's conversation language and retain project identifiers. Design alternatives do not authorize implementation.

## Shared vocabulary

Map these terms to actual project terminology. A service, component, API, or domain boundary can remain named as such; the vocabulary clarifies its architectural role rather than forcing a rename.

- **Module**: a function, class, package, or larger slice with an interface and an implementation.
- **Interface**: everything a caller must know: signatures, invariants, ordering, errors, configuration, performance, and other behavioral contracts. It is broader than a language's `interface` declaration. Consider all entry points and caller groups rather than requiring exactly one formal interface.
- **Implementation**: the behavior and machinery hidden inside the module.
- **Depth**: leverage at the interface, not a ratio of implementation lines to interface lines. A deep module hides substantial complexity; a shallow one exposes nearly as much complexity as it handles.
- **Seam**: a place where behavior can vary without editing the consuming logic. Placement of a seam is distinct from what it hides.
- **Adapter**: a concrete implementation of an interface at a seam; the term describes its role, not its size.
- **Leverage**: capability callers gain per amount of interface knowledge they need.
- **Locality**: related changes, knowledge, failures, and verification concentrate in a coherent place instead of spreading across callers.

## Design criteria

**Preserve behavior and existing contracts.** Structural improvements must account for ordering, errors, side effects, compatibility, performance, and operational constraints. Make any intended contract change explicit and keep it within the authorized task.

**Apply the deletion test.** Imagine removing a module. Complexity disappearing can indicate redundant forwarding. Complexity reappearing across callers indicates useful depth. Check domain responsibilities and compatibility obligations before recommending removal.

**Treat the interface as the primary test surface.** Prefer observable complete workflows and behavior through the interface. Use internal tests when needed to reliably cover or diagnose a failure, according to repository testing instructions. A test of internals is evidence to assess, not automatic proof of bad design.

**Use small interfaces where they reduce caller burden.** Fewer methods and parameters can help, but hiding required distinctions or creating a giant multipurpose entry point can make an interface worse. Depth is not a mandate to merge unrelated responsibilities.

**Introduce seams for real variation or constraints.** Two justified adapters can demonstrate useful variation, but adapter count is not a rule. One adapter may support a real external or architectural contract. Never invent an adapter merely to meet a slogan.

**Use dependency injection selectively.** Accept a dependency when controlled variation, external effects, or test setup justify it. Constructing a stable internal dependency can be simpler; do not expose every implementation detail in the public interface.

**Isolate computation when it improves reasoning.** Returning values can simplify deterministic checks, while workflows legitimately perform side effects. Do not extract pure functions solely to make isolated tests easy when doing so scatters the workflow's logic.

## Focused guidance

- Read [DEEPENING.md](DEEPENING.md) when restructuring a cluster: dependency categories, internal/external seams, and preserving meaningful verification.
- Read [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) when contrasting alternative interfaces: sequential designs, contract comparisons, usage, and tradeoffs.

## Source and adaptation

Locally adapted from Matt Pocock's skills for Codex. See [PROVENANCE.md](PROVENANCE.md) for the upstream source, pinned revision, adaptation details, and license.
