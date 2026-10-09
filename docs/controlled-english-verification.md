# Controlled English migration evidence

This report records the migration on 2026-10-09.
It distinguishes structural tests, language examination, and requirement preservation.
These checks do not establish ASD-STE100 compliance or general model reliability.
They do not establish token savings.

## Reference and scope

The baseline is ASD-STE100 Issue 9, dated 15 January 2025.
The [rule map](../codex/skills/writing-for-agents/references/ste-rule-map.md) records all 53 writing rules.
Each rule has a status, scope, exception, and reason.
The map records the official PDF source and its SHA-256.
The PDF and dictionary remain private and are absent from this repository.

The [profile](../codex/skills/writing-for-agents/references/controlled-english.md) contains original explanations and software examples.
The [term list](../codex/skills/writing-for-agents/references/software-terms.md) defines software vocabulary and its permitted parts of speech.
The profile defines requirement strength and source status labels as agent extensions.
It preserves exact text and explicit requests for another language.
It grants no permission, scope, tool, or delegation.

| Discovery root | Revised skills |
| --- | --- |
| `~/.codex/skills` | claude-collab, code-simplifier, codebase-design, film-studio-workflow, gh-address-comments, gh-fix-ci, hatch-pet, improve-codebase-architecture, repo-modernizer, writing-for-agents |
| `~/.agents/skills` | companion-clis, flash, runpod, runpod-mcp, runpod-migrate, runpod-templates, runpod-usage, runpodctl |

The migration also covers global Codex instructions, 17 native agent prompts, and the main configuration instruction body.
Personal Claude instructions import the same profile and term list.
The live Film Studio skill remains a symlink to its source repository.
This repository contains a resolved snapshot of that skill.
No Film Studio commit or push occurred.

## Structural tests

The bundled `quick_validate.py` passed for all 18 installed skills.
Existing YAML metadata and TOML configurations parsed successfully.
Local Markdown references resolved.
Names, invocation policy, default prompts, shared links, and licenses were examined.
An absent optional `agents/openai.yaml` is not a validation failure.

The bridge suite passed 65 workflow cases.
Six policy cases cover selected skills, no selected skill, missing material, and the complete packet size boundary.
Missing policy material stops the helper before a model request.
The 256 KiB limit includes the profile, rule map, and term list.
The input packet schema remains unchanged.

The tested helper SHA-256 is:

```text
094b531be6a82b0da3b662ab8e228c3aa92d13e843817f5bd27fd6e91e11f154
```

The existing cases cover authentication, limits, progress, inactivity, patch conflicts, stale sources, and permitted paths.
Authentication, tool isolation, progress supervision, and patch acceptance remain unchanged.

To repeat the bridge tests from the snapshot, run:

```sh
python3 codex/skills/claude-collab/scripts/test_bridge.py
```

To validate a restored skill, run the bundled validator against its directory:

```sh
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/writing-for-agents
```

Repeat that command for each skill in the inventory.
The validator examines structure, not language correctness or model behavior.

## Language examination

The examination separated instructions from descriptions.
The limits are 20 words for instructions and 25 words for descriptions.
Parentheses, quoted text, identifiers, and list items follow the documented counting rules.
Word counts are a screening aid, not evidence of dictionary compliance.
The final sentence examination covered prose, table cells, metadata, instruction bodies, and parenthetical text.
It retained 199 descriptive candidates with 21–25 words.
One fixed UI label precedes a compliant instruction.
One exact diagram retains its nine workflow stages.
Four retained semicolons occur in fixed labels or quotations.
Markdown table checks also account for escaped pipe characters.

Disputed general verbs were examined in the private dictionary reference.
Examples include check, permit, require, verify, need, confirm, allow, establish, and detect.
Revisions use approved alternatives where the original software meaning permits them.
Technical validation remains a defined software operation.
An unknown general word cannot become a technical term merely because an agent uses it.

Exact evaluation prompts remain test inputs.
Their surrounding instructions, expected results, and assertions use the profile.
Code, commands, URLs, identifiers, licenses, quotations, and required product text retain their exact content.
Template placeholders and compact labels retain their existing contracts.

## Requirement preservation

Before revision, private records captured all 177 original documents and their material requirements.
These records include scope, triggers, permissions, exceptions, verification, technical facts, and attribution.
Comparisons examined code blocks, inline literals, URLs, numeric facts, configurations, licenses, and links.
Meaning also received contextual examination.
Literal preservation alone cannot establish semantic equivalence.

All 17 agent configuration fields outside descriptions and instruction text remained unchanged.
Nine experimental configurations remained unchanged.
Existing bundled licenses remained unchanged.
The eight Runpod snapshots include the original Apache-2.0 license and source attribution.

The acceptance repair restored the explicit assertion that `pools` is a list.
It also replaced a general use of confirm with an approved formulation.
Final integration restored eight source quotations and corrected two grammatical formulations.
Those corrections preserve the operating requirements.

Two pre-existing source conflicts remain visible:

- `runpod-usage/reference/gotchas.md` says that runpodctl has no worker-log command.
  Other retained v2.10.0 material describes serverless logs.
- `runpodctl/reference/model-caching.md` states 17 of 33 data centers but lists 16 IDs.

The language migration preserves both source claims.
A technical correction requires separate evidence and scope.

## Fresh-session checks

A fresh Codex session loaded global instructions and read the shared profile.
It reported Issue 9, the English default, sentence limits, and requirement strength.
It recognized that the profile grants no new permission.
The session used read-only mode and changed no files.
A final fresh session repeated the loading check after the sentence revision.
It passed with the same source, limits, requirement meanings, and scope boundaries.

An initial Claude test excluded user settings and did not load personal instructions.
That test failed the loading criterion.
The corrected test enabled user instruction discovery while disabling custom hooks, plugins, and MCP.
It loaded `~/.claude/CLAUDE.md` and both imported references.
Its initialization event listed the four shared writing and architecture skills.
The reported model was `claude-opus-5-5`, requested through `opus` with High effort.

Seven simulated cases covered skill creation, AGENTS.md review, guide reduction, reference extraction, assignment, findings, and Plan Mode.
The cases retained scope and exposed assumptions and unresolved decisions.
The final ordinary session repeated these checks after the sentence revision.
It loaded the updated definition of root and retained the same permission boundaries.
The ordinary session did not load the skill-format reference automatically.
It reported that gap instead of inventing the format authority.
These simulations do not prove reliable behavior on arbitrary tasks.

A separate companion review used no selected skill.
It received all three communication documents and reported their exact hashes.
It reported Issue 9 and the three rule statuses.
The complete packet contained 29,648 bytes.
The request finished successfully in 62.089 seconds with an empty diff.
The reported model was `claude-opus-5-5`, requested with High effort.
It preserved the guide requirements and identified assumptions and missing dictionary material.
No patch was applied.

Private test artifacts retain commands, inputs, hashes, expected results, and observed results.
Provider event streams, authentication metadata, packets, and task history are excluded from this public snapshot.
