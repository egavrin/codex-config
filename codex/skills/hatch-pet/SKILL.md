---
name: hatch-pet
description: "Create, repair, validate, visually inspect, and package Codex-compatible v2 animated pets. Accept character art, generated images, company or prospect brand cues, or visual references. Use for any new Codex pet, custom mascot, non-pixel style, brand-inspired pet, or existing-pet repair. Also use for an 8x11 spritesheet workflow with all 9 standard animation rows and 16 look directions. Use deterministic assembly, QA artifacts, and spriteVersionNumber 2 packaging."
---

# Hatch Pet

## Overview

Create a Codex-compatible v2 animated pet from the supplied inputs. Inputs include concepts, brand cues, company/prospect names, reference images, and combinations of these. Every newly hatched pet is an 8x11 atlas with the 9 standard animation rows plus 16 clockwise look directions and is packaged with `spriteVersionNumber: 2`. The intermediate 8x9 atlas exists only to assemble and review rows 0-8. Never package it as a new pet.

User-facing inputs are optional. If the user omits a pet name, infer one from the concept, brand, company, or reference filenames. If no name follows from those sources, select a short friendly name. If the user omits a description, infer one from the concept or references. If the user omits reference images, first generate the base pet from text. Use that base as the canonical reference for every animation row.

## Existing Inputs And Upgrades

Treat character art, generated images, standard or v2 atlases, contact sheets, and built-in pet art as first-class grounding inputs.

- Preserve user-provided art as a generation reference. Do not assume it already has final cell geometry.
- For an existing valid 8x9 atlas, first complete deterministic and visual validation. Then, use it as the rows `0-8` intermediate. Generate rows `9-10` and package the result as v2.
- For an existing 8x11 atlas, preserve approved standard rows. If a look cell fails, correct the complete containing 8-frame row before deterministic reassembly. Never package a newly generated one-off repair cell beside cells from another generation.
- For a built-in pet, extract and use its atlas or neutral/idle cell as the canonical identity reference.
- Include every image that defines head shape, face, palette, markings, material, flame/ears/hair, props, or look mechanics in look-direction generation.
- When a renderer or source supplies a dedicated neutral/front frame, pass it through `--neutral-cell`. Otherwise, use the approved idle/default frame. The 16 directional cells never treat `000` as neutral.

## Generation Delegation

Use `$imagegen` for all normal visual generation.

Before generating base art, row strips, or repair rows, load and follow the installed image generation skill:

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

Do not call the Image API, image CLI, or any other image-generation path directly. Let `$imagegen` choose its own built-in-first path and fallback rules. If `$imagegen` says a fallback is conditional on confirmation, ask the user before continuing.

When invoking `$imagegen`, pass the generated pet prompt as the authoritative visual spec. Pet prompts should stay concise, state-specific, sprite-production oriented, and grounded in the listed input images. Keep longer policy and QA rules in this skill and the deterministic review scripts. Do not expand them into every image prompt. Do not wrap prompts in the generic `$imagegen` shared prompt schema.

Use this skill's scripts only for deterministic image work. This scope includes layout guides, prompts, approved `running-left` mirroring, frame extraction, row validation, and final atlas composition. It also includes contact sheets and motion-preview QA media. Parent-owned shell/`jq` steps handle manifest updates, packaging, and cleanup.

## Runtime Dependencies

Before running any bundled script, call `load_workspace_dependencies`. Set `PYTHON` to the exact Python executable path returned by that tool and use `"$PYTHON"` for every command below. The bundled runtime includes Pillow, which is necessary for these scripts. Do not use a bare system `python`. If workspace dependencies are unavailable, stop and report that the bundled runtime is required.

## Storage Controls

The built-in `$imagegen` path stores generated PNG bytes in the rollout that invokes it, even when it also writes a file under `${CODEX_HOME:-$HOME/.codex}/generated_images`. Deleting files later reduces filesystem use, but it does not shrink an already-written rollout. Keep image generation isolated and bounded:

- Use one lightweight generation worker per visual job. Do not batch multiple base/row jobs into the same worker.
- Workers must return only `selected_source=...` and `qa_note=...`. They must not include Markdown image previews, base64, or extra visual attachments in their final response.
- The parent must not open every generated PNG visually. Use worker QA for each job and inspect only the final contact sheet.
- After you copy the selected output into `decoded/`, remove its original from `${CODEX_HOME:-$HOME/.codex}/generated_images` if it is there. Then, remove the generation directory if it is empty and removal is possible.
- For storage-sensitive full runs, ask the user whether to use the `$imagegen` CLI fallback when available. Local API credentials and explicit user confirmation are necessary for that path, but it can avoid built-in image payloads being embedded in rollout events.

## Brand Discovery

If the user supplies only a brand, company, product, or prospect name, first run a lightweight discovery subagent. This rule applies when no concrete avatar description or reference image exists. Prepare the pet run after discovery. The discovery worker must use web search. It must prefer official brand sites, product pages, documentation, about pages, press pages, or brand pages. Use reputable secondary sources only when official pages are too thin.

Keep the search narrow: enough to extract visual and personality cues, not a market-research brief.

If the user supplies a concrete mascot/avatar description or reference images, skip discovery. Explicit requests for brand research are an exception.

Discovery worker responsibilities:

- search the web for 2-4 relevant sources, preferring official pages
- write an adaptive markdown brief rather than a rigid field dump
- cover identity/category, audience/use context, visual system, personality/tone, product/domain motifs, mascot translation cues, avoidances, and evidence/confidence
- mark mascot guidance that is inferred from sources as inference
- avoid copying logos, readable marks, UI screenshots, slogans, or text
- end with a compact `Generation handoff` section containing only `brand_name`, `brand_brief`, `avatar_seed`, `avoid`, and `brand_sources`
- do not generate images, prepare run folders, or edit unrelated files

Use this discovery worker prompt:

```text
Research a brand for hatch-pet mascot creation.

Brand/product/prospect: <brand name>
User context: <short user request>
Output file: <absolute path to brand-discovery.md>

Use web search. Prefer official brand, product, docs, about, press, or brand pages. Use reputable secondary sources only if official sources are too thin. Write an adaptive markdown brief to the output file. Headings may flex by brand, but the brief must cover:
- identity/category: canonical name, product type, what it does
- audience/use context: who it serves and where it appears
- visual system: palette, shapes, line quality, materials, typography feel, iconography, patterns
- personality/tone: emotional traits, energy, formality, playfulness
- product/domain motifs: objects, workflows, verbs, metaphors, environments
- mascot translation cues: candidate forms, signature traits, props, what must read at pet size
- avoidances: logos/text, trademark-sensitive elements, misleading cues, competitor confusion, poor mascot fits
- evidence/confidence: source URLs plus notes where evidence is weak or inferred

Do not copy logos, readable marks, UI screenshots, slogans, or text. Clearly label mascot guidance that is inferred rather than directly sourced.

End the brief with a `Generation handoff` section containing exactly:
- brand_name=<canonical brand/product name>
- brand_brief=<one sentence, max 45 words, covering palette/tone/domain motifs/personality>
- avatar_seed=<short mascot-safe visual idea, no logo copying>
- avoid=<short comma-separated list>
- brand_sources=<comma-separated source URLs>

Return exactly:
brand_discovery_file=<absolute output file path>
brand_name=<canonical brand/product name>
brand_brief=<same compact sentence from Generation handoff>
avatar_seed=<same short seed from Generation handoff>
avoid=<same short avoid list from Generation handoff>
brand_sources=<same comma-separated URLs from Generation handoff>
```

The parent should save the markdown brief before run preparation. Then, pass it to `prepare_pet_run.py` as `--brand-discovery-file`, with `--brand-name`, `--brand-brief`, and repeated `--brand-source`. Unless the user supplies a better avatar description, also pass concise `--pet-notes` from `avatar_seed`. Keep the full brief for review. Only the compact handoff fields should shape prompts. If web search is unavailable and the user gave only a bare brand name, ask for brand cues before generating.

## Generation Contract

### Visual Job Graph

Expect up to 13 visual jobs:
- 1 base pet.
- 9 standard row strips.
- 1 required four-cardinal anchor strip.
- 2 required coherent look-direction row strips. The standard states are `idle`, `running-right`, `running-left`, `waving`, `jumping`, `failed`, `waiting`, `running`, and `review`. Only `running-left` may use deterministic visual derivation. First, generate and visually examine `running-right`. Mirror `running-right` only after explicit approval that mirroring is safe. If mirroring is not appropriate, generate `running-left` as a normal grounded `$imagegen` row.

### Look Direction Sequence

After rows 0–8 pass validation, write qa/look-mechanics.md. Then, generate and approve one four-pose cardinal strip. Use this fixed order: 000 up, 090 screen-right, 180 down, and 270 screen-left. Generate row 9 as one coherent eight-pose family from the approved cardinal pose families.

Interpolate the intermediate directions as even 22.5-degree steps. Deterministically register its eight ordered pose groups, then run final-cell edge, semantic, and continuity QA immediately. Only after row 9 passes, generate row 10 as one coherent eight-pose family.

Use the approved cardinals for direction meaning. Use completed row 9 for identity, scale, registration, and boundary continuity. Run the same QA immediately after row 10. Row 9 contains 000, 022.5, 045, 067.5, 090, 112.5, 135, and 157.5.

Row 10 contains 180, 202.5, 225, 247.5, 270, 292.5, 315, and 337.5. 000 means up, not neutral/front. Never ask $imagegen to generate or repair a complete 8×11 atlas.

### Visual Provenance And Grounding

After visual selection, the parent copies that exact image into the job's `decoded/` path. It runs the required incremental checks. Only then mark the job complete in `imagegen-jobs.json`. Do not write helper scripts that populate row outputs. The deterministic Python scripts may only process already-generated visual outputs.

