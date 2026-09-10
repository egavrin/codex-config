---
name: repo-modernizer
description: Audit and modernize repository guidance for AI agents, including root and component AGENTS.md files, contributor-facing agent docs, repo-local Codex skills, and legacy SKILLS systems. Use when Codex is asked to study a repository from its root, inventory existing guidance, standardize or rewrite AGENTS.md coverage, propose repo or component skills, or migrate older skill layouts to modern Codex-compatible structures.
---

# Repo Modernizer

Inspect a repository from its root, build an evidence-backed map of the repo and its components, then either return a structured modernization plan or apply the approved rewrite.

Default mode is `audit`. Only enter `apply` mode when the user explicitly asks to create or rewrite files after reviewing the plan.

## Inputs

- `root`: repository root to inspect. Default to the current working directory.
- `mode`: `audit` or `apply`. Default to `audit`.
- `coverage`: `exhaustive`, `key-components`, or `root-only`. Default to `exhaustive`.

## Audit Workflow

1. Inventory the repository.
   - Run:
     - `python "<path-to-skill>/scripts/inventory_repo.py" --root "." --coverage exhaustive --format json`
   - Use `key-components` or `root-only` only if the user requests a narrower pass.
2. Ground the plan in real artifacts before writing recommendations.
   - Read the top-level manifests and docs identified by the inventory.
   - Read existing `AGENTS.md` files at the root and in representative components.
   - Read build or test configuration files for the major detected ecosystems.
   - Read representative source files and, when present, component-local `README*`, `docs/`, or `tests/`.
3. Classify component roots.
   - Treat a directory as a component root when it has its own build manifest, existing `AGENTS.md`, legacy skill directory, or a clear app/library/package boundary.
   - Leave small leaf directories without those signals documented under the nearest stronger parent.
   - Use [references/discovery-heuristics.md](references/discovery-heuristics.md) when the boundary is unclear.
4. Inventory current agent guidance and skills.
   - Record root and component `AGENTS.md` coverage.
   - Distinguish modern Codex skills from legacy repo-local skill systems such as uppercase `SKILLS/` directories or slash-command markdown collections.
   - Preserve repo facts even when planning a canonical rewrite.
5. Produce the audit response in this shape:
   - `Repo profile`
   - `Component inventory`
   - `Current documentation and skill inventory`
   - `Action matrix` with one action per relevant path: `keep`, `rewrite`, `create`, `migrate`, or `skip`
   - `Proposed repo-local skills`
   - `Risks and open questions`
6. Use canonical rewrite as the default recommendation style.
   - Normalize structure and naming.
   - Keep substantive repository knowledge discovered from the source tree.
   - Do not recommend deleting legacy `SKILLS/` directories unless the user asks for cleanup.

## Apply Workflow

Use `apply` mode only after the user approves the modernization direction.

1. Re-run the inventory and re-read the decisive source artifacts so the edits reflect current repo state.
2. Rewrite or create canonical `AGENTS.md` files using:
   - [references/agents-canonical-spec.md](references/agents-canonical-spec.md)
   - [assets/root-agents-template.md](assets/root-agents-template.md)
   - [assets/component-agents-template.md](assets/component-agents-template.md)
3. Create repo-local skills only when the workflow is repo-specific and repeated or fragile enough to justify dedicated instructions, scripts, references, or assets.
   - Use [references/skill-migration-rubric.md](references/skill-migration-rubric.md).
   - Use [assets/skill-template/SKILL.md](assets/skill-template/SKILL.md) and [assets/skill-template/agents/openai.yaml](assets/skill-template/agents/openai.yaml) as scaffolding.
4. Use the hybrid skill layout.
   - Shared workflows go in repo-root `skills/`.
   - Highly specialized workflows go in `<component>/skills/`.
   - Treat uppercase `SKILLS/` directories as migration sources.
   - Update references to point at lowercase `skills/`, but do not delete legacy directories unless the user explicitly asks.
5. Summarize what changed, which paths were rewritten or created, what was intentionally preserved, and what still needs manual review.

## Decision Rules

### Action Matrix

- `keep`: existing doc or skill already matches the repo reality and only needs minor follow-up outside this pass.
- `rewrite`: existing path should stay, but its structure or content should be standardized.
- `create`: missing but warranted by component importance or workflow repetition.
- `migrate`: legacy skill or agent-doc system should be replaced or mirrored in modern Codex form.
- `skip`: low-value leaf path, generated area, vendor code, or content better covered by a parent document.

### Repo-Local Skill Threshold

Create a repo-local skill only if all of these are true:

- The workflow is materially repo-specific.
- The workflow is likely to recur.
- The workflow is fragile, multi-step, or benefits from reusable scripts, references, or templates.

Do not create skills for generic workflows that Codex already handles well without extra context.

## Canonical Output Standards

- Root and component `AGENTS.md` files should follow the canonical schema from [references/agents-canonical-spec.md](references/agents-canonical-spec.md).
- Cite concrete evidence paths when recommending structural changes.
- Keep the audit response in chat by default; do not create a repo-local report file unless the user asks.
- Prefer lowercase `skills/` for new Codex-compatible skill directories.
- When migrating legacy skills, preserve behavior and discoverability before optimizing layout.

## Bundled Resources

### `scripts/inventory_repo.py`

Repository discovery helper that inventories:

- languages and build systems
- component roots and supporting signals
- existing `AGENTS.md` coverage
- modern and legacy skill directories
- evidence paths used for each conclusion

Usage:

- `python "<path-to-skill>/scripts/inventory_repo.py" --root "." --coverage exhaustive --format json`
- `python "<path-to-skill>/scripts/inventory_repo.py" --root "." --coverage key-components --format markdown`

### `references/`

- `discovery-heuristics.md`: component boundary and ecosystem detection rules
- `agents-canonical-spec.md`: exact schema for root and component `AGENTS.md`
- `skill-migration-rubric.md`: keep/create/merge/migrate/skip rules for skills

### `assets/`

- `root-agents-template.md`: root-level canonical `AGENTS.md` scaffold
- `component-agents-template.md`: component-level canonical `AGENTS.md` scaffold
- `skill-template/`: modern repo-local Codex skill scaffold
