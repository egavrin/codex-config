# Deepening

Deepen a cluster only when it reduces evidenced friction without losing coherent responsibilities or existing contracts. Use the vocabulary in [SKILL.md](SKILL.md) and follow repository testing instructions.

## Dependency guide

Classify dependencies to choose an appropriate verification strategy; these categories guide decisions rather than mandate new abstractions.

| Category | Design and verification considerations |
| --- | --- |
| In-process | Pure computation or in-memory state can often be exercised directly through the module's interface. Consolidate only when responsibilities belong together; no adapter is inherently needed. |
| Local-substitutable | A database or filesystem may have a useful local stand-in, such as PGLite or an in-memory filesystem. Reuse available test facilities, assess semantic differences, and verify material behavior against the real dependency when necessary. Keep test substitution internal when callers need not know about it. |
| Remote but owned | For owned services, an existing HTTP, gRPC, or queue contract may provide the seam. A port and transport adapter can keep business logic local when variation warrants them. A justified test adapter helps deterministic workflows; retain checks of the real protocol's important behavior. |
| True external | For third-party services, reuse the existing client or a narrow injected dependency when useful. Mocks, fakes, fixtures, or sandbox integration checks must reflect documented contracts, errors, and material side effects. A mock alone does not establish external compatibility. |

## Seam discipline

An external seam belongs to the module's caller-facing contract. Internal seams remain private implementation details, even when useful to tests. Avoid widening the public interface just for test setup.

Introduce ports or adapters when actual dependency variation, an external contract, or a concrete testing constraint justifies them. Two useful adapters are evidence of variation, not a minimum quota. Do not create speculative adapters or discard a meaningful single-adapter boundary solely because of its count.

## Testing through the workflow

Follow repository testing rules and preserve meaningful coverage during refactoring. Prefer observable outcomes through the complete workflow or the module's interface, including relevant errors, ordering, state changes, and dependency effects. Verify that the same behavior remains observable before and after the change.

Retain existing tests until successful replacements cover the meaningful behavior they protect. Remove a redundant shallow-module test only after identifying its protected behavior, verifying replacement coverage, and successfully running the relevant checks. Keep tests that still protect unique contracts or diagnose failures not reliably covered by the broader workflow. Never delete tests unconditionally merely because a module has been deepened.

Avoid assertions tied to incidental internal structure where observable assertions suffice. Internal tests remain appropriate where needed for reliable coverage or diagnosis. Record which checks ran and any remaining verification limits.
