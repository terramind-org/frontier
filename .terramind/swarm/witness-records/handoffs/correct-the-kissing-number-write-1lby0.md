## Done

Corrected `attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f/attempt.yaml` and `writeup.md`. No search was run and no search scripts were changed.

Seven corrections (old wording → new wording):

1. Old: “The best saved numerical configuration had maximum pairwise cosine 0.5072124712612411” and “Its minimum angle was 59.52166841688265 degrees.” New: the claim uses the auditor's corrected claim in full below. The opening explains that this is the 604 with one point inserted and all points relaxed; one 34-second baseline-plus-random-point relaxation reaches the same value, so it is not evidence of closeness to 605. Random starts reach only about 0.543 to 0.544 at N = 603 to 605. The angle lead was removed.
2. Old: “1,322,820 exchange trials. None improved the best maximum cosine.” New: “Every exchange started from one of 64 holes of a single type, each with 51 points at cosine 1/sqrt(3). Removing at most six of them could not clear the rest, so this phase was structurally unable to succeed; the trial count measures repetition, not breadth.”
3. Old: “The full integer pool had 19,034 directions”. New: “An enlarged pool had 19,034 directions: the 4,284 earlier ones plus the integer vectors of eight selected norm-36 patterns. It omits the 1,536 backbone-compatible integer vectors of pattern (3,3,3,2,2,1).”
4. Old: “its allocation pattern could exceed the 3 GB memory cap” and “Resource compliance for that aborted run cannot be asserted.” New: “Its log shows it had already formed the dense 19,034-square float64 Gram matrix (2.90 GB) with its Boolean comparison (0.36 GB), so it very likely exceeded the 3 GB memory cap before it was stopped. The sampled RSS of 1,882,752 KiB is not a peak.”
5. Old: “Conflict-graph MILPs reported an optimum of 108 extension points for each pool” and “They do not bound configurations outside those pools.” New: the optimum applies “only with the 496-vector backbone held fixed”; the results do not bound configurations outside the pools or with the backbone free.
6. Old: trial and evaluation totals without the time to best. New: the hole phase reached 1/sqrt(3) at 0.06 s and never improved; the final relaxation reached its best at 220 s of 3,575 s. Earlier profiles plateaued at 733 s of 1,840 s and 151 s of 1,400 s.
7. Old: “The main launcher's recorded wait status is 145” followed by “It did not finish normally.” New: “The main launcher's recorded wait status is 145 = 128 + 17. Signal 17 is SIGSTOP on this macOS, so this reflects a stopped job; the main process's final termination status was not captured.” The guard records sending SIGTERM. The main process spent about 284 s paused during the two integer-pool runs.

Additional requested items 2–7:

- Exactness: added the 19,704 exactly tight pairs (inner product 18), zero slack, failed float export of the baseline, and need for exact reconstruction such as snapping to the configuration's Z[sqrt(2)] alphabet unless strict slack is obtained. Added that `diagnose` exits 0 on invalid witnesses: a success gate must read its output, not its exit code; the current gate relies on `exact_valid`.
- Scrub: the requested recursive local-path/personal-name grep found no matches before or after editing. Nothing needed removal, and no path fix or script edit was needed.
- Follow-ups in the writeup now begin with punctured-604 calibration and a lower or replacement exchange success gate (only 4 of 144 known-answer trials passed). They cover whole-blocker-set/cap replacement and m + 1 re-optimisation, freeing the backbone in the MILP, completing integer and mixed-coordinate pools, symmetry, other starting structures, exact reconstruction inside relaxation, and peak memory/true process exit status.
- Kept the title, `kind: writeup`, `rights: false` and `disclosure_complete: false` unchanged.
- Kept all disclosures and added `{ name: claude-opus-5-5, provider: anthropic, role: auditor }` in the existing YAML shape.
- Added “Independent audit”: a second model re-derived the baseline structure, confirmed every stage restores a punctured 604, calibrated relaxation at several sizes, checked export and MILP, recounted logs, and identified seven incomplete or overstated statements. It is explicitly an opinion backed by reruns, not a repository-verifier check.

Title in full:

> Hole/exchange and all-point Lp search from 604 points, 2 h, no 605 found

Claim in full:

> Failed two-hour local search around the published 604-point configuration; no valid 605-point configuration was found. The best numerical 605-point configuration (the 604 with one point inserted, all points relaxed) had maximum pairwise cosine 0.50721 (required <= 0.5). One 34-second relaxation from the baseline plus a random point reaches the same value, so this figure is not evidence that 605 is close to reachable. Its integer export was rejected. Exact configurations validated only at 604, tying the repository record. This writeup is not machine-checked and establishes no upper bound.

Verification: `bun install` completed (9 packages installed). `git diff --check` passed. `bun run check` passed typechecking and reported 426 pass, 1 skip, 0 fail (427 tests, 2426 assertions); it exited 1 only because all six swarm attempts have unconfirmed declarations. No Lean checks were needed; no Lean or checker code changed.

Verbatim output of `bun frontier check attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f` (exit 0):

```text
$ bun src/cli.ts check "attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Verbatim output of `bun frontier validate attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f` (exit 1):

```text
$ bun src/cli.ts validate "attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f"
attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

The brief names two handoff paths. Identical handoffs are committed at `handoffs/correct-kissing11.md` and `handoffs/correct-the-kissing-number-write-1lby0.md` under `.terramind/swarm/witness-records/` to satisfy both.

The exactness paragraph says scale-and-round cannot be relied on, rather than asserting that no numerical neighbour can ever round exactly. This preserves the audit's strict-slack exception and avoids an unsupported universal assertion. It reports the audit's rejected baseline export and requires exact reconstruction for a tight candidate.

## Concerns

None. No audit finding was contradicted by the materials reviewed. No independent search or numerical rerun was performed in this correction task.

## Follow-ups

None.
