Outcome: done
## Done

- Read `AGENTS.md`, PR 70 handoff `6c73c47e`, and audited the c4 recovery paths first. Neither a `c4` ref nor `.terramind/scratch/kissing11-c4/{d12_candidate_unions.py,search.log}` existed in this checkout; no old solver process survived. This is therefore a reconstruction from the PR 70 source, with **no c4 elapsed-time or coverage credit**.
- Recovered the published Station Construction 3 certificate directly from `dualverse-ai/station_data_v2`, SHA-256 `61b3a572ad194a3b97d8bcae8694d57ae676328a81ef0e4db95e57a2c9d44f37`. An independent exact scan of its denominator-two `Z[sqrt(2)]` representation found 604 distinct norm-16 rows and zero incompatible pairs.
- Built `d12_candidate_unions.py` in disposable scratch. It calibrates the deterministic Bron--Kerbosch solver with a planted 4-clique and exhaustive agreement with brute force on all 32,768 labelled six-vertex graphs. It enumerates the published constrained norm-four `D12` shell, uses exact `Z[sqrt(2)]` blocker/compatibility tests, and has one SQLite writer with fully committed pair and pool batches. The ledger distinguishes `unvisited`, `pruned`, `exhaustive`, and `timeout` outcomes.
- Ran `taskset -c 0 python3 d12_candidate_unions.py --seconds 1500 --slice 64 --per-pool 0.15` for 1,505.892852 seconds, normal exit, on one cloud CPU. The shell had 6,720 directions and 6,116 non-baseline rows. The reconstructed 3--10-blocker filter yielded 5,156 directions (not the 5,120 stated by the missing c4 brief); candidate-order SHA-256 `c5f42ea6ceada60c9465564f4771d9b8fe1ab95179a96ed43e8a98c12cd327ad`.
- Exhausted pair generation at restart cursor 5,156: 10,961,632 compatible pairs, each with a unique deduplicated full blocker union of size 13--20. The bounded exact phase cardinality-pruned 597 pools; 10,961,035 pools remain durably `unvisited`. There were zero exhaustive clique outcomes, zero timeouts, and no 605 candidate, so no candidate Frontier validation was applicable.
- Raw reproducibility artifacts remain under `.terramind/scratch/kissing11-c5/`: solver `55025c81d6ba67b7e1b7962b0c10dfd9994d6f1abc2e07c1bb40f6831b79d461`, log `e2c497d8d2cbd12493df96f746405c43852fdc1d2bfcb66c7e3a5ace09290c42`, summary `a4e06e950bc7948d40b0dc642e6fde0b71ba7cd7fa7f00bef532ae91eff3b8fa`, and atomic ledger `6427549cbadb94f2ebff65ffc5dc3413aac9a30f440324fcabaf50fe096daf9c`.

## Deviations

- The fresh cloud checkout did not contain c4 artifacts, so this run reconstructed the requested family from the published certificate rather than resuming it.
- `bun` is absent from this cloud image and there was no time remaining in the 30-minute envelope to install dependencies and make a disposable Frontier scaffold. The baseline exact scan above is independent of Frontier; the prior PR 70 handoff records Frontier `check` and `diagnose` at 604. No Frontier credit is claimed for this run.

## Concerns

- The pair-first family is much larger than anticipated: it produced 10.96M distinct deletion sets, so the 25-minute bounded run reached only its 597 early cardinality prunes. The durable restart state is necessary; treating the remaining pools as searched would be false.
- The 5,156 reconstructed low-blocker directions disagree with the unavailable c4 claim of 5,120. Resume only after auditing that filter/order discrepancy against c4 if it becomes available.
- This is not an upper bound and does not rule out 605 points.

## Follow-ups

- Resume exact solving from the SQLite `unvisited` pools in lexical deletion-set order, retaining the fixture/order hashes and separate outcome counts; first prioritize pools whose eligible count exceeds deletion count.
- Audit the missing c4's 5,120-direction filter against the reconstructed 5,156-direction filter before combining coverage.
- On a new allocation, make a disposable false-declaration witness scaffold and run Frontier `check`/`diagnose` on the recovered baseline before any candidate is claimed.