Only the base job may be prompt-only. For every `$imagegen` row-strip job, use all input images listed in `imagegen-jobs.json`. Include the canonical base reference created after the selected base output is copied. Treat any row generation without attached grounding images as invalid.

## Pet-Safe Styles

Default style is `auto`. Infer the pet's style from the user's prompt and references. Then, preserve that style across every row. If the user names a style, honor it. Supported style presets include `pixel`, `plush`, `clay`, `sticker`, `flat-vector`, `3d-toy`, `painterly`, `brand-inspired`, and `auto`.

Any style is acceptable when it remains pet-safe:

- compact whole-body silhouette readable inside a `192x208` cell
- consistent face, proportions, material, palette, and props across all rows
- clean removable chroma-key background
- details large enough to read at pet size
- no text, labels, UI, or readable logos unless the user explicitly provides approved reference art and asks for them

Non-pixel styles are first-class. These styles should be accepted when they satisfy atlas and readability constraints:
- Plush, clay, sticker, vector, and 3D toy.
- Painterly mascot, ink, and brand-inspired looks.

## Transparency And Effects

Pet rows become transparent `192x208` cells. Every generated pixel must belong to the pet sprite or a cleanly removable chroma-key background. Prefer pose, expression, and silhouette changes over decorative effects.

The deterministic raster pipeline owns the transparency and chroma-cleanup invariants. The final edge-local spill-suppression step selects every translucent silhouette-boundary pixel. It also selects opaque boundary pixels whose chroma points toward the known key. It extends clean interior RGB outward through that band in linear light. It preserves alpha exactly, clears hidden RGB under fully transparent pixels, and reports the algorithm and parameters used. The cleanup report plus atlas validator are authoritative for chroma contamination.

Once the final report has `ok: true` and atlas validation passes, do not regenerate imagery or add another chroma-cleanup pass.

Fully transparent pixels are permitted outside the silhouette and in unused cells. They are also permitted in intentional design openings, such as loops or holes in a ribbon body. Reject accidental 100%-transparent holes inside a filled body in any generated or repaired cell. This includes horizontal bands, seam rows, scanline-like gaps, sliced-tile boundaries, and "see-through" interior stripes. Before acceptance, inspect suspect cells on a high-contrast background or alpha mask. Ordinary atlas validation is insufficient for an interior silhouette hole.

Allowed effects must satisfy all of these conditions:

- The effect is state-relevant and helps explain the animation.
- The effect is physically attached to, touching, or overlapping the pet silhouette, not floating nearby.
- The effect is inside the same frame slot as the pet and does not create a separate sprite component.
- The effect is opaque, hard-edged enough for clean extraction, and uses non-chroma-key colors.
- The effect is small enough to remain readable at `192x208` without clutter.

Avoid these by default because they usually break transparent-background cleanup or component extraction:

- wave marks, motion arcs, speed lines, action streaks, afterimages, blur, or smears
- detached stars, loose sparkles, floating punctuation, floating icons, falling tear drops, separated smoke clouds, or loose dust
- cast shadows, contact shadows, drop shadows, oval floor shadows, floor patches, or landing marks
- impact bursts, glow, halo, aura, or soft transparent effects
- text, labels, frame numbers, visible grids, guide marks, speech bubbles, thought bubbles, UI panels, or code snippets
- checkerboard transparency, white backgrounds, black backgrounds, or scenery
- chroma-key-adjacent colors in the pet, prop, effects, highlights, or shadows
- stray pixels, disconnected outline bits, speckle/noise, cropped body parts, or overlapping poses
- any pose that crosses into a neighboring frame slot

State-specific guidance:

- `idle`: keep this calm and low-distraction. Use only subtle breathing, tiny blinks, slight head/body bobs, very small material sway, or another quiet motion that preserves persona. The loop must still contain visible micro-variation. Do not accept six effectively identical copies. Do not show waving, walking, running, jumping, talking, working, reviewing, emotional reactions, large gestures, item interactions, or new props.
- `waving`: show the wave through paw, hand, wing, or limb pose only. Do not draw wave marks, motion arcs, lines, sparkles, symbols, or floating effects around the gesture.
- `jumping`: show vertical motion through body position only. Do not draw shadows, dust, landing marks, impact bursts, bounce pads, or floor cues.
- `failed`: Tears, attached smoke puffs, and attached stars are permitted under the allowed-effects rules. Do not use red X marks, floating symbols, detached smoke, detached stars, or separate tear droplets.
- `waiting`: show that Codex waits for approval, help, or user input through an expectant asking pose. Keep it distinct from ordinary idle and review.
- `running`: show active task work, processing, thinking, scanning, typing, or focused effort. Do not show literal foot-running, jogging, sprinting, treadmill motion, raised knees, long steps, or pumping arms. Also prohibit directional travel, speed lines, dust clouds, floor shadows, motion trails, and detached motion effects.
- `review`: show focus through lean, blink, eyes, head tilt, or paw/hand position. Add no new props unless they already exist in the base pet identity. Examples include magnifying glasses, papers, code, UI, punctuation, and symbols.
- `running-right` and `running-left`: show directional drag movement through body, limb, and prop movement only. `running-right` must face and travel right. `running-left` must face and travel left. Their cadence must visibly alternate across the loop rather than repeating one nearly static stride. Do not draw speed lines, dust clouds, floor shadows, motion trails, or detached motion effects.

## Visible Progress Plan

For every pet run, keep a visible checklist so the user can see where the work is up to. Create the checklist before starting, keep one step active at a time, and update it as each step finishes.

Use this checklist for every v2 pet run, replacing `<Pet>` with the pet's name or `your pet`:

1. Getting `<Pet>` ready.
2. Imagining `<Pet>`'s main look.
3. Picturing `<Pet>`'s poses.
4. Hatching `<Pet>`.

What each step means:

- `Getting <Pet> ready.` Select the pet name, description, source images, style preset, style notes, and working folder, or make sure these are correct. For bare brand/product/company requests, first run the brand discovery worker. Record the compact brand brief, source URLs, and avatar seed.
- `Imagining <Pet>'s main look.` Generate the pet's main reference image. This becomes the visual source of truth.
- `Picturing <Pet>'s poses.` Generate and approve rows `0-8`, write the pet-specific look mechanics plan, then generate rows `9-10`. Only mirror `running-left` if `running-right` clearly works when flipped.
- `Hatching <Pet>.` Assemble the 8x11 atlas. Review standard motion and all 16 look directions. Repair every failed cell or row. Package `spriteVersionNumber: 2` and report output paths.

Only mark a step complete when the real file, image, or decision exists. If this is a repair run, start from the first relevant step instead of restarting the whole checklist.

## Time Budget And Convergence

Aim to complete a normal pet run within 30 minutes while preserving every mandatory acceptance criterion. Use this planning target to maximize validated progress per minute. It gives no permission to weaken QA or package a failed pet.

At the start of the run, allocate an approximate budget:

- preparation: 2 minutes
- base image: 3 minutes
- standard rows: 10 minutes
- look directions: 8 minutes
- final QA and packaging: 5 minutes
- buffer: 2 minutes

Run independent generation jobs concurrently up to the worker limit. Start deterministic checks when each dependency is ready. Record actual stage and repair time. Prefer character and prop constructions that naturally satisfy cell geometry, transparency, component connectivity, and direction semantics. Before row generation, identify likely conflicts. Examples include open interior gaps, detached parts, thin connectors, asymmetric props, and ambiguous faces.

After every failed attempt:

1. Classify the failure as visual semantics, identity, source-edge geometry, component connectivity, extraction, chroma, continuity, or final visual QA.
2. State the concrete evidence and the root condition the next action will change.
3. Use a deterministic correction for deterministic failures before regenerating imagery.
4. Regenerate only when the source visual is genuinely wrong, and preserve every property that already passed.
5. Compare the new result with the previous one. A repair counts as progress only when it reduces the number or severity of failures without breaking a previously passing gate.

If the same root failure occurs twice, stop prompt variation and change strategy. Strengthen cardinal pose families or row-level direction instructions, simplify poses or props, change deterministic extraction, or redesign the problematic feature. If a repair only moves a failure to another cell or gate, treat it as a cycle. Change strategy immediately.

Use elapsed-time checkpoints:

- At 15 minutes, make sure that the run is on pace and that the remaining dependency path is bounded.
- At 25 minutes, prioritize the shortest quality-preserving path through remaining blockers and avoid optional polish.
- At 30 minutes, continue only when remaining work clearly converges and is bounded. Examples include final validation, one targeted repair, or packaging.
- Record elapsed time, retries, validation failures, and QA cost throughout the run. Do not pause or stop only because elapsed time exceeds 45 or 60 minutes. Continue until the pet passes, the user cancels, or a genuine external blocker prevents further progress.

Never use the time target to omit blind direction QA, labeled semantics, continuity review, or atlas validation. Do not omit despill validation, final visual QA, or any other acceptance criterion.

## Default Workflow

1. Prepare a pet run folder and imagegen job manifest:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet"
"$PYTHON" "$SKILL_DIR/scripts/prepare_pet_run.py" \
  --pet-name "<Name>" \
  --description "<one sentence>" \
  --reference /absolute/path/to/reference.png \
  --output-dir /absolute/path/to/run \
  --pet-notes "<stable pet description>" \
  --brand-discovery-file /absolute/path/to/brand-discovery.md \
  --brand-name "<optional researched brand name>" \
  --brand-brief "<optional compact researched brand cue sentence>" \
  --brand-source "https://example.com/source" \
  --style-preset auto \
  --style-notes "<optional freeform style notes>" \
  --force
