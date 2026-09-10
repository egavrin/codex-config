# Discovery Heuristics

Use these heuristics to map an unfamiliar repository into a modernization plan without inventing component boundaries.

## Read Order

1. Top-level manifests and lockfiles
2. Top-level `README*`, `CONTRIBUTING*`, `docs/`, and existing `AGENTS.md`
3. Existing component `AGENTS.md`
4. Build and test configuration for each detected ecosystem
5. Representative source, test, and documentation files inside each candidate component

## Root-Level Signals

Use top-level evidence to identify the repository profile:

- Build systems: `package.json`, `pnpm-workspace.yaml`, `pyproject.toml`, `setup.py`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle*`, `CMakeLists.txt`, `BUILD`, `WORKSPACE`, `meson.build`, `Makefile`
- Documentation: `README*`, `CONTRIBUTING*`, `docs/`, `AGENTS.md`
- Workspace boundaries: `apps/`, `packages/`, `services/`, `libs/`, `modules/`, `components/`, `tools/`

## Component Root Rules

Treat a directory as a component root when at least one of these is true:

1. It has its own build manifest.
2. It already has its own `AGENTS.md`.
3. It contains a repo-local skill directory such as `skills/` or legacy `SKILLS/`.
4. It is a clear app, library, package, service, tool, or module boundary.

Use supporting evidence before classifying rule 4:

- A component-local `README*`
- A `src/`, `lib/`, `include/`, `cmd/`, `app/`, or `tests/` subtree
- Meaningful source file density relative to sibling directories
- A directory name that clearly denotes a component boundary, such as `apps/foo`, `packages/bar`, or `services/baz`

Do not promote tiny leaf directories unless they carry one of the stronger signals above.

## Coverage Levels

- `exhaustive`: inspect all candidate component roots that meet the rules above
- `key-components`: keep the strongest component roots, always retaining any existing `AGENTS.md` or skill roots
- `root-only`: audit only the repo root and summarize component discovery at a high level

## Skill System Detection

Modern Codex skills:

- `skills/<skill-name>/SKILL.md`
- `skills/<skill-name>/agents/openai.yaml`
- component-local variants under `<component>/skills/`

Legacy repo-local skill systems often look like:

- uppercase `SKILLS/`
- slash-command markdown collections
- one markdown file per command under a shared directory
- `README.md` describing commands rather than `SKILL.md`

Treat legacy systems as migration sources, not garbage to remove by default.

## Evidence Discipline

For every significant conclusion, keep at least one concrete path:

- language detection: representative file paths
- build systems: manifest paths
- component roots: the specific manifest, `AGENTS.md`, skill dir, or boundary files
- doc quality: the paths of representative `AGENTS.md`
- legacy skill findings: the exact `SKILLS/` or markdown-command paths

If the evidence is weak, mark the conclusion as tentative in the audit output.
