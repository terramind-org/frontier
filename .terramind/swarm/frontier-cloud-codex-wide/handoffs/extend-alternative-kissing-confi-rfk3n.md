Outcome: done
## Done

- Recovered PR 153 commit `80e585bb` and reverified the Station Construction 3 baseline used by c9: 604 distinct exact rows, pairwise exact-compatible. The immutable public fixture SHA-256 is `61b3a572ad194a3b97d8bcae8694d57ae676328a81ef0e4db95e57a2c9d44f37`; the reconstructed 5,156-direction ordering SHA-256 is `c5f42ea6ceada60c9465564f4771d9b8fe1ab95179a96ed43e8a98c12cd327ad`. This family remains distinct from c4's unverified 5,120 count and from the completed size-13--20 pair family.
- Ran a fresh one-CPU deterministic triple-exchange experiment, with a separate SQLite single-writer ledger. Its seeded order is `python.Random(0xc102130)`, sorted selected indices; it accepts mutually compatible triples with at least one shared blocker and a complete baseline blocker union of size 21--30. It records triples and deduplicated deletion pools independently.
- Screened every committed prefix pool against all 6,116 recovered shell directions, not just the 5,156 stream directions. Exact integer-mask eligibility was independently compared with the direct set predicate on 32 lexical pools after the run. The run also completed the planted K4 and exhaustive 32,768 labelled six-vertex exact-clique controls before ledger mutation.
- The bounded run was stopped cleanly at stream cursor 24,227,840. It durably contains 3,951,256 accepted triples and 3,948,629 unique pools: 94,639 sound cardinality `pruned` and 3,853,990 explicitly `unvisited`; zero `exhaustive`, `timeout`, or candidate outcomes. The first unvisited pool is `1,2,9,10,21,22,67,101,102,113,117,201,283,284,291,292,465,534,542,548,557,558,566,594`.
- SQLite `quick_check(1)` returned `ok`; the external, uncommitted ledger SHA-256 is `5c35df0e69d6385cab9699f92f6235527425d85b0f5828e350cc8ae18e5c3fca`. Compact script and summary are in `.terramind/scratch/kissing11-c10/`; the multi-GB ledger is deliberately outside Git. No eligibility surplus, clique invocation, 605+ witness, or Frontier candidate validation occurred.

## Deviations

- The 24-minute cap was manually stopped before the nominal limit after the durable checkpoint became large; this is a bounded prefix, not exhaustive triple-family coverage.
- The initial in-script set/mask check saw no pre-existing pools. It was therefore rerun immediately after the slice on 32 deterministic lexical pools and passed.

## Concerns

- 3,853,990 generated pools remain unvisited, and the infinite seeded stream has a larger ungenerated scope. Neither is an upper bound.
- The overlap-biased stream is a reproducible search heuristic, not exhaustive enumeration of all compatible triples.

## Follow-ups

- Resume exact screening from the recorded unvisited key without regenerating the committed triple prefix; run the calibrated clique solver and independent exact scan plus Frontier diagnose/check if eligibility exceeds deletions.
- If broader coverage is required, define a finite disjoint triple order or another shell family, retaining separate ledgers and the c4 separation.
