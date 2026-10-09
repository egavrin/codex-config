# Skill Mechanics for Codex

Read this reference when you write or revise a skill.
Read [SKILL.md](SKILL.md) for the shared criteria for instructions.
The bundled `skill-creator` defines current packaging, metadata, and validation requirements.

## Discovery and invocation

A skill is a directory with a `SKILL.md` file that contains YAML `name` and `description` fields.
Use the description to state the capability and its trigger conditions.
The host first exposes discovery metadata. When it selects the skill, it loads the complete instructions.
The agent can read linked references when necessary.

Codex supports explicit invocation with `$skill-name`.
It also selects a skill automatically when a request matches the description.
Put optional UI and invocation settings in `agents/openai.yaml`:

```yaml
interface:
  display_name: "Example Skill"
  short_description: "A focused summary of the skill's capability"
  default_prompt: "Use $example-skill to complete the requested workflow."
policy:
  allow_implicit_invocation: true
```

For a new skill, keep automatic selection enabled unless the user requests explicit-only invocation.
Preserve an existing skill's invocation policy unless the user asks to change it.
For explicit-only invocation, set `policy.allow_implicit_invocation: false`.
Keep the required `name` and `description` in `SKILL.md`.
Do not use provider-specific frontmatter switches.

The invocation policy controls skill selection. It gives no permission for file writes or external actions.
It does not control permission to read linked reference files.
Do not promise zero context cost. Discovery details and context budgets depend on the host.
An explicit-only skill may still have a summary for humans.

## Shared references and document divisions

Keep each shared reference in one location.
Give callers an explicit link and a condition that tells them when to read it.
One linked file can serve several workflows without a separate discoverable skill.
Explicit-only invocation does not prohibit access to that file when it is necessary for the current task.

Create a separate skill when it has a distinct useful capability and a meaningful independent trigger.
Otherwise, use a reference inside the current skill.
Keep common requirements in the entry document.
Read specialized material only for the applicable branch.

A router is useful only when selection among several real workflows is itself a repeated task.
It may describe the choices and link to their instructions.
It does not automatically invoke tools, bypass invocation policy, grant permission, or create subagents.
Do not add a router merely because several files exist.

## Validate

Run `skill-creator`'s `quick_validate.py` on the skill directory.
Make sure that local links resolve. Make sure that metadata matches the skill.
Make sure that the default prompt names the correct `$skill-name`.
Structural validation does not prove correct behavior.
When necessary, review realistic trigger and completion cases.