```

All arguments above are optional except any flags needed to express user constraints. For text-only requests, pass the concept through `--pet-notes` and omit `--reference`. `prepare_pet_run.py` infers a name, description, chroma key, and output directory as necessary.
For brand-only requests, first run the discovery worker and save the Markdown brief.

Pass the brief path through `--brand-discovery-file`. Pass `avatar_seed` through `--pet-notes`, `brand_name` through `--brand-name`, and `brand_brief` through `--brand-brief`. Pass each source URL through a separate `--brand-source`.

2. Inspect `imagegen-jobs.json` for the next ready `$imagegen` jobs. A job is ready when its `status` is not `complete` and every id in `depends_on` is already complete. Prefer reading the manifest directly with `jq` or the editor instead of adding helper scripts for status display:

```bash
jq '.jobs[] | {id, kind, status, depends_on, prompt_file, retry_prompt_file, input_images, output_path, derivation_policy}' /absolute/path/to/run/imagegen-jobs.json
```

3. Generate visual jobs with lightweight workers by default:

- Generate and copy `base` first, using a lightweight base worker.
- Generate and copy `idle` and `running-right` next as the identity and gait check, using one lightweight worker per row.
- Inspect `running-right`. Mirror `running-left` only when visual identity, prop placement, markings, lighting, and direction semantics remain correct.
- Generate `running-left` normally with a lightweight worker when mirroring would change meaning or identity.
- Generate the remaining rows with lightweight workers, using every input image listed for each job.
- After standard-row QA, generate `look-cardinals` as one four-pose strip. Extract it into `decoded/look-anchors/000.png`, `090.png`, `180.png`, and `270.png`. Approve all four. The `090` and `270` anchors must be unmistakable in viewer/screen coordinates and visibly oppose each other.
- Generate look row 9 as one coherent eight-pose synthesis from the approved cardinal strip. Interpolate each intermediate direction as an even step between adjacent cardinal pose families. Recover the eight ordered pose groups deterministically. Crop them and normalize them with one shared scale and baseline. Immediately run final-cell edge diagnostics and labeled per-direction QA, before row 10 or final atlas assembly.
- Only after row 9 passes, generate row 10 as one coherent synthesis. Use the approved cardinal strip and completed row 9.

Keep up to three generation workers active whenever three independent jobs are ready and worker capacity is sufficient. Backfill an available slot immediately instead of waiting for a fixed wave to finish. Use two or one worker when the dependency graph exposes fewer ready jobs. Do not exceed three generation workers without explicit user direction.

For each ready visual job, invoke `$imagegen` with the prompt file and all input images listed in `imagegen-jobs.json`. Include each image's role label. Use the default built-in `image_gen` path unless `$imagegen` routes otherwise. The parent agent must keep its own image handling minimal.

Do not open every generated base or row in the parent rollout. Workers return only the selected source path and a one-sentence QA note. The parent records the selected source path in the manifest.

`prepare_pet_run.py` creates matching layout guides under `references/layout-guides/` for the nine standard rows, two look rows, and four-cardinal strip, and both look rows. Visual jobs attach the matching guide as a layout-only input. This helps the model follow the correct frame count, spacing, centering, and safe padding. Treat these guides as invisible construction references. Generated strips must not include visible boxes, borders, center marks, labels, guide colors, or the guide background.

When generating row strips, keep the identity lock in the row prompt authoritative. Preserve the same style, face, markings, palette, materials, prop design, body proportions, and silhouette from the canonical base. Row jobs attach the layout guide and canonical base by default. Keep the decoded base in the run folder for deterministic processing. Do not send it as a redundant generation input.

If `$imagegen` returns a transport-level `Bad Request` for a row, retry that same row once with its generated `retry_prompt_file`. The retry prompt preserves the row id, frame count, chroma key, canonical-base identity, and state action. Keep the canonical base attached. If the retry still fails, stop. Report the failing row and prompt paths. Do not change to another generation path.

4. After selecting a generated output for a job, copy it into the decoded output path. For `base`, also create the canonical identity reference:

```bash
RUN_DIR=/absolute/path/to/run
JOB_ID=<job-id>
SOURCE=/absolute/path/to/generated-output.png
OUTPUT_REL=$(jq -r --arg id "$JOB_ID" '.jobs[] | select(.id == $id) | .output_path' "$RUN_DIR/imagegen-jobs.json")
mkdir -p "$(dirname "$RUN_DIR/$OUTPUT_REL")"
cp "$SOURCE" "$RUN_DIR/$OUTPUT_REL"
```

```bash
if [ "$JOB_ID" = "base" ]; then mkdir -p "$RUN_DIR/references"; cp "$RUN_DIR/$OUTPUT_REL" "$RUN_DIR/references/canonical-base.png"; fi
```

For every standard `row-strip` job, immediately extract and inspect only that row before marking the job complete. This overlaps deterministic QA and any repair with generation of other ready rows instead of waiting for all nine rows:

```bash
ROW_QA_DIR="$RUN_DIR/qa/rows/$JOB_ID"
"$PYTHON" "$SKILL_DIR/scripts/extract_strip_frames.py" \
  --decoded-dir "$RUN_DIR/decoded" \
  --output-dir "$ROW_QA_DIR/frames" \
  --states "$JOB_ID" \
  --method auto
"$PYTHON" "$SKILL_DIR/scripts/inspect_frames.py" \
  --frames-root "$ROW_QA_DIR/frames" \
  --json-out "$ROW_QA_DIR/review.json" \
  --states "$JOB_ID" \
  --require-components
```

Treat errors as an immediate repair request. Inspect warnings before accepting the row. Do not defer a known clipping, component, or extraction problem to final atlas QA. Chroma cleanup belongs to the deterministic post-assembly despill pass and must not trigger row regeneration.

If only component extraction fails, examine the source strip's scale and placement. When both are stable, use the existing `stable-slots` correction with `--allow-stable-slots`. Do not regenerate imagery for that failure.

For `look-cardinals`, extract and validate all four anchors before marking the job complete:

```bash
CHROMA_KEY=$(jq -r '.chroma_key.hex' "$RUN_DIR/pet_request.json")
"$PYTHON" "$SKILL_DIR/scripts/extract_cardinal_anchors.py" \
  --strip "$RUN_DIR/decoded/look-cardinals.png" \
  --output-dir "$RUN_DIR/decoded/look-anchors" \
  --chroma-key "$CHROMA_KEY" \
  --json-out "$RUN_DIR/qa/cardinal-anchors.json"
"$PYTHON" "$SKILL_DIR/scripts/compose_cardinal_anchor_strip.py" \
  --anchors-dir "$RUN_DIR/decoded/look-anchors" \
  --output "$RUN_DIR/decoded/look-anchors-approved.png"
