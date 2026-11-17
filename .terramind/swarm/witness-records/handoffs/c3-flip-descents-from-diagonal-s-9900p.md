## Done

**Attempt:** `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d/`, kind `writeup`. Title: "C3 flip descents from 2-block {4,1},{3,2} and 1-block diagonal starts, scheduled 2 h, no rank-92 scheme found (best GF(2): 95, 98, 97)". Declarations are false. Nothing was submitted.

`bun frontier check attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d`, verbatim:
```
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```
`bun frontier validate` on the attempt complains only that the declarations are not confirmed.

**Result:** The record is 93. No GF(2) scheme of rank 92 or less was reached, so nothing beats, ties or reaches the record as a witness of this attempt.

| start (block sizes) | target | descents | lowest GF(2) rank |
| --- | --- | --- | --- |
| {4,1} | 92 | 237 fresh, plus 44 pool restarts | 95, in 20 descents |
| {3,2} | 92 | 113 | 98 |
| {5} | 91 | 108 | 97 |
| {2,2,1}, the paper's start | 90 | 116 | 93, in 8 descents |

Partitions with the same block sizes are isomorphic searches (a permutation relabelling commutes with C3), so {3,2}, {4,1} and {5} cover all 2- and 1-block starts.

The long run went from 19:16:13 to 21:16:14 UTC on at most 2 processes. Exit statuses:
- 0: p1-32, p2-41, p3-41v, p3-5, p4-221, p4-41.
- 134: p1-5, a crash; see Concerns.
- 143: p1b-5-repro, p2-32k and p3-41pool, which I stopped.

The searches ran unattended across the usage-limit pause, from about 20:38 to 20:45 UTC. They stayed inside their planned windows, nothing overran, and no planned phase was skipped. The final phase was launched after the pause to end at the budget end. No search process remains.

**Calibration:**
- Self-test: 20,000 random moves with the tensor identity and index re-checked after each, 0 failures; a broken copy was rejected.
- 2x2 from {{1,2}}: 20 of 20 descents reached 7.
- 3x3 from {{1,2},{3}}: 20 of 20 reached 23, the paper's value.
- 5x5 from the paper's start {{1,5},{2,4},{3}}, with Algorithm 1 as printed: 1 of 10 descents reached 93 at 31 s in the calibration, and 8 of 115 in the 28-minute long-run phase, the first after 27 s. An earlier variant that reset the plus counter after every reduction reached only 96 in 150 s; this is in the writeup. Throughput is about 6 to 10 M flips/s per core, a few times lower than the paper reports.
- The status note's "{3,2} ending at 101 and {5} at 106" were the first descents only. The full runs reached 98 and 97.

**Lift:** a C3-symmetric Hensel lift, `c3lift.py`. On the published scheme's mod-2 reduction it returned an integer scheme with coefficients in {-1,0,1} on the first try (mod 4). `bun frontier diagnose`: `valid: yes`, value 93, ties. It also lifted, all verifier-accepted:
- all 19 3x3 rank-23 schemes (verifier at n = 3);
- the 2x2 rank-7 scheme;
- a {4,1} rank-95 scheme;
- all 9 rank-93 schemes this search found. These fall into at least 5 factor-rank classes, 4 of them different from the published scheme's. They are ties and were not submitted.

**Evidence:**
- Worktree `frozen-canyon`, scratch `.terramind/scratch/matmul5-r2/`.
- Logs in `logs/`: `<tag>.log` and `<tag>.status` per process, `summary-all.txt`, `cal-small.log`, `lift-*.log`, `factor-ranks-93.log`, `baseline-diagnose.log`, `broken-diagnose.log`.
- Schemes in `out/long/` and `out/cal/` (`.c3` GF(2), `.json` lifted).

**Gate:** `bun run check`: tsc passes, 434 tests pass, 1 skipped, 0 failed. Validate fails only on unconfirmed declarations (decision 6) and on local paths in two attempts that are not mine (see Concerns).

## Deviations

- The brief listed three {3,2} partitions and one {4,1}. They are equivalent by relabelling, so I searched block-size types: {3,2}, {4,1} and {5}.
- The paper's prose and its pseudocode differ on when the plus counter resets. The prose reading reached only 96 at calibration; the pseudocode reached 93. All long runs use the pseudocode.
- The pseudocode, with no rank cap, let one {5} descent run away and crash p1-5 at 19:25 UTC. The core sat idle for 12 minutes, and about 13 core-minutes went to a deterministic replay that confirmed the cause. Later builds cap plus-transitions at 30 orbits above the descent's best.
- "Keep the best state when restarting" was tried two ways: kicks back to the descent's best, and pool restarts from rank-95 states. Both mostly revisited states (17% and 0.6% distinct), so I stopped them early and went back to independent descents.
- The calibration took about 10 minutes before the long run. Brief lifts and diagnoses (about 5 s each) ran beside the 2 search processes.

## Concerns

- Throughput is a few times below the paper's. Every 2- and 1-block descent stopped at least one orbit above its target. So "no 92 found" is weak evidence about whether a C3 rank-92 scheme exists. The search itself is calibrated: it reproduces 93 from the paper's start within a minute.
- Distinct-state counts are sampled every 128 flips, through a 64-bit order-independent hash. They are not exact counts.
- `bun run check` on this branch also fails on local paths in `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/writeup.md` (round 1) and `attempts/witness.schur-7/20261117-terramind-com-c8ca32/run.sh`. Neither is mine; the correction tasks own them.
- `verify-n.ts` in the attempt imports the verifier relative to the attempt directory. It was run from scratch with the equivalent path.

## Follow-ups

- More independent {4,1} descents at higher throughput (it reaches 95 in about 8% of descents), and a sweep of M and L.
- The paper's 6x6 trick: mine 1-block results for diagonal orbits that suggest a better partition.
- C3 × Z2 starts, and the other partition types.
- The lift is not the bottleneck: it worked on every scheme tried.
