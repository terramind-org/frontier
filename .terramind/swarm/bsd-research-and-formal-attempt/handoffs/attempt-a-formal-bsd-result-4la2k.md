Outcome: done
## Done
- Continued on branch `swarm/bsd-research-and-formal-attempt--attempt-a-formal-bsd-result-4la2k-c2` and extended `formal-attempt.md` with a source-pinned 389a1 rank-two case study.
- Verified the requested label/model against LMFDB: 389a1 is `y^2 + y = x^3 + x^2 - 2*x`, conductor 389. The rational points `(0,0)` and `(1,0)` satisfy the equation by direct substitution.
- Recorded the reproducible Magma command published in the handbook: `E := EllipticCurve("389a1"); time rank, gens, sha := MordellWeilShaInformation(E);`. The published transcript reports 2-Selmer rank 2, two independent points, and after 2-descent `2 <= Rank(E) <= 2`; it also says 2-covering point search was bounded by height 100. This is the documented unconditional descent-plus-independence route to algebraic rank 2; its numerical analytic-rank line is not needed for that interval. No BSD assumption is used for the descent conclusion.
- Separated analytic bounds from algebraic rank. Magma's modular-symbol example reports `LRatio(M,1) = 0`; the LMFDB L-function record gives sign `+1`. Treating those exact modular-symbol and functional-equation data as inputs gives `ord_{s=1} L(E,s) >= 2` (even order and central vanishing). The printed floating-point leading coefficient and heuristic analytic-rank output do not prove order at most 2. Using algebraic rank 2 to infer exact analytic order 2 would assume the weak BSD equality.
- First non-generalizing step: obtaining and certifying this particular curve's 2-Selmer upper bound and two independent points. It does not give a general analytic-to-arithmetic implication, nor an upper bound for analytic order. No strong BSD normalization is used.
- Exact environment probes: `command -v magma` and `command -v sage` returned no path; `command -v bun` returned `/usr/local/bin/bun`. Therefore the Magma command was documented from the published handbook but not locally run. No Frontier attempt, checker run, or formal result was created.
- The supplied design document explicitly says it is read-only and not present in this worktree; `find . -iname 'design.md' -o -iname '*design*'` found no design document. I did not recreate or edit it. Prior environment limits from the earlier task remain recorded here: `gh`, Lean, Lake, and `lean/.lake` were absent; no declarations were created or set true.
- Read all seven research handoffs and the audited rational BSD target in the preceding task turn; their rank-zero/one, Iwasawa, higher-rank, computational, Riemann, and fluids findings remain unaltered.
- Committed the note and handoff as `37b82955` (`Extend BSD attempt with 389a1 descent assessment`).

## Deviations
- The requested rank-two certificate could not be independently rerun in this environment because Magma and Sage are absent. The note transcribes the published Magma command/output and explicitly labels it as non-local evidence, rather than claiming a reproduced computation.
- `design.md` was not updated because the supplied design document is expressly read-only and not in the worktree. It was not recreated, consistent with that constraint.
- No tests were run: this was research-note-only work, and no source implementation changed.

## Concerns
- The Magma handbook transcript is reproducible software output, not a machine-checkable standalone descent certificate. A local reproduction with a versioned Magma binary and archived complete output would strengthen the computational record.
- The exact analytic order is still not established by the cited output. Its rigorous lower bound is at least 2; no rigorous upper bound is given here.
- The formal BSD attempt remains unavailable, and the imported Mordell–Weil finiteness `sorryAx` concern and general rank-at-least-two implication remain unresolved.

## Follow-ups
- On a machine with Magma, execute the exact command in `formal-attempt.md`, record version and complete output, and check that the rank bounds derive from descent rather than relying on the heuristic analytic-rank line.
- For a rigorous analytic order exactly 2 claim, supply an independently checkable nonvanishing certificate for `L''(E,1)`; do not use BSD to infer it from the algebraic rank.
- If the lead needs a mutable design record, provide the actual writable design document/location; the copy supplied with this task is read-only and absent from the worktree.
