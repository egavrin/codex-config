# Skill Migration Rubric

Use this rubric when deciding whether to keep, create, merge, migrate, or skip repo-local skills.

## Keep

Choose `keep` when a repo-local skill:

- already uses modern Codex structure
- is still accurate
- has a clear trigger and narrow scope
- provides repo-specific guidance that would be expensive to rediscover repeatedly

## Rewrite

Choose `rewrite` when a skill should continue to exist but needs one or more of:

- clearer trigger language
- lower-noise instructions
- updated commands or file paths
- separation of core workflow from detailed references
- conversion from ad hoc notes into `SKILL.md` plus bundled resources

## Create

Choose `create` when the workflow is:

- repo-specific
- repeated often enough to justify dedicated guidance
- fragile or multi-step enough that scripts, references, or templates help

Common candidates:

- repo-specific build or test workflows
- code generation or release procedures
- component exploration or debugging flows
- review or migration workflows tied to local architecture

## Migrate

Choose `migrate` when you find a legacy system such as uppercase `SKILLS/` or slash-command markdown collections.

Migration rules:

- create modern lowercase `skills/` targets
- preserve equivalent behavior and discovery cues
- update local documentation to point at the new location
- do not delete legacy sources unless the user explicitly requests cleanup

## Merge

Merge multiple skills when they are only superficially different and duplicate the same workflow. Prefer one stronger skill with clearer inputs over many tiny variants.

## Skip

Choose `skip` when the workflow is:

- generic enough that Codex does not need extra repo context
- too narrow or one-off to justify maintenance
- fully generated or vendor-owned
- already covered cleanly by a parent `AGENTS.md`
