# Skill Mechanics for Codex

Read this reference when writing or revising a skill. The shared writing criteria
are in [SKILL.md](SKILL.md); the bundled `skill-creator` is authoritative for
current packaging, metadata, and validation requirements.

## Discovery and invocation

A skill is a directory containing `SKILL.md` with YAML `name` and `description`.
Use the description to explain the capability and when it applies. The host
initially exposes discovery metadata and loads the full instructions when the
skill is selected; linked references can be read as needed.

Codex supports explicit invocation with `$skill-name` and automatic selection
when the request matches the skill's description. Optional UI and invocation
settings belong in `agents/openai.yaml`:

```yaml
interface:
  display_name: "Example Skill"
  short_description: "A focused summary of the skill's capability"
  default_prompt: "Use $example-skill to complete the requested workflow."
policy:
  allow_implicit_invocation: true
```

Keep automatic selection enabled for a new skill unless the user requests
explicit-only invocation. Preserve an existing skill's invocation policy unless
the user asks to change it. For explicit-only invocation, set
`policy.allow_implicit_invocation: false`; keep the required `name` and
`description` in `SKILL.md`. Do not use provider-specific frontmatter switches.

Invocation policy is about skill selection, not permission to mutate files,
authorization for external actions, or whether linked reference files can be
read. Do not promise zero context cost: discovery details and context budgets
depend on the host. An explicit-only skill may still have a human-facing summary.

## Shared reference and splitting

Keep shared reference in one place and give callers an explicit link with a
reading condition. A plain linked file can serve several workflows without
requiring another independently discoverable skill. Explicit-only invocation
does not prohibit reading that file when the current task requires it.

Create a separate skill when it has a distinct useful capability and a meaningful
independent trigger. Otherwise use a reference inside the current skill.
Keep common requirements in the entrypoint and read specialized material only
for its relevant branch.

A router is useful only when selecting among several real workflows is itself a
repeated task. It may describe the choices and link to their instructions, but
does not automatically invoke tools, bypass invocation policy, grant permission,
or create subagents. Avoid adding a router solely because multiple files exist.

## Validate

Use `skill-creator`'s `quick_validate.py` on the skill directory. Check that
local links resolve, metadata matches the skill, and a default prompt names the
correct `$skill-name`. Structural validation does not establish correct behavior;
review realistic trigger and completion scenarios when warranted.
