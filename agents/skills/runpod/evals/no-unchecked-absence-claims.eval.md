# Never assert a tool cannot do something without checking

## Prompt

I'm on runpodctl and I don't have the Runpod MCP connected. Can I read the logs of
the workers behind my serverless endpoint from the CLI, or do I need the MCP server
or the Console for that?

## Expected behavior

Per `runpod/SKILL.md` → *"These skills are a snapshot; the tools are the source of
truth"*:

1. **Answers yes, and names the command** — `runpodctl serverless logs <endpoint-id>`
   (v2.10.0+), optionally narrowed with `--worker`. Reaching for
   `runpodctl serverless --help` or `runpodctl version` to make sure that the local binary
   has it is *better*, not worse.
2. **Does not answer from a remembered limitation.** "The CLI has no worker-log
   command, use MCP or the Console" was true through v2.9.0 and is the exact answer
   this eval exists to catch. A model that has internalized the older documentation — or an
   older copy of this skill — will produce it confidently.
3. **If it hedges on version, it hedges with a floor, not a denial** — "needs
   runpodctl ≥ v2.10.0; check `runpodctl version`" is correct. "runpodctl cannot do
   this" is not.
4. If it mentions the pre-v2.10.0 fallbacks, it names them as fallbacks. These are the v2 REST SSE path, MCP `stream-worker-logs`, and the Console Workers tab.

Apply the same rule to other capabilities. A negative capability claim must name a version, identify an API, or give a "check it yourself" reference.

## Assertions

- Answers **yes** and names `runpodctl serverless logs`
- Does **not** claim runpodctl lacks a worker-log command
- Does **not** make MCP or the Console mandatory
- Any version caveat is expressed as a floor (`≥ v2.10.0` / `runpodctl version`), not
  as an absence
- Bonus, not required: tests against `runpodctl serverless --help` rather than
  asserting from the skill text alone
