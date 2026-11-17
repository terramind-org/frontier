## Done

C1: Old: “These trials used the supplied templates; they did not optimize their lengths or parameters.” New: with S(2)=4, S(3)=13 and S(4)=44, the 376, 109 and 33 templates give at most 1664, 1456 and 1458 respectively. None can reach 1697 with any base. These were reproductions; the 376 template reproduces the published 1664 partition up to colour relabelling. Only a new template could help. Old follow-up: “Weighted conflict search and other product-template parameters remain untried.” New: “New templates with larger m·S(k)+φ remain untried.” Clause-weighting is retained separately as a follow-up.

C2: Old: “I tried reflected placements of the original prefix at orders 1697, 1698, 1700, 1704 and 1712. No accepted extension emerged.” New: reflected placements of the original 1..537 at those orders were each UNSAT by unit propagation alone (0–1 conflicts, no decisions). The accompanying 1696 jobs fixed the unshifted baseline and are not matched controls.

C3: Old: each top-window UNSAT had a SAT control at 1696 with the same free positions; the 1250-window control returned SAT and passed diagnosis. New: both passages say phases were set to the baseline and the controls returned it unchanged, showing only that the encoding does not exclude the known solution.

Minor exit-status point: Old: “The final SAT controller and final local-search process both exited 0.” New: both printed their own `exit 0` end lines; shell exit statuses were not captured.

Minor repair-count point: Old: only the 25 later restricted target jobs were mentioned. New: also records the 287 stage-2 neighbourhood repair pairs, each control SAT and target UNSAT.

Minor local-start point: Old: “The final clean run made 112,873,492 moves over 113 restarts”. New: the final local-search run resumed from the best-6 colouring saved during the mixed two-process interval; the single-process run then made those moves and restarts.

Item 2: Added the auditor's independent encoding and certificate result, explicitly attributed to the auditor: at-least-one colour per integer, every triple clause, fixed-colour unit clauses, 11,879 variables and 5,044,483 clauses; CaDiCaL 3.1.0 UNSAT in 373.7 seconds, LRAT verified by lrat-check. Records the S(3)=13/S(4)=44 controls, different valid 1696 colouring, and undecided shorter prefixes at 300–600 seconds. Limits the result to extensions of the specified 1..446 colours and states that encoder and proof checker are not formally verified.

Item 3: The requested grep found one home-directory path, in run.sh line 2. Replaced that line with `cd "$(git rev-parse --show-toplevel)" || exit 2`. Repeated grep and a case-insensitive scan for the requester's name returned no matches. No other source file changed. Scholarly attribution to Rowley remains as required by the brief.

Item 4: Follow-ups now start with many six-colour bases near length 536 that first reproduce mirrored 1696 completions, then 1697 with mirror x → 1698 − x and without it; followed by cube-and-conquer for shorter prefixes, clause-weighting from other start points, and new templates.

Item 5: Kept the title and kind writeup. Made the claim's fixed prefix exact, added the independent LRAT result and the 1664 template ceiling. Both declarations remain false.

Item 6: Kept every existing disclosure entry and added claude-opus-5-5 / anthropic / auditor with the existing YAML shape.

Item 7: Added a four-sentence “Independent audit” section summarising reruns and the three corrected passages. It calls the audit an opinion backed by reruns, not a repository-verifier check. The writeup remains explicitly not machine-checked. No search or new result was run.

Title in full:

"Rowley-seeded SAT windows and tabu, 2 h, no extension; best 5 conflicts"

Claim in full:

"No valid seven-colour Schur partition beyond 1696 was found in a 119-minute-50-second wall-clock search. The best observed colouring at N=1697 has five monochromatic triples. CaDiCaL reported UNSAT with Rowley's colours fixed on integers 1 through 446 and all of 447..1697 free; an independent audit re-derived this result with a checked LRAT proof. The author's SAT length-1696 control returned Rowley's colouring unchanged with its phases set to that colouring. The product templates used cannot exceed 1664. This writeup is not machine-checked and supplies no upper bound on S(7)."

`bun install` succeeded. `git diff --check` passed. `bun run check`: typechecking passed; 426 tests passed, 1 skipped, 0 failed (427 tests, 34 files). Final validation exited 1 solely for unconfirmed declarations on all six swarm attempts, as expected by the design.

Verbatim output of `bun frontier check attempts/witness.schur-7/20261117-terramind-com-c8ca32` (exit 0):

```text
$ bun src/cli.ts check "attempts/witness.schur-7/20261117-terramind-com-c8ca32"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Verbatim output of `bun frontier validate attempts/witness.schur-7/20261117-terramind-com-c8ca32` (exit 1):

```text
$ bun src/cli.ts validate "attempts/witness.schur-7/20261117-terramind-com-c8ca32"
attempts/witness.schur-7/20261117-terramind-com-c8ca32/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

The brief names two handoff paths. Identical copies are committed at `.terramind/swarm/witness-records/handoffs/correct-schur7.md` and `.terramind/swarm/witness-records/handoffs/correct-the-schur-writeup-8v7ns.md` to satisfy both.

## Concerns

None. No disagreement with the audit. The expected declaration failures remain; nothing was submitted.

## Follow-ups

None.
