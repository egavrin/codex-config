# Handle a runpodctl failure without parsing message text

## Prompt

I'm scripting `runpodctl` in a loop. Write the failure handling: how do I tell a
missing endpoint from a bad API key from a blip I should retry? Here are two failures
I've seen:

```
{"error":"failed to get endpoint: endpoint not found","code":"not_found","status":404}
{"error":"failed to get template: template not found: tpl-abc","code":"not_found"}
```

## Expected behavior

The agent should do these actions:

1. Branch on `code`, not on `status` and not on substrings of `error`
2. Explain why the second failure has no `status`. GraphQL returns HTTP 200 and null data for a missing resource. Thus, `status === 404` misses it.
3. Retry `network_error`, `rate_limited` and `server_error` with backoff, and say why
   `cli_error` (for example a malformed `RUNPOD_API_URL`) must not be
4. Distinguish `no_credentials` (no key set → `RUNPOD_API_KEY` / `runpodctl doctor`) from
   `unauthorized` (key present but wrong/expired) — neither is a retry
5. Treat `not_found` as server-side, not as a mistyped local path
6. Use a non-zero exit code to detect failure. Read errors from **stderr** and data from stdout. Do not treat a `warning:`/`note:` line on stderr as a failure
7. Include a default branch for an unrecognized `code`, because the vocabulary is what the
   CLI generates rather than exhaustive (the API can pass its own code through lowercased)
8. Do not retry `timeout` / `wait_timeout` / `wait_interrupted` / `job_failed` (v2.9.0+). Each result means that work or a resource survived the CLI process. Another execution creates a **second** job or billed resource. Follow up instead — poll (`serverless status`, `pod get`)
   or clean up via the error object's `id`

## Assertions

- Switches/branches on `code`
- Does not branch on `status` alone or on `error` text matching
- Retry set includes `network_error` and at least one of `rate_limited`/`server_error`
- The produced handler has a default/else branch treating an unknown `code` as fatal
- Does not retry `cli_error`, `usage_error`, `not_found`, `no_credentials`, or
  `unauthorized`
- Does not retry `timeout`, `wait_timeout`, `wait_interrupted` or `job_failed`. Treats them
  as "poll or clean up", not as "run it again"
- Separates `no_credentials` from `unauthorized` in the auth handling
- Reads errors from stderr and does not expect error JSON on stdout
- Does not claim `status` is always present
- Does not tell the user to parse plaintext for `pod`/`serverless`/`template`/`model`
  commands (On v2.10.0+, only legacy `pod` paths and `project` still print plaintext. `exec` uses coded JSON and now exits non-zero. An assertion that lists `exec` as a plaintext surface is stale.)
- Pass only `json`/`yaml` to `--output`. On v2.10.0+, an unrecognized value causes `usage_error` with exit 1. On v2.9.0, it silently returned JSON.