```

Approve the four extracted anchors semantically at final pet size. If one cardinal fails, regenerate that individual anchor with `prompts/look-anchor-repairs/<degree>.md`, replace only its extracted file, and run again `compose_cardinal_anchor_strip.py`. Both final look rows use the approved cardinal strip, and row 10 additionally uses completed row 9. Mark the job complete only after its required deterministic and visual checks pass:

```bash
UPDATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TMP_MANIFEST=$(mktemp)
jq --arg id "$JOB_ID" --arg source "$SOURCE" --arg at "$UPDATED_AT" '(.jobs[] | select(.id == $id)) += {status: "complete", source_path: $source, completed_at: $at}' "$RUN_DIR/imagegen-jobs.json" > "$TMP_MANIFEST"
mv "$TMP_MANIFEST" "$RUN_DIR/imagegen-jobs.json"
```

After `decoded/look-anchors-approved.png` exists and all four cardinals have passed semantic review, mark `look-cardinals` complete. Row 9 then becomes ready immediately.

If the copied source is under `${CODEX_HOME:-$HOME/.codex}/generated_images`, delete the original generated file after the decoded copy exists:

```bash
GENERATED_ROOT="${CODEX_HOME:-$HOME/.codex}/generated_images"
case "$SOURCE" in
  "$GENERATED_ROOT"/*)
    rm -f "$SOURCE"
    rmdir "$(dirname "$SOURCE")" 2>/dev/null || true
    ;;
esac
```

5. Derive `running-left` only when it is visually safe:

```bash
"$PYTHON" "$SKILL_DIR/scripts/derive_running_left_from_running_right.py" \
  --run-dir /absolute/path/to/run \
  --confirm-appropriate-mirror \
  --decision-note "<why mirroring preserves this pet's identity>"
```

That script mirrors each generated frame slot in place so the leftward row preserves the rightward row's temporal order. Do not replace it with a whole-strip mirror that reverses animation timing.

6. When all nine incrementally validated standard row jobs are complete, build and review the intermediate rows `0-8`:

```bash
RUN_DIR=/absolute/path/to/run
mkdir -p "$RUN_DIR/final" "$RUN_DIR/qa"
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/extract_strip_frames.py" \
  --decoded-dir "$RUN_DIR/decoded" \
  --output-dir "$RUN_DIR/frames" \
  --states all \
  --method auto
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/inspect_frames.py" \
  --frames-root "$RUN_DIR/frames" \
  --json-out "$RUN_DIR/qa/review.json" \
  --require-components
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/compose_atlas.py" \
  --frames-root "$RUN_DIR/frames" \
  --output "$RUN_DIR/final/spritesheet.png" \
  --webp-output "$RUN_DIR/final/spritesheet.webp"
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/make_contact_sheet.py" \
  "$RUN_DIR/final/spritesheet.webp" \
  --output "$RUN_DIR/qa/contact-sheet.png"
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/render_animation_previews.py" \
  --frames-root "$RUN_DIR/frames" \
  --output-dir "$RUN_DIR/qa/previews"
```

If per-frame fit-to-cell extraction causes size pops or baseline jumps, examine the original row strip. If its scale and placement were stable, extract frames again with the explicit row-stability mode. Then, repeat inspection, atlas composition, contact sheet generation, and previews:

```bash
"$PYTHON" "$SKILL_DIR/scripts/extract_strip_frames.py" \
  --decoded-dir "$RUN_DIR/decoded" \
  --output-dir "$RUN_DIR/frames" \
  --states all \
  --method stable-slots
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/inspect_frames.py" \
  --frames-root "$RUN_DIR/frames" \
  --json-out "$RUN_DIR/qa/review.json" \
  --require-components \
  --allow-stable-slots
```

Use `stable-slots` as a deliberate QA-driven correction, not the default. It should reduce extraction-induced motion pops without hiding clipped wide poses or bad source strips.

Expected intermediate output before the required v2 look stage:

```text
run/
  pet_request.json
  imagegen-jobs.json
  prompts/
  decoded/
  frames/frames-manifest.json
  final/spritesheet.webp
  qa/contact-sheet.png
  qa/previews/*.gif
  qa/review.json
```

Inspect `qa/contact-sheet.png` and `qa/previews/*.gif` before generating look rows. `qa/review.json` plus visual motion review are the intermediate gates. The standard contact sheet precedes chroma cleanup. Visible key-color fringe there is not a failure. Judge chroma only on the cleaned final v2 atlas. Block progress if a standard row changes identity, style, prop handedness, or silhouette.

Also block progress if playback pops, reverses cadence, faces the wrong direction, or shows no visible motion. Do not package or clean up yet.

## Required V2 Look-Direction Stage

Every new pet must complete this stage. After standard-row QA passes, write `qa/look-mechanics.md`, approve the four cardinals, synthesize and validate the complete `look-row-9`, then synthesize `look-row-10`. Row 10 is ready only after row 9 passes deterministic registration and post-registration edge checks. Row 9 must have no semantic or continuity hard failure. Reviewed warnings may remain. It uses row 9 plus the approved cardinal strip as continuity evidence.

Before either look row, run the prepared `look-cardinals` strip job, extract its four cells with `extract_cardinal_anchors.py`, and approve them. Do not let a two-row sweep invent its own left/right basis. `090` must point toward the viewer's screen-right edge. `270` must point toward the viewer's screen-left edge. For faces, the nose tip and pupils must cross to the applicable side of the head center. If one cardinal is ambiguous, regenerate only that anchor before continuing.

After copying row 9 into `decoded/look-row-9.png`, register and edge-check it with the same transform used by final assembly:

```bash
"$PYTHON" "$SKILL_DIR/scripts/assemble_extended_atlas.py" \
  --base-atlas "$RUN_DIR/final/spritesheet.webp" \
  --look-row-9 "$RUN_DIR/decoded/look-row-9.png" \
  --neutral-cell "$RUN_DIR/frames/idle/00.png" \
  --chroma-key "$CHROMA_KEY" \
  --chroma-threshold 96 \
  --registered-row-output "$RUN_DIR/qa/look-row-9-registered.png" \
  --registration-manifest-output "$RUN_DIR/qa/look-row-9-registration.json"
```

Inspect the eight registered cells at normal pet size in `000` through `157.5` order. Record the row-9 semantic and adjacent-continuity review. For any hard failure, resynthesize the complete row. Mark `look-row-9` complete only after this check passes. That completion makes row 10 ready in `imagegen-jobs.json`.

Generate only the additional look-direction visuals with `$imagegen`:

- Required for new pets: two coherently synthesized 8-frame row strips, one for row 9 and one for row 10.
- Always include the canonical base reference and approved 8x9 contact sheet.
- Keep the body scale, baseline, head size, face, materials, palette, markings, and props consistent with the standard atlas.
- Before prompting, write a short look mechanics decision for this specific pet. First ask: **what is the best natural motion for this character when looking around?** Describe the anchor, the part that leads the gaze, and the parts that follow. Describe each bend, shift, turn, squash, stretch, or deformation. Include eyes and props. Decide whether physical eyeballs rotate, irises move on a fixed surface, eyelids change shape, or pupils slide.

  Decide whether props stay stable, lag slightly, or move with the body. Use the character's physical construction as the guide. Flexible wire should bend, soft bodies should deform, and separate heads should turn. Ears/fur/antennae may follow through. Physical eyeballs should rotate as complete eye globes in their sockets. Flat screen or sticker eyes may change drawn features on a fixed surface.

  Rigid or screen-like bodies may remain fixed while facial features move.
- Before generation, define a motion budget. Each 22.5-degree step should move the same parts by approximately the same visual amount. No adjacent pair should have a larger bend, scale change, prop shift, or silhouette change. An explicit asymmetry in the mechanics decision is the exception.

  First, generate row 9 along `000 -> 090 -> 180`. Give completed row 9 to row 10. Make sure that `180` begins exactly one step after `157.5`. Row 10 follows `180 -> 270 -> 000`, and `337.5` in row 10 must land one step before the approved `000` in row 9.
- Do not use whole-sprite rotation, whole-cell rotation, skewing, or affine tilting to fake gaze direction. Fail a direction row that rotates the complete pet unless both conditions hold:
  - The pet is a rotating rigid object.
  - The look mechanics decision explicitly specifies complete-object rotation. Whole-body tilt that makes the item/background appear to rock left or right is not natural look behavior for ordinary pets.
- Generate a coherent 16-pose gaze set, not 16 unrelated variants. Each direction should feel like a point on one continuous arc around the clock.
- Before generation, the look mechanics decision must name the natural pose family for each cardinal direction. Include the more-visible body side, hidden features, and the held prop's following or delayed motion. Do not let the generator infer all directions from one front-facing pose. For a character with a face or head, leftward directions must visibly turn or bend it left. Rightward directions must visibly turn or bend it right. Up/down directions must use eyes, eyelids, head angle, neck, and upper body as physically appropriate.

  Diagonals must interpolate between those pose families. A set where every cell remains essentially front-facing, or where all leftward cells still read as front/right-facing, is failed.
- Adjacent direction cells must have continuous body movement. Compare every neighboring pair in direction order, including `157.5 -> 180`, `337.5 -> 000`, and any row-strip boundary. Anchored parts must not jump, flip sides, or teleport between adjacent states. If a body part moves laterally, bends, stretches, or rotates, its position should progress gradually through intervening directions.
- Do not mirror, re-center, or independently regenerate adjacent direction cells in a way that changes the pet's body registration. Keep a stable anchor, usually the feet/base/torso/lower body or the character's naturally grounded part. Let only the intended look mechanics change around it.
- Every look cell must be visually distinguishable from the neutral/resting frame at final pet size. A direction cell that reads as front-facing, idle, or neutral is failed even when it is non-empty, transparent, and in the correct row/column.
- Cardinal directions must be semantically unmistakable at final pet size, not only numerically or geometrically different. Use the pet's natural mechanism for each direction. `000` must clearly look up, `090` right, `180` down, and `270` left. If the pet has no pupils or physical eyeballs, other features must clearly show direction. Use the head, face surface, eyelids, antennae, ears, or body bend. A viewer must be able to identify the cardinal without labels.
- Diagonal and intermediate directions should broadly occupy the intended quadrant and advance naturally through the ordered loop. Minor pupil, nose, eyelid, or feature-placement deviations are not failures by themselves. Reject only gross wrong-quadrant poses, visible reversals, or intermediate cells that break the coherent motion family.
- For eyeless object pets, do not default to literal whole-object rotation just because the object is rigid. First identify whether the object has a natural front, display face, playable surface, readable silhouette, or iconic viewing angle. Preserve that primary readable face unless the user explicitly asks for turntable rotation. Express look direction through subtle object-specific body language. Use small lean, neck/tip aim, hinge, yaw, pitch, bend, vibration, squash, follow-through, or attached-part motion. The direction should read as attention or orientation, not as the object spinning through all clock angles.
- Preserve the pet's original eye design in look-direction cells. Do not add new round "googly" eyes, replacement eye whites, floating pupils, or detached eye dots. Do not add a second eye layer over the source eyes. Eye motion must follow the look mechanics decision. If the pet has physical eyeballs, rotate or redraw each complete eyeball surface. The sclera/eye white, iris, pupil, eyelids, rim, and highlights must change together as one physical eye.

  Do not slide only the iris or pupil across a fixed eye white. If the pet has flat printed, sticker, or screen eyes, keep the surface fixed. Move or redraw only the features that would physically change on that surface. Use procedural pupil/iris compositing only when clipped to the original eye aperture.

  It must visibly stay inside the head silhouette in every direction. If clean preservation of the original eye design is impossible, regenerate the complete look cell with that eye construction. Do not composite new eyes over it.
- Eyes may lead the gaze, but pupil-only motion is an exception, not the default. Use it only when the look mechanics decision explains why other motion would be unnatural for that design. The explanation must cover whole-eye rotation, eyelid reshaping, and body, head, or feature movement. Large-eye pets, cyclops pets, and round rigid-body pets with physical eyeballs usually should rotate the whole eye globes.

  Pupil-only or googly-eye sliding is not the usual choice. Screen-face pets and printed-eye pets may be body-locked with feature motion only. Separate head/body pets should usually combine eye movement with head turn, head tilt, ear/fur/upper-body follow-through, and a stable torso.

  Rigid object mascots may hinge, flex, slide, or shift attached features without rotating the whole sprite. Flexible wire or paperclip-like mascots should usually keep their feet/base anchored. Their upper loop or face area should bend toward the target. Held props should remain stable or lag slightly. Blob or organic pets should usually keep a base anchored while the face/head area stretches subtly toward the target. Other pet types should get their own similarly grounded mechanics.
- Use look mechanics that preserve the persona of human or humanoid pets. Do not use broad non-rigid raster warps only to show a direction. This prohibition covers stretches of skull, brows, mouth, hoodie, hands, or held props. The eyes should usually lead the gaze with visible eye, eyelid, and eyebrow participation.

  Then, the head/neck and upper body should follow slightly. Fail a humanoid row if the head moves but the eyes remain fixed in one expression. A specific physical reason in the mechanics decision is the exception.

  Use small eye rotation, eyelid/eyebrow changes, head/neck turn, and restrained upper-body follow-through while preserving facial proportions and expression. Programmatic repairs must move anatomical parts with rigid or near-rigid part motion, not displacement fields that change facial feature spacing. Before look-direction generation, infer the physical constraints of each held, worn, or attached prop. Identify its anchor, rigidity or flexibility, leading or delayed motion, and expected occlusion as the character turns. Props near the face may show a side view, become partly hidden, or show different contact points. Hand-held tools may swing or lag slightly while attached.

  Worn props should follow the body. Flexible cords or straps should form continuous arcs. Do not keep the prop and character in the same front-facing relationship across all look directions. Before humanoid packaging, inspect normal-size neutral and cardinal cells together. Reject identity or facial-proportion drift. Reject a `270` cardinal that does not clearly point left.
- For every pet, use cardinal anchors instead of trusting a two-row sweep to preserve left/right semantics. Generate `000`, `090`, `180`, and `270` together as one strip, then extract and approve them. The final look rows use those four pose families for direction meaning and interpolate the intermediate directions as a coherent arc. Define directions in viewer/screen coordinates, never character-relative coordinates. Do not make exact pupil or nose placement mandatory on intermediate poses. Use the ordered loop and overall quadrant motion as primary evidence.
- Keep motion subtle and pet-safe: preserve volume, baseline, silhouette readability, identity, and material believability. Only when they naturally participate, use head, eyes, face, upper body, appendages, or body deformation in the look pose.
- Do not add labels, degree text, arrows, clocks, guide marks, shadows, glows, scenery, or detached effects.

Direction order is fixed:

```text
row 9:  000, 022.5, 045, 067.5, 090, 112.5, 135, 157.5
row 10: 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5
```

`000` means looking up / 12 o'clock. Neutral/front is the pointer deadzone and should fall back to idle unless the target renderer explicitly uses a neutral cell.

### Direction Acceptance Policy

Judge the completed 16-pose loop as an animation family. Cardinals must match their single axis exactly. Intermediate directions should preserve the intended axes. Use isolated blind-review uncertainty as evidence for labeled loop review. It does not automatically trigger regeneration.

For hard failures, generate the row again:

- a cardinal anchor is wrong or ambiguous: `000` up, `090` screen-right, `180` down, or `270` screen-left
- a blind cardinal classification contradicts or does not show `000` up, `090` screen-right, `180` down, or `270` screen-left
- Labeled normal-size review shows an intermediate pose in the wrong principal quadrant or a loop reversal. A required axis may also be lost enough that the pose shows a different direction.
- The ordered loop visibly reverses, backtracks, or crosses into the wrong principal quadrant. Alternatively, it has a conspicuous snap, identity change, scale pop, registration jump, or broken prop attachment.
- The source or atlas has a deterministic structural failure. Alternatively, visual review shows clipping, an accidental transparent interior hole, a seam band, replacement eyes, or a materially broken sprite.
- whole-sprite rotation, deformation, or eye mechanics visibly break the pet's identity or make the motion feel incoherent

Review warnings alone do not make regeneration necessary:

- An intermediate pose resembles a neighbor, a diagonal cue is subtle, or body movement is below the ideal mechanics plan.
- Blind reviewers disagree, return `ambiguous`, or produce an opposite-sign majority for an intermediate direction. Labeled normal-size review must show the intended direction, and the ordered loop must remain coherent.
- Continuity metrics identify a diff, center, area, or alpha-hole candidate. No visible snap, pop, seam, or broken silhouette appears in the QA sheet or animation loop.

Before v2 atlas acceptance, create a focused direction QA sheet. Put the neutral/rest frame beside all 16 look cells. Label each look cell with degrees and expected direction. Use approximately the in-app display size. Run the adjacent continuity measurement separately and treat its findings as motion-review evidence, not automatic direction failures.

Perform an explicit semantic review for every direction. Record `pass`, `warning`, or `fail`. Give separate visible evidence for its horizontal and vertical axes. A warning may accept blind-review uncertainty for an intermediate pose only under both conditions.

Labeled normal-size review must show the intended axes. The ordered loop must remain coherent. It may not waive a wrong or ambiguous cardinal, a labeled wrong-quadrant pose, or a visible reversal. If a direction receives `fail`, strengthen the containing row's instructions and resynthesize that complete coherent row.

Never replace the final normalized cell directly.

Look rows must have transparent backgrounds after assembly. Do not accept or install the pet if `qa/look-directions.png` or `qa/contact-sheet-extended.png` shows chroma-key panels behind any look cell. If generated look rows contain slight chroma-key lighting variation, run assembly again with a wider `--chroma-threshold`. Do not package the opaque key color. Validation must pass without opaque chroma-key-pixel errors.

Extended look cells must also keep the same practical scale and body registration as the neutral/default pet. Reject a direction set if neutral/default is noticeably larger than the look cells. Also reject floating look cells or left/right movement within the 192x208 cell during gaze-only changes. Extended assembly recovers each pose group from the complete original-resolution row. It calculates one shared scale from height and each pose's left/right extents around the shared lower-body anchor. Thus, asymmetric poses remain inside the final cell after alignment.

It resizes each original crop exactly once and never enlarges an already-resampled cell. The neutral frame supplies the target body height, lower-body anchor, and baseline. When an external neutral frame is available, pass `--neutral-cell`. Otherwise, the assembler uses the populated neutral/default slot or first visible idle frame in the base atlas. If the focused QA sheet still shows scale or placement drift, repair before packaging.

Assemble the extended atlas from two generated row strips:

Use the run's selected chroma key for every assembly path. Without it, assembly uses green and can misclassify a magenta background as clipped sprite pixels.

```bash
CHROMA_KEY=$(jq -r '.chroma_key.hex' "$RUN_DIR/pet_request.json")
```

Extended assembly reuses the approved registered row-9 cells and persisted scale exactly. It removes row 10's chroma background and detects eight separate pose groups. It preserves left-to-right order and crops each complete pose without fixed-slot slicing. It fits them to the same neutral-frame scale, lower-body anchor, and baseline. Only then does it apply the near-edge clipping check to row 10's normalized `192x208` cells. If pose-group recovery is ambiguous, resynthesize row 10.

Also resynthesize it if the approved row-9 transform causes a post-registration edge failure. Do not rescale row 9, repair an individual final cell, or relax the acceptance threshold.

```bash
"$PYTHON" "$SKILL_DIR/scripts/assemble_extended_atlas.py" \
  --base-atlas "$RUN_DIR/final/spritesheet.webp" \
  --registered-row-9 "$RUN_DIR/qa/look-row-9-registered.png" \
  --row-9-registration "$RUN_DIR/qa/look-row-9-registration.json" \
  --look-row-10 "$RUN_DIR/decoded/look-row-10.png" \
  --neutral-cell "$RUN_DIR/frames/idle/00.png" \
  --chroma-key "$CHROMA_KEY" \
  --chroma-threshold 96 \
  --output "$RUN_DIR/final/spritesheet-extended.png" \
  --webp-output "$RUN_DIR/final/spritesheet-extended.webp" \
  --manifest-output "$RUN_DIR/final/spritesheet-extended.json"
```

For repair or upgrade of a user-provided 16-cell source that was already approved as one coherent set, individual-cell assembly remains available. Do not use this path for newly generated repair cells:

```bash
"$PYTHON" "$SKILL_DIR/scripts/assemble_extended_atlas.py" \
  --base-atlas "$RUN_DIR/final/spritesheet.webp" \
  --look-cells-dir /absolute/path/to/look-cells \
  --neutral-cell "$RUN_DIR/frames/idle/00.png" \
  --chroma-key "$CHROMA_KEY" \
  --chroma-threshold 96 \
  --output "$RUN_DIR/final/spritesheet-extended.png" \
  --webp-output "$RUN_DIR/final/spritesheet-extended.webp" \
  --manifest-output "$RUN_DIR/final/spritesheet-extended.json"
```

Run the single deterministic edge-local spill-suppression pass on the assembled v2 atlas, then validate and make a contact sheet:

```bash
"$PYTHON" "$SKILL_DIR/scripts/despill_chroma_edges.py" \
  "$RUN_DIR/final/spritesheet-extended.png" \
  --output "$RUN_DIR/final/spritesheet-extended.png" \
  --webp-output "$RUN_DIR/final/spritesheet-extended.webp" \
  --chroma-key "$CHROMA_KEY" \
  --json-out "$RUN_DIR/qa/chroma-despill-extended.json"
```

Treat `qa/chroma-despill-extended.json` as the authoritative chroma result. When it has `ok: true` and `validate_atlas.py --require-v2` passes, accept the chroma result. Do not fail visual QA for perceived magenta fringe. Do not regenerate rows, repeat despill, adjust thresholds, or create another chroma-repair script. If either deterministic check fails, stop with a pipeline failure instead of retrying image generation.

This is the only chroma-cleanup invocation in the workflow. Never despill the intermediate 8×9 atlas. Clean rows `0-8` and the assembled look rows `9-10` together exactly once in the completed 8×11 atlas.

```bash
"$PYTHON" "$SKILL_DIR/scripts/validate_atlas.py" \
  "$RUN_DIR/final/spritesheet-extended.webp" \
  --json-out "$RUN_DIR/final/validation-extended.json" \
  --chroma-key "$CHROMA_KEY" \
  --require-v2
```

```bash
"$PYTHON" "$SKILL_DIR/scripts/make_contact_sheet.py" \
  "$RUN_DIR/final/spritesheet-extended.webp" \
  --output "$RUN_DIR/qa/contact-sheet-extended.png"
```

Create the focused direction QA sheet:

```bash
"$PYTHON" "$SKILL_DIR/scripts/make_direction_qa_sheet.py" \
  "$RUN_DIR/final/spritesheet-extended.webp" \
  --output "$RUN_DIR/qa/look-directions.png"
```

Create the blind horizontal-and-vertical axis challenge and keep its answer key away from the visual QA worker:

```bash
"$PYTHON" "$SKILL_DIR/scripts/make_direction_blind_qa_sheet.py" \
  "$RUN_DIR/final/spritesheet-extended.webp" \
  --output "$RUN_DIR/qa/direction-blind-pairs.png" \
  --answer-key "$RUN_DIR/qa/direction-blind-answer-key.json"
```

Give three fresh isolated workers only `qa/direction-blind-pairs.png`. Each row states whether to classify the horizontal or vertical axis. Every worker must classify A and B as `screen-left`, `screen-right`, `up`, `down`, or `ambiguous`, as appropriate. Hide degree labels, expected directions, the labeled direction sheet, the answer key, and other workers' verdicts. Write their classifications separately, then combine them by strict per-cell majority:

```bash
"$PYTHON" "$SKILL_DIR/scripts/combine_direction_blind_verdicts.py" \
  --verdicts "$RUN_DIR/qa/direction-blind-verdicts-1.json" \
  --verdicts "$RUN_DIR/qa/direction-blind-verdicts-2.json" \
  --verdicts "$RUN_DIR/qa/direction-blind-verdicts-3.json" \
  --json-out "$RUN_DIR/qa/direction-blind-verdicts.json"
```

Apply the hidden answer key only to the consensus verdict:

```bash
"$PYTHON" "$SKILL_DIR/scripts/validate_direction_blind_verdicts.py" \
  --answer-key "$RUN_DIR/qa/direction-blind-answer-key.json" \
  --verdicts "$RUN_DIR/qa/direction-blind-verdicts.json" \
  --json-out "$RUN_DIR/qa/direction-blind-validation.json"
```

The hidden answer key contains seven horizontal pairs and seven vertical pairs. The cardinal pairs (`000` vs `180` and `090` vs `270`) are hard gates: a mismatch or ambiguous majority keeps validation at `ok: false`. All intermediate pairs are review gates: mismatches, same-direction votes, and ambiguous majorities are preserved as warnings while validation remains `ok: true`. The blind pass is mandatory. By default, resolve intermediate warnings through labeled normal-size loop review instead of repeated regeneration.

### Blind Review Severity Resolution

After receiving a blind or final visual QA `pass`/`fail` result:

1. If it passes, continue immediately.
2. If it fails, inspect the worker's semantic reasons, repair note, labeled direction sheet, `qa/direction-semantics.json`, and `qa/look-continuity.json` before regenerating anything.
3. Classify the failure as `major` or `minor`:
      - `major`: Wrong or ambiguous cardinal. Labeled normal-size review shows a wrong principal quadrant or visible reversal. Other major defects include conspicuous snaps, scale pops, identity changes, broken attachments, clipping, interior seams/holes, or deterministic validation failures.
      - `minor`: Exact pupil or nose placement differs from the numerical ideal, or a near-vertical horizontal cue is subtle. Isolated reviewers disagree or return `ambiguous`. An intermediate blind majority conflicts, but the labeled ordered loop still reads correctly. Continuity metrics warn without a visible defect.
4. Repair major failures. Minor failures may be overridden and the installation pipeline continues.
5. Record every override in `qa/blind-review-resolution.json`. Include `decision: "accept"`, `severity: "minor"`, and the failed checks. Include the labeled/continuity evidence that makes them acceptable. Record `reviewed_by: "parent"` or `"user"`. Never override a major failure.

An override is a deliberate visual judgment, not a way to silence missing evidence. Keep all final QA artifacts: the blind sheet, consensus verdicts, validation output, labeled semantics, continuity report, and resolution file.

Measure adjacent direction continuity:

```bash
"$PYTHON" "$SKILL_DIR/scripts/measure_direction_continuity.py" \
  "$RUN_DIR/final/spritesheet-extended.webp" \
  --json-out "$RUN_DIR/qa/look-continuity.json"
```

Visually QA `qa/contact-sheet-extended.png`, `qa/look-directions.png`, and `qa/look-continuity.json` before accepting. Inspect the 16 normal-size look cells as an ordered loop, not only as isolated stills. For every direction label, compare the expected direction with the visible gaze/body direction. Record `pass`, `warning`, or `fail` in `qa/direction-semantics.json`.

Reject only the hard failures in the Direction Acceptance Policy. Record subtler semantic or metric concerns as warnings. Accept them when the normal-size loop stays cohesive, readable, visually pleasing, and preserves identity.

If a blind or final visual QA worker returns `fail`, apply Blind Review Severity Resolution before queuing a repair. Continue packaging when the failure is minor and `qa/blind-review-resolution.json` records the accepted override.

Only after all deterministic and visual QA passes, package the approved extended spritesheet as a v2 pet. `spriteVersionNumber: 2` is mandatory. Without it the app defaults to the 9-row v1 contract and rejects the 2288-pixel-tall asset.

```bash
PET_ID=$(jq -r '.pet_id' "$RUN_DIR/pet_request.json")
DISPLAY_NAME=$(jq -r '.display_name' "$RUN_DIR/pet_request.json")
DESCRIPTION=$(jq -r '.description' "$RUN_DIR/pet_request.json")
PET_DIR="${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID"
mkdir -p "$PET_DIR"
cp "$RUN_DIR/final/spritesheet-extended.webp" "$PET_DIR/spritesheet.webp"
jq -n --arg id "$PET_ID" --arg displayName "$DISPLAY_NAME" --arg description "$DESCRIPTION" \
  '{id: $id, displayName: $displayName, description: $description, spriteVersionNumber: 2, spritesheetPath: "spritesheet.webp"}' \
  > "$PET_DIR/pet.json"
```

Write `qa/run-summary.json` after packaging:

```bash
jq -n --arg run_dir "$RUN_DIR" --arg spritesheet "$RUN_DIR/final/spritesheet-extended.webp" --arg validation "$RUN_DIR/final/validation-extended.json" --arg chroma_despill "$RUN_DIR/qa/chroma-despill-extended.json" --arg contact_sheet "$RUN_DIR/qa/contact-sheet-extended.png" --arg direction_sheet "$RUN_DIR/qa/look-directions.png" --arg direction_semantics "$RUN_DIR/qa/direction-semantics.json" --arg blind_direction_validation "$RUN_DIR/qa/direction-blind-validation.json" --arg blind_review_resolution "$RUN_DIR/qa/blind-review-resolution.json" --arg continuity "$RUN_DIR/qa/look-continuity.json" --arg review "$RUN_DIR/qa/review.json" --arg package "$PET_DIR" '{ok: true, spriteVersionNumber: 2, run_dir: $run_dir, spritesheet: $spritesheet, validation: $validation, chroma_despill: $chroma_despill, contact_sheet: $contact_sheet, direction_sheet: $direction_sheet, direction_semantics: $direction_semantics, blind_direction_validation: $blind_direction_validation, blind_review_resolution: $blind_review_resolution, continuity: $continuity, review: $review, package: $package}' > "$RUN_DIR/qa/run-summary.json"
```

After all QA and packaging succeed, keep these files and directories:

- `pet_request.json`.
- `final/spritesheet-extended.webp`.
- `final/validation-extended.json`.
- `qa/chroma-despill-extended.json`.
- `qa/contact-sheet-extended.png`.
- `qa/look-directions.png`.
- `qa/direction-semantics.json`.
- `qa/direction-blind-pairs.png`.
- `qa/direction-blind-answer-key.json`.
- `qa/direction-blind-verdicts.json`.
- `qa/direction-blind-validation.json`.
- `qa/blind-review-resolution.json` when an override was used.
- `qa/look-continuity.json`.
- `qa/previews/`.
- `qa/review.json`.
- `qa/run-summary.json`.
 Remove prompts, layout guides, generated row strips, extracted frames, PNG intermediates, the 8x9 intermediate atlas, and the imagegen job manifest. Retain these files if the user wants debug artifacts.

## Lightweight Visual Workers

Use lightweight subagents for image-heavy work by default. This limits each `$imagegen` rollout to one selected image. It keeps contact-sheet vision payloads out of the parent thread and reduces cost. The complete v2 contract still applies.

## Subagent Delegation

Use lightweight workers unless the user specifically prohibits delegation.

Parent responsibilities:

- run the brand discovery worker before preparation when the user provides a bare brand/product/company/prospect name
- prepare the run and inspect `imagegen-jobs.json`
- Assign the base job and all standard rows to lightweight workers. Also assign the four-cardinal strip, coherent look rows, blind direction QA, and final contact-sheet QA to lightweight workers.
- copy selected worker outputs into their decoded paths and mark jobs complete in `imagegen-jobs.json`
- create `references/canonical-base.png` from the selected base output
- run the approved `running-left` mirror derivation when appropriate
- write the pet-specific look mechanics plan after standard-row QA
- approve the cardinal semantics and compose `decoded/look-anchors-approved.png`
- make immediate deterministic registration mandatory, post-registration edge QA, and labeled semantic QA after each coherent look-row generation
- run deterministic v2 assembly, packaging, repair regeneration, and cleanup

Base worker responsibilities:

- handle only the `base` job
- read `prompts/base-pet.md` and use any listed reference images
- use `$imagegen` only
- Use any compact brand inspiration line in the prompt as broad visual/personality guidance. Do not copy logos, readable marks, UI screenshots, slogans, or text.
- return only `selected_source=/absolute/path/to/selected-output.png` and `qa_note=<one sentence>`

Row worker responsibilities:

- handle exactly one row job
- read the row prompt and use all listed input images
- use `$imagegen` only. Do not draw, edit, tile, or synthesize sprites locally
- perform a quick visual sanity check for frame count, identity, chroma background, spacing, clipping, and detached effects
- Enforce the row prompt's transparency and effects rules. Prohibit detached effects, wave marks for `waving`, and speed lines or dust for directional running rows. Prohibit literal foot-running for the non-directional `running` row. Use attached opaque sprite-like tears/smoke/stars only when the state prompt gives permission.
- For a `look-row-strip`, synthesize the complete row as one coherent family from the approved cardinals. Never restyle individual cells independently.
- For a `look-row-strip`, make sure that eight separate pose groups appear in the required order. Reject overlap or outer-canvas clipping. Deterministic assembly owns exact cell crops, one shared scale and baseline, centering, and final-cell edge validation.
- return only `selected_source=/absolute/path/to/selected-output.png` and `qa_note=<one sentence>`

Blind direction QA worker responsibilities:

- Inspect only `qa/direction-blind-pairs.png`. Do not supply the labeled direction sheet, atlas, prompt, degree order, prior verdicts, or hidden answer key.
- Classify A and B independently for each pair on the sheet's named axis. Use `screen-left`, `screen-right`, `up`, `down`, or `ambiguous`. Use visible pupils, nose, face surface, head turn, or the pet's natural direction feature.
- never infer from pair order. Use `ambiguous` honestly when the requested axis is unreadable. Cardinal ambiguity blocks packaging. Intermediate ambiguity becomes labeled-review evidence.
- never inspect or receive another blind worker's classifications. The parent combines exactly three isolated verdict files with `combine_direction_blind_verdicts.py`
- return JSON-ready pair classifications only. Do not edit files or inspect unrelated artifacts

Final visual QA worker responsibilities:

- inspect the standard and extended contact sheets, direction QA sheet, row GIFs, semantic verdicts, continuity results, and v2 validation
- make sure that all 11 rows match the Codex app contract and the same pet identity
- return a compact result: `visual_qa=pass` or `visual_qa=fail`, plus row-specific repair notes when failing
- do not edit files, queue repairs, package, or clean up

Model choice for workers:

- Prefer a smaller capable model for brand discovery, since it returns a compact research brief rather than doing orchestration.
- Prefer a smaller capable model for visual workers, such as `gpt-5.4-mini` with medium reasoning, when model override is available.
- Use the parent/default model only for orchestration or when a smaller worker model is unavailable.
- When at least three independent jobs are ready and capacity is sufficient, keep three generation workers active. Fill each slot when its worker finishes. Use fewer workers when dependencies expose fewer jobs. Run final visual QA as a single worker after deterministic image processing. Close workers after their result has been consumed.
- Once `look-cardinals` passes, start row 9 immediately. Start row 10 only after row 9 passes deterministic registration, post-registration edge, semantic, and continuity QA. Give row 10 the completed row 9 strip as continuity evidence.

Use this base worker prompt:

```text
Generate the hatch-pet base image.

Run dir: <absolute run dir>
Job id: base
Prompt file: <absolute base prompt file>
Input images:
- <absolute path> — <role>

Use $imagegen only. Read the base prompt and attach every listed input image. If the prompt contains brand inspiration, use it only as broad mascot-safe guidance; do not copy logos, readable marks, UI screenshots, slogans, or text. Before returning, visually check that the result is one centered full-body pet on a flat chroma background, with no text, scenery, shadows, or detached effects.

Do not edit manifests, copy into decoded, mark jobs complete, generate rows, run image-processing scripts, repair, package, or open unrelated files.
Do not include Markdown image previews, base64, or extra attachments in the final response.

Return exactly:
selected_source=/absolute/path/to/selected-output.png
qa_note=<one sentence>
```

Use this cardinal-strip worker prompt:

```text
Generate one hatch-pet four-cardinal anchor strip.

Run dir: <absolute run dir>
Job id: look-cardinals
Prompt file: <absolute prompt file>
Input images:
- <absolute path> — <role>

Use $imagegen only. Read the cardinal-strip prompt and attach every listed input image. Read `qa/look-mechanics.md`. Screen-left and screen-right are viewer/image coordinates, never character-relative coordinates. Before returning, verify all four slots in order without relying on their labels: for a face, cite the nose-tip and pupil positions relative to the head center; for other pets, cite the natural aiming feature. Any ambiguous cardinal fails the strip.

Do not edit manifests, copy files, generate rows, assemble, package, or inspect unrelated files. Do not include image previews or attachments in the final response.

Return exactly:
selected_source=/absolute/path/to/selected-output.png
qa_note=<one sentence with concrete landmark evidence for all four cardinals>
```

Use this row worker prompt:

```text
Generate one hatch-pet row.

Run dir: <absolute run dir>
Row id: <row-id>
Prompt file: <absolute prompt file>
Retry prompt file: <absolute retry prompt file>
Input images:
- <absolute path> — <role>
- <absolute path> — <role>

Use $imagegen only. Read the row prompt and attach every listed input image. For a `look-row-strip` job, also read and obey `qa/look-mechanics.md`; use the approved cardinal strip for direction meaning and draw all eight cells together as one coherent family with even intermediate steps. Never paste, reuse, or independently restyle individual cells. If imagegen returns Bad Request, retry once with the retry prompt and the same input images.

Before returning, visually check: exact frame count, same pet identity as canonical base, flat chroma background, complete separated unclipped poses, and no detached effects or guide marks. For a `look-row-strip`, verify there are eight separated pose groups in the required left-to-right order, neighboring poses do not overlap, no foreground is cropped at the outer canvas edge, and the generated family keeps a consistent scale and baseline. Exact cell cropping, shared-scale normalization, recentering, and final-cell edge validation happen deterministically after generation. The prompt's transparency and effects rules are mandatory: no detached effects, no wave marks for `waving`, no speed lines or dust for directional running rows, no literal foot-running for the non-directional `running` row, and only attached opaque sprite-like tears/smoke/stars when allowed by the state prompt.

Do not edit manifests, copy into decoded, mark jobs complete, mirror rows, run image-processing scripts, repair, package, or open unrelated files.
Do not include Markdown image previews, base64, or extra attachments in the final response.

Return exactly:
selected_source=/absolute/path/to/selected-output.png
qa_note=<one sentence>
```

Use this blind direction QA worker prompt in a fresh worker that has not seen the labeled direction sheet. Spawn it without prior conversation context when the worker system supports context isolation (for example, `fork_turns="none"`):

```text
Classify one required gaze axis in an unlabeled hatch-pet A/B challenge.

Blind sheet: <absolute run dir>/qa/direction-blind-pairs.png

Inspect only this sheet. Do not open the atlas, labeled direction sheet, prompts, prior QA, degree order, answer key, or any other file.

Each row contains two normal-size pet cells labeled A and B and identifies the axis to judge. For a horizontal row, classify each cell as exactly `screen-left`, `screen-right`, or `ambiguous`. For a vertical row, classify each cell as exactly `up`, `down`, or `ambiguous`.

Judge only what is readable at the displayed pet size. Use visible landmarks such as pupils, nose tip relative to head center, face surface, head turn, eyelids, or the pet’s natural aiming feature. If the requested axis is not definite without enlarging or guessing, classify it as `ambiguous`; do not invent confidence.

Do not infer from A/B order. If A and B point the same way, report the same classification; do not force one left and one right.

Return exactly one JSON object and nothing else:
{"pairs":[{"pair":"horizontal-1|vertical-1","A":"screen-left|screen-right|up|down|ambiguous","B":"screen-left|screen-right|up|down|ambiguous","reason":"short landmark evidence"}]}

Include every pair shown in the sheet.
```

Use this final visual QA worker prompt:

```text
Visually QA one finalized hatch-pet contact sheet.

Run dir: <absolute run dir>
Contact sheet: <absolute run dir>/qa/contact-sheet.png
V2 contact sheet: <absolute run dir>/qa/contact-sheet-extended.png
Focused direction QA sheet: <absolute run dir>/qa/look-directions.png
Direction semantics JSON: <absolute run dir>/qa/direction-semantics.json
Blind direction validation JSON: <absolute run dir>/qa/direction-blind-validation.json
Look continuity JSON: <absolute run dir>/qa/look-continuity.json
Preview dir: <absolute run dir>/qa/previews
Review JSON: <absolute run dir>/qa/review.json
V2 validation JSON: <absolute run dir>/final/validation-extended.json

Inspect the contact sheet and the preview GIFs visually. Confirm the same pet identity, style, palette, silhouette, face, proportions, and props across all rows:
0 idle, 1 running-right, 2 running-left, 3 waving, 4 jumping, 5 failed, 6 waiting, 7 running, 8 review.

Require `qa/direction-blind-validation.json` to have `ok: true`, or require an explicit accepted minor override in `qa/blind-review-resolution.json`. Cardinal mismatches or ambiguity are major and block packaging. For intermediate warnings or a worker-level fail, inspect the labeled normal-size pose and ordered loop; accept when the issue is minor and there is no wrong-quadrant pose or reversal.

Inspect the 16 direction cells as a labeled ordered loop against the neutral frame and review `qa/look-continuity.json`. Produce a `pass`, `warning`, or `fail` semantic verdict for every expected direction: `000 up`, `022.5 up-right`, `045 up-right`, `067.5 up-right`, `090 right`, `112.5 down-right`, `135 down-right`, `157.5 down-right`, `180 down`, `202.5 down-left`, `225 down-left`, `247.5 down-left`, `270 left`, `292.5 up-left`, `315 up-left`, and `337.5 up-left`. Record separate horizontal and vertical landmark evidence for every diagonal. Fail wrong or ambiguous cardinals, labeled wrong-quadrant poses, and visible reversals. Record blind uncertainty on intermediate poses as warnings when labeled review and loop context confirm the intended direction.

Fail rows with identity drift, missing/blank frames, copied guide marks, white/nontransparent backgrounds, cropped bodies, slot overlap, detached effects, shadows/glows/smears/dust, motion that does not match the row state, unintended size popping, wrong facing direction, reversed or non-alternating gait, or idle loops that are effectively static. Judge chroma only on the cleaned extended contact sheet, not the pre-cleanup standard contact sheet. Do not fail or retry a row for magenta/chroma fringe after the final despill report and v2 atlas validation pass; those deterministic results are authoritative.

Do not edit files, queue repairs, package, clean up, or inspect unrelated files.

Return exactly:
visual_qa=pass|fail
qa_note=<one sentence summary>
direction_semantics=<semicolon-separated labels with pass/warning/fail and short visual reason>
review_warnings=<semicolon-separated accepted warnings, or none>
repair_rows=<comma-separated row ids, or none>
repair_notes=<short row-specific notes, or none>
```

## Repair Workflow

If frame inspection or final visual QA fails, read `qa/review.json`. Regenerate the smallest failed row. Copy its replacement into the same decoded output path. Keep the job complete with the new `source_path` and `completed_at`. Repair the failed row, not the whole sheet.

## Rules

- Keep `$imagegen` as the primary generation layer.
- For brand/product/company/prospect requests without a concrete avatar description or reference image, run brand discovery before base generation. Pass only the compact brief into the run.
- Use `$imagegen` as the only visual generation layer. Do not invoke image APIs, image CLIs, local raster generators, or one-off generation scripts from this skill.
- Keep reference images attached/visible for `$imagegen` whenever the chosen path supports references.
- Attach the row's `references/layout-guides/<state>.png` image to every row-strip job as a layout-only guide. Reject outputs that copy guide pixels.
- By default, use lightweight visual workers for base generation, row-strip generation, and final contact-sheet QA. The parent owns manifest updates, deterministic image scripts, packaging, and cleanup.
- Generate every normal visual job with `$imagegen`: base plus all row strips that are not explicitly approved `running-left` mirror derivations.
- Treat only the base job as eligible for prompt-only generation. Every row job must attach its listed grounding images.
- Generate `running-right` before deciding whether `running-left` can be mirrored.
- When `running-left` is mirrored, preserve frame order and timing semantics. Use the deterministic script. Do not mirror an entire strip as one image.
- Generate `waiting`, `running`, `failed`, `review`, `jumping`, and `waving` as separate rows. Do not derive or reuse them from another state. Each state has distinct app semantics.
- Generate look row 9 directly from the approved cardinal strip. Generate row 10 only after row 9 passes deterministic registration and post-registration edge QA. Row 9 must have no semantic or continuity hard failure. Reviewed warnings do not block row 10. Both rows attach the cardinal strip, and row 10 must also attach completed row 9.
- Final look rows must each originate from one coherent 8-frame row generation. Individually generated repair cells may never be copied into the final atlas.
- If one look direction fails, strengthen the containing row's direction instructions and resynthesize the complete row. Do not patch the final cell directly, even when deterministic assembly supports individual-cell input.
- Register each coherent look row deterministically. Immediately after generation, run final-cell edge diagnostics and explicit labeled semantics. Complete these before expensive final atlas assembly. Run blind horizontal-and-vertical axis QA as soon as both coherent rows exist.
- Never substitute locally drawn, tiled, transformed, or code-generated row strips for missing `$imagegen` outputs.
- Only mark a visual job complete after its selected output has been copied into the decoded output path.
- Never mark a failed coherent row, diagnostic iteration, or one-off repair cell as packaging eligible.
- Do not rely on generated images for exact atlas geometry. Use this skill's deterministic image scripts.
- Use the chroma key stored in `pet_request.json`. Do not force a fixed green screen.
- Keep the pet's silhouette, face, materials, palette, style, and props consistent across all rows.
- Treat visual identity or style drift as a blocker even when deterministic validation has no errors.
- Treat a contact sheet that shows cropped references, repeated tiles, white cell backgrounds, or non-sprite fragments as failed.
- Reject preview GIFs with extraction-induced size changes, reversed directional timing, incorrect facing direction, or inert idle loops.
- Apply the Direction Acceptance Policy to look cells. Cardinals are hard gates. Intermediate blind uncertainty is a warning unless labeled normal-size review shows a wrong quadrant, missing axis, or loop reversal.
- Treat missing explicit per-direction semantic gaze review as failed. This applies even when the focused QA sheet and continuity JSON exist.
- Treat missing `qa/direction-semantics.json` as failed. The file must include every expected direction with `verdict`, `expected`, `observed`, and `reason` fields. Packaging must have no `fail` verdicts. Reviewed `warning` verdicts are allowed.
- Treat missing or failed `qa/direction-blind-validation.json` as failed. Each of the three isolated blind reviewers must see only the randomized A/B sheet. Never show degree labels, the answer key, or another verdict. Cardinal mismatches or ambiguity fail validation. Intermediate mismatches or ambiguity remain review warnings.
- Never assign blind A/B classification to a worker that has seen the labeled direction sheet or direction prompts. Label-conditioned classification is not independent evidence.
- Do not let the parent agent self-approve a repaired look direction. Run an independent final visual QA worker on `qa/look-directions.png` or ask the user to inspect it before packaging.
- After an independent blind or final QA failure, the parent may override only a minor issue. Follow Blind Review Severity Resolution. Record the evidence in `qa/blind-review-resolution.json`. Never override a major failure.
- For humanoid cardinal verdicts, record concrete screen-coordinate landmark evidence in `qa/direction-semantics.json`. Intermediate verdicts may use holistic head, face, posture, and ordered-loop evidence. Exact pupil or nose placement is advisory, not mandatory.
- Fail look rows that rotate, skew, or tilt the complete sprite to imitate gaze. An exception applies only to a literal rotating-object pet with explicit justification in the look mechanics decision.
- Treat pupil-only motion or underused natural mechanics as a warning. This exception does not apply if it visibly breaks identity, direction meaning, or loop cohesion.
- Treat adjacent continuity metrics as review evidence. Fail only when visual QA shows a conspicuous snap, pop, registration jump, identity change, broken silhouette, or semantic discontinuity.
- Fail rows with forbidden detached effects, shadows, glows, smears, dust, landing marks, wave marks, speed lines, or motion trails. Handle chroma-key-adjacent generation artifacts only through the single deterministic despill pass. After that pass reports success, never trigger image retries for those artifacts.
- Treat `qa/review.json` errors as blockers. Examine warnings visually.

## Acceptance Criteria

- Final atlas is PNG or WebP, exactly `1536x2288`, and based on `192x208` cells. The `1536x1872` standard atlas is intermediate-only.
- `pet.json` must contain `spriteVersionNumber: 2`. The extended despill report must have `ok: true`. The packaged spritesheet must pass `validate_atlas.py --require-v2` with the run's chroma key. These deterministic results close chroma QA. No separate visual chroma-fringe gate or image retry is allowed.
- Used cells are non-empty and unused cells are fully transparent.
- Atlas follows the row/frame counts in `references/animation-rows.md`.
- Before look-row generation, extract the four-cardinal strip deterministically. Its clipping report must pass. Obtain semantic approval for all four anchors.
- Both coherent look rows must use `decoded/look-anchors-approved.png` as the direction basis. Interpolate all intermediate directions as even 22.5-degree steps. Preserve the fixed clockwise order.
- Each coherent source row must pass deterministic pose-group registration, final-cell edge diagnostics after registration, and labeled per-direction semantic QA. These checks precede final atlas assembly. Run blind horizontal-and-vertical axis QA after both rows exist.
- Contact sheet and per-row motion previews have been produced and inspected by a lightweight visual QA worker.
- A focused neutral-plus-16-directions QA sheet has been produced and inspected before packaging.
- A randomized unlabeled horizontal-and-vertical axis pair sheet has been classified by three isolated blind workers and combined by strict majority. Both cardinal pairs pass. `qa/direction-blind-validation.json` has `ok: true`, or a worker-level/intermediate failure has an accepted minor resolution in `qa/blind-review-resolution.json` backed by labeled and continuity evidence.
- Each expected direction must have an explicit `pass`, `warning`, or `fail` semantic verdict. Include horizontal and vertical axis evidence where applicable. Leave no wrong cardinal, labeled wrong-quadrant pose, or visible reversal.
- `qa/direction-semantics.json` must record verdicts for all 16 directions from an independent visual QA worker or explicit user inspection. Include review notes for accepted warnings.
- Review `qa/look-continuity.json`. Accept metric warnings when the normal-size ordered loop has no visible snap, pop, identity change, or semantic discontinuity.
- `qa/review.json` has no errors.
- Row-by-row review shows the animation cycles are complete enough for the Codex app.
- Motion previews do not show unintended size popping, reversed directional cadence, or wrong row semantics.
- Look directions follow the fixed clockwise order and form a cohesive, readable loop at normal pet size. Cardinals must be unmistakable. Intermediate blind uncertainty is acceptable as a reviewed warning when labeled normal-size review shows the intended direction and the loop does not reverse.
- Non-pixel styles are accepted when readable at pet size and consistent across rows.
- `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/pet.json` and `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/spritesheet.webp` are staged together for custom pets.
