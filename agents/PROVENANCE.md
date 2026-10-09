# Runpod skill provenance

These eight skills come from [runpod/runpod-plugins-official](https://github.com/runpod/runpod-plugins-official).
The installed source paths are `plugins/runpod/skills/SKILL-NAME/`.
The source metadata identifies Runpod as the author and Apache-2.0 as the license.
The original [Apache-2.0 license](LICENSE) covers the source materials.

The snapshot preserves the installed technical content and version metadata.
The prose uses the shared profile derived from ASD-STE100 Issue 9.
This update does not upgrade the Runpod skills or change their operational rules.
The installed source records identify folder hashes, not Git commit revisions.
Do not use these hashes as commit identifiers.

| Skill | Installed source folder hash |
| --- | --- |
| `companion-clis` | `9f25a6099e3937ebda70dc1ec82b52f4ea0935e1` |
| `flash` | `dc65a5c7b09dcf451ebd846ad82a48390cf5bfcd` |
| `runpod` | `a7f460b9282a063374e240ca736c3608991bbca3` |
| `runpod-mcp` | `3d05cdd35739bbe1c05cc5021f0536c7439ebbd1` |
| `runpod-migrate` | `f50aaab268f1b3a4637d87d9f369f8ebab45e48f` |
| `runpod-templates` | `f0ff7c25bfa359feb7b1141d3ad8800a0db4bff0` |
| `runpod-usage` | `d78a452e080d94547f14599626168babe323a350` |
| `runpodctl` | `5b8920d79b1dacefdbab67287c99d76baef973a5` |

The eight skills are companion-clis, flash, runpod, runpod-mcp, runpod-migrate, runpod-templates, runpod-usage, and runpodctl.
Their normal discovery root remains `~/.agents/skills`.
The snapshot uses `agents/skills/` to preserve that root.
Plugin caches and provider-managed skill directories are excluded.

Original license source: [upstream LICENSE](https://github.com/runpod/runpod-plugins-official/blob/main/LICENSE).
