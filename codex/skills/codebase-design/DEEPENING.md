# Deepening

Deepen a cluster only when evidence shows less friction.
Preserve coherent responsibilities and existing contracts.
Use the vocabulary in [SKILL.md](SKILL.md).
Follow the repository's test instructions.

## Dependency guide

Classify dependencies before selection of a verification strategy.
These categories guide decisions. They do not mandate new abstractions.

| Category | Design and verification considerations |
| --- | --- |
| In-process | Exercise pure computation or in-memory state through the module interface when possible. Combine responsibilities only when they belong together. An adapter is not inherently necessary. |
| Local-substitutable | A database or filesystem can have a useful local substitute, such as PGLite or an in-memory filesystem. Reuse existing test facilities. Examine semantic differences. When necessary, compare material behavior with the real dependency. Keep test substitution internal when that knowledge is unnecessary for callers. |
| Remote but owned | An owned service's HTTP, gRPC, or queue contract can supply the seam. A port and transport adapter can keep business logic local when variation justifies them. A justified test adapter supports deterministic workflows. Retain tests of the real protocol's important behavior. |
| True external | For third-party services, reuse the existing client or a narrow injected dependency when useful. Mocks, fakes, fixtures, and sandbox integration tests must reflect documented contracts, errors, and material side effects. A mock alone does not prove external compatibility. |

## Seam discipline

An external seam belongs to the module's contract with callers.
Internal seams remain private implementation details, including those that support tests.
Do not enlarge the public interface merely for test setup.

Introduce ports or adapters only for actual dependency variation, an external contract, or a concrete test constraint.
Two useful adapters are evidence of variation. They are not a minimum quota.
Do not create speculative adapters.
Do not discard a meaningful single-adapter boundary merely because it has one adapter.

## Testing through the workflow

Follow repository test rules. Preserve meaningful coverage during refactoring.
Prefer observable results from the complete workflow or module interface.
Include relevant errors, order, state changes, and dependency effects.
Make sure that the same behavior remains observable before and after the change.

Keep existing tests until successful replacements cover the meaningful behavior that they protect.
Before removal of a redundant shallow-module test, identify its protected behavior.
Make sure that replacement tests cover that behavior. Run the relevant checks successfully.
Only then remove the redundant test.

Keep tests that protect unique contracts or diagnose failures that broader workflows cannot reliably cover.
Never delete tests unconditionally merely because a module has more depth.

Prefer observable assertions when they suffice.
Avoid assertions about incidental internal structure in that case.
Use internal tests when reliable coverage or diagnosis makes them necessary.
Record the checks that ran and the remaining verification limits.
