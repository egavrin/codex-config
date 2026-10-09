# Access, assignments, and transfers

## Current deployment

- Website: `https://film-studio.46.101.247.248.sslip.io/`. The root opens «Проекты».
  A film opens at `/projects/<project_id>`.
- «Сожжение Хром»: ID `21f3e1ad79204157ada7924cdbec3dd1`.
- Private text history: `https://github.com/egavrin/film-studio-projects`, directory `projects/burning-chrome`.
  Media stays on the server Volume.
- SSH: `46.101.247.248`, port `443`. Verified server ED25519 fingerprint:
  `SHA256:rachWQ04QQfYWUNna/RDbl7niXRVtlUN+hB0c1ELlC4`.
- Operators: `studio`, `film-h3`. Generator roles: `film-images`, `film-writer`.
  Use only your assigned role and this machine's separate key.

These addresses identify the current server. They are not universal defaults.
If the operator supplies another endpoint/ID, make sure that the project identity is correct before use.
Caddy protects HTTPS with shared HTTP Basic Authentication. The operator supplies the password separately.
Do not add a Studio login/token.

Keep credentials out of URLs, task manifests, reports, and repositories.

## Viewer HTTP interface

Selected film base path: `/api/v1/projects/<project_id>`.

| Operation                                    | Interface                                                    |
| -------------------------------------------- | ------------------------------------------------------------ |
| Find films                                   | `GET /api/v1/projects`                                       |
| Read revision and structure                  | `GET <base>/context`                                         |
| List documents or read one complete document | `GET <base>/documents`, `GET <base>/documents/<id>`          |
| Read universe and history                    | `GET <base>/universe`, `GET <base>/universe/history`         |
| Read materials and versions                  | `GET <base>/artifacts`, `GET <base>/artifacts/<id>/versions` |
| Read job progress                            | `GET <base>/jobs`                                            |
| Read comments                                | `GET <base>/comments`                                        |
| Read material bytes                          | `GET <base>/media/<sha256>`. HTTP Range is supported.        |
| Save a permitted edit                        | `POST <base>/commands`                                       |

Lists use pagination. Use `limit`, `offset`, `next_offset`, and the returned `checkpoint`.
After 409, start the list read again.
A job summary contains progress, not the complete external task specification.

A command has `type`, `expected_revision`, `idempotency_key`, and `payload`.
In the viewer, `comment`, `workspace_save`, `universe_save`, and human `record_media_review` are permitted.
Limited `create_document`, `propose_revision`, and `apply_revision` are also permitted for the typed library and scene relations (below).
This route prohibits generation, creative task claim/submit, or arbitrary screenplay edits.
For those operations, the operator uses the public CLI.
The `local view` mode is read-only.

The following example adds an ordinary comment to the source document.
Supply the revision that you **read** and your stable key:

```json
{
  "type": "comment",
  "expected_revision": 2,
  "idempotency_key": "review-source-unique-key",
  "payload": { "entity": "source", "text": "Уточнить замысел адаптации." }
}
```

The remote `StudioClient` and CLI use only Hub reads.
`status` returns limited context. Read documents, jobs, events, tasks, and materials separately.
`events` uses `after`/`next_after`. Other lists have their own pagination.
For production writes, explicitly use SSH and `local command`.

The client does not select SSH automatically or retry a submission with an unknown result.

## Public operator CLI

Server application: `/opt/film-studio/current`. Node: `/opt/film-node/bin/node`.
Use the assigned `PROJECT_DIRECTORY`, `STUDIO_CONFIG=/etc/film-studio/config.json`, and correct access role.
Current directory for «Сожжения Хром»:
`/srv/film-studio/production/burning-chrome-20261005/sqlite-project-v2`.

Since 8 October 2026, `film-h3` has full operator `sudo` without a password.
It belongs to `filmstudio` and has read/write ACL access to production and catalog.
`film-images` and `film-writer` remain restricted generator roles.
After group changes, connect through SSH again.
The H3 key and connection address have not changed.

Examine permission with `sudo -n id`. The result must contain `uid=0`.
Run project commands as owner `filmstudio` so the service can access new files.
Change accepted state only through Core:

```sh
cd /opt/film-studio/current
sudo -n -u filmstudio env STUDIO_CONFIG=/etc/film-studio/config.json /opt/film-node/bin/node dist/cli.js local context /srv/film-studio/production/burning-chrome-20261005/sqlite-project-v2
```

From the application directory, use these public operations:

```sh
node dist/cli.js local context PROJECT_DIRECTORY
node dist/cli.js local document PROJECT_DIRECTORY DOCUMENT_ID
node dist/cli.js local jobs PROJECT_DIRECTORY
node dist/cli.js local tasks PROJECT_DIRECTORY JOB_ID
node dist/cli.js local task PROJECT_DIRECTORY JOB_ID TASK_ID
node dist/cli.js local skills
node dist/cli.js local command PROJECT_DIRECTORY COMMAND.json
```

Read text-history status through `GET <base>/text-git`:
`synced`, `pending`, `blocked`, or `disabled`.
`pending` means that the system saved the change and awaits a push.
For `blocked`, the operator examines access, settings, or external repository changes.
For an explicit check and another push, use:

```sh
node dist/cli.js local text-git-status PROJECT_DIRECTORY
node dist/cli.js local text-git-sync PROJECT_DIRECTORY
```

These operations do not apply GitHub edits to Studio.
Automatic pushes operate in the configured `local hub`.

