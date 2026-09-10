# AGENTS Canonical Spec

Use this schema when rewriting or creating `AGENTS.md`. Adapt the wording to the repository, but keep the section order stable unless the repo has a strong existing convention worth preserving.

## Root `AGENTS.md`

Required sections:

1. Repository identity
   - name
   - purpose
   - primary languages or platforms
2. Repository layout
   - major top-level directories or workspaces
   - how the main components fit together
3. Build, test, and run entry points
   - canonical commands
   - important prerequisites or toolchains
4. Architecture and workflows
   - key data flow or subsystem relationships
   - generated code or codegen workflow
   - deployment, release, or CI notes if they materially affect local work
5. Conventions and pitfalls
   - code style or formatting expectations
   - generated-file rules
   - areas that should not be edited directly
   - repo-specific traps and debugging shortcuts
6. Local skills
   - shared repo-root skills
   - when to use them

## Component `AGENTS.md`

Required sections:

1. Component purpose and scope
2. Important directories, entry points, or public interfaces
3. Build/test/run commands relevant to the component
4. Architecture and workflows inside the component
5. Generated files, conventions, and local pitfalls
6. Local component skills and when to use them

## Writing Rules

- Prefer factual, repo-specific guidance over generic advice.
- Keep command examples copy-pastable.
- Use references to parent `AGENTS.md` only for shared rules that truly apply unchanged.
- Preserve substantive facts from existing docs even when rewriting the layout.
- Do not claim coverage for workflows you did not verify from source artifacts.

## Rewrite Guidance

- If the existing file already has strong repo facts but weak structure, rewrite in place.
- If the file is very small and redundant with the parent, consider skipping the child file and documenting the area in the parent instead.
- If the repo has many components, keep each component file scoped to the local area rather than re-explaining the whole repository.
