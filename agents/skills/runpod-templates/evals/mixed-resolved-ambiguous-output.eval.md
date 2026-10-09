# Apply verified metadata and still output when another model is ambiguous

## Prompt

This UI workflow references two missing models. One has an exact publisher file and hash;
the other has two credible exact-filename candidates with no evidence distinguishing them.
Repair it as far as you safely can.

## Expected behavior

The agent adds metadata only for the verified model and omits the ambiguous model from the
temporary manifest. It does not pause when it discovers the ambiguity. First, run the finalizer with `--allow-unresolved` to produce one partial repaired JSON. Attach its verified record and preserve its ambiguous loader selection.

Starts the final handoff with the one full absolute `Fixed workflow` path. States that one model remains unresolved. Briefly names the model with added download information. Presents the two possible files and one consolidated choice question. It
does not provide inventory, manifest, normalized JSON files, hashes, or long URLs.

## Assertions

- Creates and reports the partial workflow before asking the ambiguity question.
- Applies the verified record and does not apply either ambiguous candidate.
- Names the verified model without showing a technical table by default.
- (handoff-contract assertions owned by always-output-workflow.eval.md)
