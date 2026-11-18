Outcome: done
## Done

Ran a new one-core Golomb-ruler experiment on branch `swarm/frontier-cloud-codex-wide--search-nonlocal-golomb-construct-kidfh-c4`.  The retained reproducibility material is in `.terramind/swarm/frontier-cloud-codex-wide/search-nonlocal-golomb-construct-kidfh-c4/`:

* `golomb-block-shift.ts` (SHA-256 `fd788b7628efc757ffe8c922d67db268ae14f943b60275e1e828e5cfccf1f735`) is the exact search implementation.
* `block-shift-output.json` (SHA-256 `2bffdf38041babf422994286314b993029afa206a2b8752c6d281d3fef982274`) is its raw result, and `block-shift-time.txt` records its 28 ms wall time.
* `baseline-check.txt` and `baseline-diagnose.txt` record the Frontier controls; `repo-check.txt` records the final repository gate.

Primary-source control: downloaded `https://cube20.org/golomb/rulers-all-00.zip` (SHA-256 `46882140622d84b005b98423d293d44e156992850b59140994b2bfe63f3cad02`) and extracted every `29`-mark record of length at most 630.  The raw extraction (`dataset-29-lte630.txt`) has exactly one line, the established 623 ruler.  Thus the published data has no alternate length-623 or near-record 29-mark seed in that range; no translation/reflection inequivalence claim can be made.  The canonical (translation/reflection-minimized) SHA-256 of that sole seed is `14e0bd44eb9199e52b3007138180355bc43efdecd086b3d0807900771bd6286d`.

Created a disposable witness scaffold with both declarations left `false`, copied the published 623 seed, and ran:

```text
bun frontier check attempts/witness.golomb-ruler-29/20261118-agrim26-3db523
bun frontier diagnose attempts/witness.golomb-ruler-29/20261118-agrim26-3db523
```

Both controls passed: the check said `verified: Valid witness ... value 623; ties the best known`, and diagnosis reported `valid: yes`, `result: ties the best known value`.  The disposable scaffold was then removed; no attempt, declaration, submission, PR, or merge was created.

Pivoted to the specified contiguous-block move.  For every suffix beginning after a published gap of at least 40, the search tried every negative shift that preserves order and reduces the length to at most 622, then attempted every necessary one-mark repair.  A repair position is eligible only if it lies in every duplicated-difference conflict; the remaining core must be Golomb before every legal replacement is tested exactly.  Completed ranges were:

* cut 6, gap 47: deltas -1 through -46;
* cut 10, gap 52: -1 through -51;
* cut 16, gap 71: -1 through -70;
* cut 23, gap 61: -1 through -60;
* cut 24, gap 54: -1 through -53.

All 280 shifted states were invalid, and none admitted a one-mark repair position covering all collision classes (`repairableStates: 0` in every cut).  Therefore zero candidates reached Frontier checking.  The exact resume cursor is: `complete: cuts 6,10,16,23,24 (0-based suffix starts), delta range -1..-(gap-1), all repair positions implied by duplicated differences`.

Verification: `bun run check` completed after the disposable scaffold removal: 434 pass, 1 skip, 0 fail; repository validation ended `ok: 18618 problems, 0 attempts`.

## Deviations

The cloud image initially lacked Bun, so installed Bun 1.4.4 with the repository setup command and ran `bun install --frozen-lockfile`.  No alternate published 623/near-record seed existed in the selected source, so the assigned alternate-seed route was exhausted immediately and the search pivoted to the requested block-shift route.  The finite search took 28 ms rather than the 30-minute ceiling because all prescribed states were exhausted.

## Concerns

This result excludes only the five large-gap suffix-shift neighborhoods and one-mark repairs specified above.  It is not evidence that a shorter 29-mark Golomb ruler does not exist.  The prior Golomb work visible in local history was `4725cd51`/`abb4db90` (endpoint exchange/audit); this experiment used a distinct block-shift neighborhood.  PR numbers 56, 58, and 61 were not present in the fetched local refs, so they could not be independently inspected in this cloud run.

## Follow-ups

Try two-sided internal block shifts (which can search for inequivalent 623 seeds) before a wider multi-mark repair search; retain the canonicalization hash rule above to reject translations/reflections.
