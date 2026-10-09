---
name: film-studio-workflow
description: Operate the Film Studio website and public CLI/API. Find assigned production tasks, transfer inputs and results over SSH, and record reviews through Studio. Use for film production and generator handoffs. Do not use for application development.
---

# Film Studio workflow

Studio stores the project and checks changes. An external machine does the assigned work.
First, identify the film, your role, and your assignment.
The interface shows the film name. Requests use its stable ID.
Each film has one universe and one shared library.

Cards are available in all project episodes. The system does not yet support a common pinned version set for each episode.

Read [access and interfaces](references/access.md) for the website address, SSH access, available operations, and assignment discovery.
If private settings are absent, get them from the operator.
Do not extract passwords from the browser or another person's configuration.
Keep secrets out of results and Git.

## Select the workflow

- **View and review:** Open the film on the website. Examine the screenplay, universe, materials, and «Работы».
  Save ideas, comments, or the required review through the page or its limited HTTP command.
- **Operator or external creative agent:** Read the current context and assigned task through the public CLI.
  Use the task's frozen skill/contract bytes and built-in writer workflow.
  Use proposal/apply for changes to the accepted screenplay and cards.
  Do not create a parallel writer or a separate accepted state in chat.
- **Generator machine:** Get the assigned package from `/srv/film-studio/packages`.
  Examine its ID, basis, hashes, and requirements. Do the assigned work locally.
  Transfer the complete result to your incoming directory. Return the manifest/receipt to the operator.
  The operator imports the result through the applicable public Studio command.

## Cards and relations

Create typed cards in «Библиотеке».
For changes to existing cards, use proposal/apply and examine the diff.
This requirement includes explicit conversion of an old generic card.
Sound can explicitly refer to a prop, character, or location.
Their presence in the same scene does not create that relation.
Costume and voice belong to a character.

For a scene, edit the existing production card's characters/location separately from additional relations and selected files.
Before/after states are read-only.

Before you transfer inputs, read `scene-inputs`.
An object's presence does not prove that its file is present.
Use exact versions, roles, and hashes. Examine stale selections again.
A complete input set gives no permission to run work or spend money.
Read the [reference](references/access.md) for exact routes and limited commands.

## Get the assignment

«Работы» and the HTTP jobs list show progress.
They are not a queue of arbitrary tasks that you may start independently.
Get a complete external creative assignment through `local tasks PROJECT_DIRECTORY JOB_ID`.
The task contains inputs, role, skill bytes, contract, and basis.
The operator gives the generator an explicitly assigned package and result requirements.

If no assignment exists, report that no work was assigned.
Do not start generation from a film name alone or an empty materials list.

Before a write, read the current revision.
When a request's result is unknown, preserve its original `expected_revision` and `idempotency_key`.
A retry with the same key examines the receipt.
After conflict 409, read the basis again and examine the intended change. Preserve the draft.
Do not change the key to bypass a conflict.

Examine unfinished or unconfirmed external work through the original receipt.
Do not restart it without that check.

Attach comments to the scene/item and the version that you examined.
For media, retain the ID, SHA-256, and timecode.
Before H3 acceptance through `record_media_review`, perform actual visual and audio review. Obtain an explicit human decision.
Successful decoding or a short film description does not satisfy that requirement.

Git stores text history after Studio accepts a change.
A commit or GitHub file edit does not approve a stage, start work, or apply a project change.
A local commit and a push to GitHub are different states.
Examine the synchronization status.
