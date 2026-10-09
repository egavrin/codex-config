# Create a pod and wait until it is actually usable

## Prompt

Spin me up an A40 pod from `runpod/pytorch:1.0.3-cu1281-torch291-ubuntu2404` and
tell me when I can ssh into it.

## Expected behavior

The agent should do these actions:

1. Create with `runpodctl pod create --image ... --gpu-id "NVIDIA A40" --wait`, which returns
   only once port 22 answers with an ssh banner.
2. Read the printed payload (the `pod get` shape, so it carries the live `ssh` block) and give
   the user the ssh command.
3. Do not write a custom poll loop around `pod get`/`ssh info`. Do not treat `desiredStatus: RUNNING` as "ready". That status also applies during the image download.
4. If the wait times out, state that the pod **exists and still causes charges**. Read its id from the error object's `id` field. Offer to delete it.

## Assertions

- Uses `--wait` (optionally with `--wait-timeout`) rather than a custom polling loop
- Does not claim the pod is ready based on `desiredStatus` alone. If it inspects status, it reads `runtimeStatus`
- Reports the ssh connection details from the waited-for output
- On `wait_timeout` / `wait_interrupted`, report the pod id from the error object. Propose cleanup instead of assuming no creation occurred.
