Outcome: done
## Done
Created `attempts/witness.golomb-ruler-29/20261118-agrim26-830b60` with `gpt-5:openai:author` and `bun:checker` credits; both submission declarations remain false.  The prescribed practice warmup was scaffolded and checked, but Lean is absent in this cloud image, so its output was `error: Lean is not installed here; CI will check this attempt`; the temporary warmup scaffold was removed before committing.

Copied the published 29-mark length-623 ruler into the witness and ran:

`bun frontier check attempts/witness.golomb-ruler-29/20261118-agrim26-830b60`

Output: `verified: Valid witness for witness.golomb-ruler-29 with value 623; ties the best known (Rokicki and Dogon, Golomb ruler dataset).`

`bun frontier diagnose` reported `valid: yes` and `result: ties the best known value`.

The one-core bounded exchange search exited 0 in 155,518 ms, with no candidate of length at most 622.  It used the required ascending insertion order and duplicate-difference/span pruning.  Controls: `[0,1,4]` completed at cap 6 (one completion leaf) and had no completion at cap 5; both endpoint-recovery controls at cap 623 completed (two leaves), recovering the fixture.  For the 623 seed at cap 622, eligible completed core counts were 3-deletions 3,627, 4-deletions 23,400, and 5-deletions 115,830.  The omitted counts—27, 351, and 2,925—are exactly the cores retaining both endpoints, which the brief required skipping; therefore no eligible unfinished core exists at any stage.  No completion leaf survived the pruning in these three stages.

The published 28-mark length-585 seed was then exhausted at cap 622: delete-0 1/1, delete-1 28/28, delete-2 378/378, delete-3 3,276/3,276.  No completion leaf survived pruning and no first unfinished core exists.  This finished well before the five-minute reservation became binding, so the search ended rather than idling.

## Deviations
The environment had no `bun`, so it was installed with the repository's setup command.  `gh` was also absent; the configured local Git identity (`agrim26`) was used as the actual scaffold login rather than inventing one.  The search exhausted its stated finite domain in about 2.6 minutes rather than consuming the entire 30-minute maximum.

## Concerns
This is only an exhaustive result for the specified deletion-and-completion neighborhoods and caps.  It is not evidence that no ruler shorter than 623 exists.  No improved candidate was available to normalize or rerun through Frontier.

## Follow-ups
None.
