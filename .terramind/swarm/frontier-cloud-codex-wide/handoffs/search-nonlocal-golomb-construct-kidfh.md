Outcome: done
## Done

Ran a new one-core, measured Golomb repair experiment on branch `swarm/frontier-cloud-codex-wide--search-nonlocal-golomb-construct-kidfh-c5`, recovering commit `3f8f1f93` as the control. Reproducibility materials are in `.terramind/swarm/frontier-cloud-codex-wide/search-nonlocal-golomb-construct-kidfh-c5/`: both source programs, raw JSON outputs, timing logs, hashes, and `repo-check.txt`.

The recovered published 29-mark, span-623 seed has canonical SHA-256 `14e0bd44eb9199e52b3007138180355bc43efdecd086b3d0807900771bd6286d`. Its Frontier controls from c4 were retained: `frontier check` reported a valid witness at 623 tying the known value, and `frontier diagnose` reported `valid: yes`. No candidate was generated in this run, hence no new disposable scaffold or candidate check/diagnose was needed. Declarations remain false; no attempt, submission, PR, or merge was created.

Two-mark repair exhaustively covered the five c4 large-gap suffix-shift neighborhoods (cuts 6, 10, 16, 23, 24; 280 states). It deleted every unordered pair of marks, `C(29,2)=406`, yielding 113,680 exact 27-mark cores. All 113,680 were filtered because their retained differences were not distinct; feasible cores 0, exhausted insertion domains 0, unfinished cores 0, actual candidates 0. For a feasible core, the code would enumerate every pair of distinct coordinates in `[max(core)-622, min(core)+622]`, including negative/outside-endpoint coordinates, and verifies all old/new/mutual differences and final span. The two-mark code self-tested against a brute-force oracle on a 6-mark ruler and recovered planted missing marks `[4,10]` from `[0,1,5,9,12,17]`. Both exact and brute-force sets agreed.

Advanced to the requested three-mark layer. The collision-class prune completed all 1,023,120 triples (`280 * C(29,3)`) in 38 ms: every triple missed at least one duplicated-difference endpoint class, so no 26-mark core could be valid and no three-coordinate insertion domain existed. This is a conservative necessary-condition prune: a triple that misses a collision class cannot remove either endpoint of any colliding pair in that class. Counters: states 280, triples 1,023,120, pruned 1,023,120, cores filtered 0 after pruning, feasible 0, unfinished 0.

Measured runs: two-mark search 1,134 ms wall time (search's internal measurement 1,115 ms); three-mark screen 49 ms wall time (internal 38 ms), both exit 0, well below the 30-minute one-CPU cap. `bun run check` passed: 434 pass, 1 skip, 0 fail; validation: `ok: 18618 problems, 0 attempts`.

Exact resume cursor: complete all c4 cuts/deltas (`-1` through `-(gap-1)`), all 406 pair deletions per shifted state, and all 3,654 triple deletions per shifted state under the collision-class prune. The next unsearched repair layer is four deleted/insertion marks, or a different block-shift neighborhood.

## Deviations

None. The requested three-mark escalation was necessary because the two-mark domain exhausted; it ended far below the runtime ceiling because the duplicate-distance lower-bound prune excluded every triple before coordinate enumeration.

## Concerns

These negative results cover only the five inherited large-gap suffix shifts. They do not rule out a span-622 29-mark ruler, two-sided/internal shifts, or repairs of four or more marks. The three-mark screen is a necessary-condition rejection, not a complete four-or-more repair search. PRs 56, 58, and 61 remain unavailable in local refs; this search uses the c4 route and does not deliberately repeat endpoint-exchange work.

## Follow-ups

Search four-mark repair with a minimum hitting-set calculation over duplicated-difference pairs, or use a distinct internal/two-sided block shift with translation/reflection canonicalization before repairing.