For an existing external creative assignment, the operator uses `external-prepare`/`external-advance` with `{job, expected_revision, idempotency_key}`.
Send `claim_task`, `checkpoint_task`, and `submit_task` through `local command`.
Include `job`, `task`, stable `client`, and the applicable `text` or string `result`.
Claim the task before checkpoint/submit.
The canonical workflow examines returned raw results. Submission does not mean document acceptance.

Apply new screenplay edits through `propose_revision`/`apply_revision`.
Do not edit SQLite or accepted JSON directly.

## Generator: files through SSH

Example for the H3 machine with its existing private key (now with operator access):

```sh
ssh -p 443 -i ~/.ssh/id_ed25519 film-h3@46.101.247.248
scp -P 443 -i ~/.ssh/id_ed25519 -r film-h3@46.101.247.248:/srv/film-studio/packages/ASSIGNED_PACKAGE ./
scp -P 443 -i ~/.ssh/id_ed25519 result.mp4 film-h3@46.101.247.248:/srv/film-studio/incoming/film-h3/JOB_ID/result.mp4.partial
```

Create a separate task directory in your incoming area.
After transfer, compare SHA-256 at both ends. Rename `.partial` to the final name.
Transfer the manifest last.
The operator does not import `.partial` files, files without a manifest, or files with a different hash.
For large packages, use a resumable directory transfer.

Do not put the complete production into memory.

Report the project/job/package ID, incoming directory path, tool/model version, exact hashes, and original receipt to the operator.
H3 must preserve the relation to the original package and graph.
If source files or AV latent are necessary for the package, transfer them separately.
One MP4 does not satisfy the complete result contract.
Return images and draft speech in the same way, with their own manifests.
The operator selects the applicable public import:

```sh
node dist/cli.js local import-image PROJECT_DIRECTORY ORIGIN.json IMAGE
node dist/cli.js local import-draft-speech PROJECT_DIRECTORY ORIGIN.json AUDIO
node dist/cli.js local h3-result-import PROJECT_DIRECTORY RESULT.json
```

Get origin and result schemas from the assigned workflow and current contracts.
Do not infer them from the command name.
An import with the previous key returns the receipt without a second result.
An uploaded file remains a candidate until the required review.
Upload and import do not approve a gate.

## Typed library and exact inputs

In the same HTTP base, use `GET <base>/structure?kind=prop` and `GET <base>/entities/prop/<id>?part=cards|usages|history|assets`.
Use one part value.
Pages have checkpoint/next_offset.
Usages returns `usage_contexts` with canonical scene/episode/shot links to the place of use.
For scene/shot, `part=states` shows only saved incoming/outgoing and opening/closing states.

Commands retain the shared expected_revision/idempotency_key envelope:

- `create_document`: payload `{version:1,document:{id,kind,episode,data,dependencies:[]}}`.
  The website accepts character/location/prop/costume/voice/sound with `card_contract:1` and scene_bindings with `bindings_contract:1`.
  Every card must have title, description, and its typed fields.
  For prop: function, optional material/size.
  For sound: category effect/ambience/music, direction, optional sources.
  For costume: character/design.

  For voice: character/direction. For location: setting/layout.
  For character: identity{name,appearance,traits}, dramatic{want,need,conflict,stakes,arc}, states.

- Sound sources: `sources:[{document:"prop_id",kind:"prop"}]`.
  The sources may be prop/character/location cards from the same project, including other episodes.
  An empty list means independent sound.
  Core examines current cards and derives dependencies.
  A card's episode records its origin. It does not restrict use to that episode.
- `propose_revision`: payload `{target,data}` with complete new data. Read the diff.
  `apply_revision`: payload `{proposal:proposal_id}` only after review.
  Such a proposal may explicitly convert an old generic card to a typed card.
  For an existing typed scene, only characters/location changes are permitted. Preserve all other fields.

  The limited web route prohibits scene creation and screenplay/staging edits.
  If no production scene exists, use the CLI.

`GET <base>/scene-inputs/<canonical-scene-id>?episode=E01&shot=<optional-shot-id>`
returns stable bindings_id, scene_cards owners, occurrences, selections, basis, stale, dependencies, request, and package_inputs.
CLI: `local scene-inputs
PROJECT_DIRECTORY INPUT.json`. INPUT contains scene, episode, and optional shot.
Hub API: `/api/v1/projects/<project-id>/scene-inputs/<scene-id>`.

One scene_bindings has data `{bindings_contract:1,scene,occurrences:[],selections:[]}`.
Occurrences: `{document,kind:"prop"|"costume"|"sound",shot?}`.
Selections: `{document,document_fingerprint,artifact,fingerprint,sha256,role,purpose,shot?}`.
Roles: identity/look/voice/location/prop/sound/previs.
Get the exact current card and its related material from public reads.
Do not replace an old SHA with the current file.

The scene/shot must belong to the exact episode. Library cards belong to the whole project.
Save the complete bindings, not the filtered response for one shot.
A draft reference does not automatically enter the confirmed set.
When request.ready=false, do not treat references as a ready request.
Unsupported types remain in package_inputs for an explicit workflow.

These reads do not replace gates, provider capability checks, or permission to execute.

For subsequent remote CLI pages, pass QUERY.json:
`documents PROJECT
[QUERY.json]`, `jobs PROJECT [QUERY.json]`, `artifacts PROJECT [QUERY.json]`,
`tasks PROJECT JOB [QUERY.json]`, `materials PROJECT [EPISODE] [QUERY.json]`.
The file contains `limit`, `offset`, the returned `checkpoint`, and required filters.
`events PROJECT [AFTER] [QUERY.json]` uses `next_after`.
`job PROJECT JOB` reads one job.
Production commands remain local.
