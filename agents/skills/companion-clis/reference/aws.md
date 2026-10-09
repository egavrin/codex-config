# AWS CLI

The AWS CLI is used to access Runpod storage over the S3 protocol. Any Runpod product that can mount a Network Volume — pods, clusters, and serverless endpoints — can have its storage accessed this way. The bucket name is the network volume ID.

> **Not installed?** One-time install lives in [`aws-setup.md`](aws-setup.md) — skip if `aws --version` already works.

## Credentials

Runpod uses its own S3-compatible API, not AWS. Supply a Runpod user ID and S3 API key. An AWS account is unnecessary.

- **Access key** (`AWS_ACCESS_KEY_ID`): your Runpod user ID — found in the console under Settings > S3 API Keys, in the key description (format: `user_...`)
- **Secret key** (`AWS_SECRET_ACCESS_KEY`): an S3 API key — generate one at Settings > S3 API Keys > Create. Shown only once. Save it immediately (format: `rps_...`)

> **S3 API keys are Console-only.** Neither `runpodctl` nor REST/GraphQL can create an S3 API key or read the user ID.
> Both values come from the Console (Settings > S3 API Keys). An agent cannot obtain them automatically.
>
> The CLI can save the regular `RUNPOD_API_KEY`.
> The AWS access key must be the Runpod **user id** (`user_...`), not the `RUNPOD_API_KEY`.
>
> If S3-API access is necessary, first look for S3 credentials in `~/.aws/credentials` or environment variables.
> If absent, stop and ask the user to generate them in the Console.
>
> Do not try to generate them yourself.

```bash
# Option 1: interactive configure (writes ~/.aws/credentials and ~/.aws/config)
# When prompted: enter user ID as access key, S3 API key as secret.
# Press Enter to skip region and output format — region is always passed per-command, not stored in config.
aws configure

aws configure list    # verify stored credentials

# Option 2: environment variables (override config files)
export AWS_ACCESS_KEY_ID=user_...
export AWS_SECRET_ACCESS_KEY=rps_...

# To stop using env vars and fall back to config file:
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
```

## Region and Endpoint

The `--region` flag on every command is the Runpod datacenter ID where the network volume lives — not an AWS region. The `--endpoint-url` is derived from the same datacenter ID.

Supply both flags for every command. **`--region` takes the DC id as-is, but the
`--endpoint-url` host must be LOWERCASED** — `s3api-eu-ro-1…`, not `s3api-EU-RO-1…`
(an upper-cased host fails to resolve):
```
--region <DC> --endpoint-url https://s3api-<dc-lowercased>.runpod.io/
# DC EU-RO-1  →  --region EU-RO-1  --endpoint-url https://s3api-eu-ro-1.runpod.io/
```

**Tip:** Each network volume on the storage page at https://console.runpod.io/user/storage/ shows a pre-filled example `aws s3 ls` command with the correct `--region` and `--endpoint-url` already substituted. Use this to make sure that the values for a given volume are exact.

Datacenter IDs are **region-prefixed**. They go verbatim into `--region <DC>` but must be
**lowercased** in the host `https://s3api-<dc-lowercased>.runpod.io/`. `runpodctl datacenter
list` is authoritative — the set grows over time. Run it for the current list. Common ones:

| Region | Datacenter IDs |
|--------|---------------|
| EU | EU-CZ-1, EU-RO-1, EU-NL-1, EU-FR-1, EUR-IS-1, EUR-NO-1 |
| US | US-CA-2, US-GA-1, US-GA-2, US-IL-1, US-KS-2, US-MD-1, US-MO-1, US-NC-1, US-TX-1, US-WA-1 |
| Other | CA-MTL-1, AP-JP-1, AP-IN-1, SEA-SG-1, OC-AU-1 |

## Key Commands

Replace `DATACENTER` in `--region` with the network volume's datacenter ID unchanged (for example `US-CA-2`). Replace `<dc-lowercased>` in the host with that same ID in lowercase (`us-ca-2`). Replace `NETWORK_VOLUME_ID` with the volume ID, which is the S3 bucket name.

```bash
# List files in a volume
aws s3 ls \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  s3://NETWORK_VOLUME_ID/

# List a subdirectory
aws s3 ls \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  s3://NETWORK_VOLUME_ID/my-folder/

# Upload a file
aws s3 cp local-file.txt \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  s3://NETWORK_VOLUME_ID/

# Download a file
aws s3 cp \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  s3://NETWORK_VOLUME_ID/remote-file.txt ./

# Delete a file
aws s3 rm \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  s3://NETWORK_VOLUME_ID/remote-file.txt

# Sync a local directory to a volume
aws s3 sync local-dir/ \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  s3://NETWORK_VOLUME_ID/remote-dir/
```

Path mapping: `/workspace/my-folder/file.txt` on a pod = `s3://NETWORK_VOLUME_ID/my-folder/file.txt` via S3.

## Troubleshooting

```bash
# Retry on timeout (large transfers)
export AWS_RETRY_MODE=standard
export AWS_MAX_ATTEMPTS=10

# Extend read timeout for large files (seconds)
aws s3 cp large-file.zip \
  --region DATACENTER \
  --endpoint-url https://s3api-<dc-lowercased>.runpod.io/ \
  --cli-read-timeout 7200 \
  s3://NETWORK_VOLUME_ID/
```

## Optional: resumable volume transfers (community tool)

`aws s3 sync` suits modest directory trees. Its resume support is weak, and performance deteriorates beyond approximately 10,000 files. This affects large model weights and copies across volumes (see [10 — multi-region HA serverless](../../runpod/golden-paths/10-multi-region-ha-serverless.md)).
For those transfers, the community **Runpod Network Volume Storage Tool** adds resumable multipart uploads to the same S3 API. It supports automatic chunk sizes and MD5-verified resume. It also supplies directory synchronization with exclusions, an interactive file browser, a Python SDK, and a REST server.

It is referenced in the official documentation under
[community solutions](https://docs.runpod.io/community-solutions/runpod-network-volume-storage-tool).

```bash
git clone https://github.com/justinwlin/Runpod-Network-Volume-Storage-Tool.git
cd Runpod-Network-Volume-Storage-Tool && uv sync

# Same S3 credentials as the AWS CLI above (access key = user id, secret = rps_... key)
export RUNPOD_API_KEY=...
export RUNPOD_S3_ACCESS_KEY=user_...
export RUNPOD_S3_SECRET_KEY=rps_...

uv run runpod-storage upload ./model-artifacts <volume-id>   # resumable — re-run to resume
uv run runpod-storage list-volumes
```

Plain `aws s3` (above) stays the zero-dependency baseline. Reach for this tool when
resume/large-tree reliability matters.
