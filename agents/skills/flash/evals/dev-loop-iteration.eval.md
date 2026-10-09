# Iterate on a flash GPU handler against a live remote worker

> **LIVE eval.** This runs against real Runpod infrastructure — it provisions a real
> worker and incurs cost. It is graded on what actually happened at runtime, not on what
> the agent says it would do.

## Setup

- Use `RUNPOD_API_KEY` from the environment (flash CLI authenticated, v1.17.0+).
- Copy the fixture to a scratch dir so the graded fix does not mutate the committed
  fixture: `cp -r flash/evals/fixtures/dev-loop /tmp/dev-loop-eval && cd /tmp/dev-loop-eval`
  (or `git checkout flash/evals/fixtures/dev-loop` afterward).
- The fixture's `/predict` handler refers to module-level constant `VOL`. Flash does not send that constant to the remote worker. The handler fails at runtime until the constant moves inside the function body.

## Prompt

Use the runpod-flash project in this directory (an image-to-3D style endpoint). The
`/predict` route fails when it actually runs on a worker. Iterate against a **real** remote
worker: start the dev loop, send a request, read the worker's logs, fix whatever is broken,
and confirm a successful JSON response. I don't want to re-deploy on every change.

## Expected behavior

The agent should actually execute (not merely describe) the following:

1. Recommend and use `flash dev` (not repeated `flash deploy`) for the loop. Run it as a background process so it does not block the session.
2. Determine the dev server's **actual** URL from its startup log rather than assuming
   `localhost:8888` (flash bumps the port if 8888 is taken).
3. Send a real request to the correct **file-namespaced** route (`main.py` → `/main/predict`),
   which provisions and dispatches to the remote worker.
4. Read the captured dev-server log to observe the **real** error from the worker.
5. Diagnose it: only the function body ships, so module-level `VOL` is undefined remotely.
   Fix by moving `VOL` inside the handler and rely on hot-reload (no redeploy).
6. Send the request again and make sure that a real successful response arrives.
7. Undeploy the endpoint it provisioned (`dev-loop-eval`), scoped by name — not the whole
   account.

## Assertions

- Runs `flash dev` as a background / non-blocking process (does not run it as a plain
  blocking command and hang)
- Determines the actual host:port from the dev-server output (does not hardcode `8888` when
  it was bumped)
- Sends the request to the file-namespaced route (`/main/predict`), not the bare `/predict`
- Observes the **verbatim** runtime error `NameError: name 'VOL' is not defined` in the
  worker's streamed logs (it is reported from the live run, not guessed)
- Fixes the bug by moving `VOL` into the function body and re-tests via hot-reload, without
  running `flash deploy`
- Obtains a real **HTTP 200** whose body contains `"ok": true` (for example
  `{"ok":true,"vol":"/runpod-volume/models","echo":...}`)
- Run `flash undeploy dev-loop-eval --force` only for the endpoint created in this task. Do not use `flash undeploy --all`, which deletes unrelated account endpoints. Make sure that the `dev-loop-eval` endpoint is absent.

## Cleanup

- `flash undeploy dev-loop-eval --force` must report the `dev-loop-eval` endpoint deleted,
  and `flash undeploy list` must no longer list it. Do not use `flash undeploy --all` here —
  it would delete endpoints this eval did not create.
- The agent must only stop processes/ports it started.
- Restore the fixture if it was edited in place: `git checkout flash/evals/fixtures/dev-loop`.
