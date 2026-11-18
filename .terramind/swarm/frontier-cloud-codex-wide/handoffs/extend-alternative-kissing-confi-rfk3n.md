Outcome: done
## Done

- Read `AGENTS.md`, the earlier 604-point search handoff and its audit from commits `c69c9b04` and `f8f861b8` before searching.  This run deliberately did not repeat the earlier G-orbit/mixed-B pool, free-backbone LNS, symmetric CP-SAT, or 604-neighbourhood searches.
- Retrieved two primary coordinate sources into the disposable `.terramind/scratch/kissing11-c2/` checkout:
  - Together's EinsteinArena 604 file at `c388c6f7408c886311940896713339a1a70c2394`, SHA-256 `0bde9ca2c434d7beb5af63a64a291498e8c264d9a5718b738e92dd70b9ba7761`.
  - Station's public `kissing_number.zip`, SHA-256 `bbbef10e6934459c486fc0050f2d225ff60174fd761cc3884ee89d208fb9418a`; its certificate bundle SHA-256 is `61b3a572ad194a3b97d8bcae8694d57ae676328a81ef0e4db95e57a2c9d44f37`.
- Used the distinct Station Construction 3 as the baseline.  Its public certificate gives a 604-vector configuration as a rank-one projection of a constrained norm-four `D12` shell.  A standalone exact-integer checker validated the baseline before searching; a deliberately duplicated row and a baseline-row substitution control both rejected.  `bun frontier check` on a disposable witness scaffold reported `verified: Valid witness ... value 604; ties the best known`; declarations stayed false.  `bun frontier diagnose` likewise reported valid, 604, ties best known.  The disposable scaffolds were removed and no attempt was created for review.
- Enumerated the structured shell exactly: all norm-four `D12` points satisfying the published projection condition `r * (z[6] + z[8]) = 0`, represented as `p + q*sqrt(2)` numerator pairs.  It contains 6,720 projected directions, including all 604 baseline rows and 6,116 new rows.  Every new row has an exact baseline blocker set of size at least 3.  Histogram: 3:36, 4:192, 6:512, 7:1152, 8:1344, 9:1536, 10:384, 12:384, 13:320, 14:128, 16:64, 17:64.
- Ran `taskset -c 0 python3 d12_shell_search.py --seconds 1800 --seed 2026111802` for exactly 1,800.000064 seconds, normal exit status 0 (2026-11-18T12:40:43Z to 13:10:43Z).  The seeded blocker-union sampler made 22,948,687 trials, tested every comparison with exact `Z[sqrt(2)]` arithmetic, and stopped if it created an exact configuration of at least 605.  It produced no positive-gain exchange and no candidate witness; consequently there was no candidate to pass to `frontier diagnose`.
- Raw evidence is retained in the disposable scratch checkout: `d12_shell_search.py` (SHA-256 `48664c60c0ccbeccd44f09fcbabe791c3b43725b13cb6c5e020ce41766228ee1`), `search.log` (SHA-256 `5493e82b3fd78941f6b682aedcb3ee3db85feec43be7066d7525f4da23e31ecd`), `summary.json` (SHA-256 `955b75b8a6b80d87578c9134cc919082d8850aec9805e4b44521c0d1571c61e5`), and baseline checker/diagnostic logs.  Exact resume cursor: `22948687`; reuse the same source data and `--seed 2026111802 --resume 22948687` to continue the trial count (the current search restarts its PRNG sequence, so a true continuation should also advance/replay the RNG state or add state persistence).

## Deviations

- The requested clean disposable checkout was used for source material rather than a separate clone of Frontier: the current task worktree was already clean and the external source repository was cloned into the disposable scratch directory.  No repository product files outside this handoff were retained.
- The search is a bounded randomized blocker-union sampler, not a maximum-clique proof.  Its negative outcome applies only to the sampled exchanges in this 6,720-direction constrained `D12` shell; it establishes no upper bound and does not rule out a 605 configuration.
- The source shell contains the published Construction 3 and is a new structured pool relative to the earlier work, but it is not a claim that this shell exhausts every useful projection or every `D12` shell.

## Concerns

- A single insertion cannot help because all 6,116 nonbaseline shell directions have at least three blockers.  The current sampler also had no positive-gain event, so it did not exercise a near-improving exact candidate; the duplicate/substitution controls exercise the validator but not a planted multi-swap restoration.
- Candidate-pair compatibility is memoized in process memory (18,699,670 entries by the final progress line).  The run completed on one core, but a larger shell or longer run should use a bounded cache or explicit checkpointed state.
- The run has no 605 witness; publications, declarations, PR submission, and any claim beyond this measured negative search remain pending human approval.

## Follow-ups

- Add a checkpointed RNG state and a calibrated planted positive-gain instance, then resume blocker-union search from cursor 22,948,687.
- Search the full `D12` norm-four shell without the norm-preserving projection restriction using per-vector normalization and Frontier's scale-free verifier, or use a different published Station configuration (2) as the backbone.
- Use an exact branch-and-bound/max-clique solver on tightly filtered blocker unions to exhaust small exchange sizes before spending more time on random sampling.
