Outcome: done
## Done

Audited the previous search record, which contained no retained implementation or raw log—only the claimed counts in the prior handoff.  Its endpoint classification was reversed: `C(27,k-2)` is the class that **deletes both endpoints**, not the frozen class.  I wrote a reproducible Bun implementation and retained its JSON output at `.terramind/swarm/codex-witness-pair/search-wider-golomb-ruler-exchan-654pt-c4/golomb-audit.ts` and `output.json`.

The audit keeps coordinates in the published seed's frame and, for each core, completes in the ascending integer interval `[max(core)-622, min(core)+622]`.  It skips only a core whose retained span already exceeds 622.  Thus the 623-seed frozen class is exactly the cores retaining both endpoints (`C(27,k)`), while all endpoint-deleting classes are enumerated.

The required controls passed:

* Completing `[0,1,4]` to four marks has one leaf at cap 6, `[0,1,4,6]`, and zero at cap 5.
* Recovering both endpoints from the 27-mark interior at cap 623 has one leaf, the published 623 ruler.  This explicitly exercises the both-endpoints-removed class.

The one-core bounded run exited 0 in 14,910 ms, well inside the 30-minute limit.  No 29-mark ruler of span at most 622 was found.  The asserted eligible-core totals `C(29,k)-C(27,k)` were fully enumerated and equal the completed counts:

* delete 3: 729/729; endpoint classes left 351, right 351, both 27; frozen retaining-both count 2,925; leaves 27.
* delete 4: 6,201/6,201; endpoint classes left 2,925, right 2,925, both 351; frozen retaining-both count 17,550; leaves 351.
* delete 5: 38,025/38,025; endpoint classes left 17,550, right 17,550, both 2,925; frozen retaining-both count 80,730; leaves 2,926.

All stages exhausted: there is no unfinished core in any 623 stage.  The published 28-mark length-585 seed was also exhaustively covered at cap 622 with the required extra insertion to reach 29 marks: delete 0 1/1, delete 1 28/28, delete 2 378/378, delete 3 3,276/3,276; every stage produced zero completion leaves and no unfinished core.

I also reran the Frontier baseline commands:

`bun frontier check attempts/witness.golomb-ruler-29/20261118-agrim26-830b60`

returned `verified: Valid witness for witness.golomb-ruler-29 with value 623; ties the best known (Rokicki and Dogon, Golomb ruler dataset).`

`bun frontier diagnose attempts/witness.golomb-ruler-29/20261118-agrim26-830b60`

returned `valid: yes` and `result: ties the best known value`.  No improved candidate existed, so no candidate was normalized or submitted for Frontier checking.

The prescribed practice command was attempted before the audit.  It is blocked by an inherited broken attempt outside this task: `bun frontier pick --practice` fails with `attempts/erdos595.erdos-595.variants.k4-not-cliquefree/20261118-agrim26-059b2c/attempt.yaml: cannot read: ENOENT`.  The Golomb checker itself remains operational as shown above.

## Deviations

The prior implementation and logs were not retained, so the audit reconstructs the search rather than patching old code.  The complete finite search ended early because every required core was exhausted; it did not consume the 30-minute maximum.  No changes were made to attempt declarations, no submission command was run, and no PR was created, updated, pushed, or merged.

## Concerns

This is exhaustive only for the stated deletion/recompletion neighborhoods at cap 622; it is not a proof that no shorter 29-mark Golomb ruler exists.

Provenance is inconsistent across routing and recorded metadata.  Observed in this checkout: the existing attempt YAML and commit `4725cd51` name `agrim26` and `gpt-5`; this cloud image has no `gh` executable, so it cannot independently observe a current GitHub login.  The lead's supplied routing context says the local `gh` login was `terramind-com` and the worker was configured as `gpt-6.2-sol-high` through Codex.  Those are routing/configuration claims, not evidence that the current execution used those identities; they should not be conflated with the observed historical commit and attempt metadata.

## Follow-ups

None.
