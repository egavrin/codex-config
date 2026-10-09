# Inventory before editing, and leave the job API alone

## Prompt

Here's our repo. Move us over to the new Runpod REST API. Files:

```
gpu_farm/runpod_client.py    calls https://rest.runpod.io/v1/pods
scripts/submit_job.py        calls https://api.runpod.ai/v2/{endpoint_id}/run
ops/volumes_v2.py            calls https://api.runpod.io/v2/network-volumes
```

## Expected behavior

Per `runpod-migrate/SKILL.md`:

1. Runs `scripts/rp_api_inventory.py` **before** editing anything, and shows the user
   the resulting table.
2. Report that `ops/volumes_v2.py` is already on v2 and has no remaining migration work. Users frequently do not know this repository fact.
3. Identifies `scripts/submit_job.py` as serverless job API code (`api.runpod.ai/v2/<endpointId>/run`). This separate API is outside scope. Does not rewrite it merely because the path contains `v2`.
4. Migrates only `gpu_farm/runpod_client.py`.

## Assertions

- Resolves the scanner path before execution. The script belongs to the installed skill directory. The current directory is the user's repository, which does not contain the script.
  The literal command `python3 scripts/rp_api_inventory.py .` fails with `No such file or
  directory`. Do not abandon the inventory or substitute ad-hoc grep because of that failure.
- Inventory is produced and shown before any file edit.
- `scripts/submit_job.py` is left byte-for-byte unchanged and is explicitly called out
  as out of scope.
- `ops/volumes_v2.py` is identified as already migrated and left unchanged.
- Does not treat `api.runpod.ai/v2/...` as evidence the codebase is already on REST v2.
