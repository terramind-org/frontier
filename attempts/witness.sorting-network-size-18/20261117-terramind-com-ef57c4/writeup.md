# Record-started sorting-network search, 120-minute wall budget

This failed search found no valid 18-input sorting network with 76 gates or fewer. No SorterHunter run produced a valid network smaller than its input. The only 77-gate networks the runs printed are the two 77-gate inputs (the published record and round 1's network), so the best valid size, 77, is the input, which ties the record. The best measured 76-gate candidate fails 48 of the 262144 binary inputs. This writeup is not machine-checked. No witness is submitted.

## Measured

The campaign used the interval **2026-11-17 19:07:41.384524 to 21:07:41.384524 UTC** as its 7200-second wall deadline, including controls and setup retries. The first calibration launch failed before starting SorterHunter because the operating system rejected the requested virtual-address limit. The successful calibration started at 19:08:55 UTC; the original deadline was retained. The long SorterHunter runs started at 19:09:11.890452 UTC and ended at 21:07:40.387069 UTC. The final repair child ended at 21:07:41.414048 UTC, about 30 ms after the scheduled deadline during termination and reaping.

`bun frontier diagnose` accepts the published 77-gate baseline and reports that it ties the best known value. The inner-loop checks accept all three starting networks and reject the baseline with gate 33 deleted; that 76-gate object fails 63 inputs. Post-run independent bitset simulation accepts all **86 distinct ordered networks** printed by the 36 SorterHunter runs. Eight distinct printed ordered sequences have 77 gates. They are four orderings each of the two 77-gate inputs. The auditor found that up to commuting gates and mirror symmetry, the 86 printed networks form 77 classes. These include the three inputs, 16 new 78-gate classes and larger networks.

There were **36 bounded SorterHunter runs**, each lasting 196.0 to 197.6 seconds of wall time. In the auditor's recount, SorterHunter's own CPU clock reports 33 to 178 s per run, 3,717 CPU s in total. That is 52% of the 7,095 s wall total, about half a core on a shared machine. Every run reported the intended initial size, 77 or 78, and every run ended by the wrapper's scheduled SIGTERM, return code `-15`. Their last iteration reports sum to **4,238,175,949** mutation iterations. This is a lower bound on the total because the heartbeat prints at every 10% increase. It includes repeated states.

Exact candidate sampling every 65536 iterations records 33 to 6289 distinct sampled ordered candidates per run. The sum of these within-run counts is 64,653; overlap between runs was not removed. From run 08 onwards, a 65536-register HyperLogLog counter also estimates cardinality across all mutation candidates. The final printed estimates in those 28 runs range from 2,172,346.8 to 368,420,602.0 distinct ordered candidates per run. The nominal relative standard error is 0.40625% under the usual uniform-hash assumption. These are estimates at the last printed heartbeat, with no exact global union count. The first eight runs retain exact sampled counts only. Each run also retains the maximum reported positional difference from the initial mutable sequence (`MaxPositionDistance`). As the auditor noted, a single insertion shifts every later position, so this metric does not measure distance from the record.

There were **47 SAT shortening queries**. All remain unresolved: 38 logs contain an explicit internal `timeout` result and nine were stopped by the per-query 120-second limit (110-second internal deadline plus 10 seconds) without a final solver answer. Process exit codes are 36 zeros and eleven `-15`s. Two of the interrupted processes had already printed an internal timeout before termination, so those exit counts overlap the result counts. No research query returned UNSAT or a fully validated SAT replacement. Each solve attempt logs the solver's Boolean/unknown answer and accumulated restart, conflict, decision and propagation statistics.

The 76-gate repair phase started at 20:37:50.368692 UTC and printed its budget result at 21:07:41.391333 UTC. It evaluated **699,445 candidates**, accepted 29,258 moves, and initialized 35 walks. Its every-128-candidate sample contains **5464 distinct ordered candidates**, an exact count of that sample. The best score went from 63 to 58 at evaluation 362018, then to **48 at evaluation 377888**, both in walk 19. The final child returned `-15` at the deadline after printing its budget result. The repository verifier rejects the retained 48-failure candidate: 76 gates, `valid: false`, `beats_best_known: false`, with adjacent-wire violation counts 15, 18 and 15. Independent bitsets count 48 distinct failing inputs.

## Starting networks and controls

The [published network list](https://bertdobbelaere.github.io/sorting_networks.html) gives the 77-gate, 12-layer record and the 78-gate, 11-layer alternative. Their source JSON files are `Networks/Sorters/Sort_18_77_12.json` and `Sort_18_78_11.json` in [SorterHunter](https://github.com/bertdobbelaere/SorterHunter), revision `a18ee1743733c76ba07f08f990139a2d6840230a`. The third input is the distinct 77-gate, 14-layer network retained by round 1 in `attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/logs/network_77_found_by_SorterHunter_seedB.json`, revision `09ffd987b038ff0b0ea37967e0eee1e83375c5f4`. The preparation script can retrieve that immutable input if the prior attempt is absent from a checkout.

The search stages passed known-answer controls before their long runs:

- SorterHunter started from an optimal 19-gate, 8-input network padded to 20 gates and reached 19. Its initial-size report was 20. The bounded control ended by SIGTERM after reaching its target.
- The sequential-cardinality SAT encoder removed a planted redundant comparator from the 18-input record, returning a valid 77-gate network. All sixteen four-gate windows of the optimal 19-gate, 8-input network returned UNSAT when shortened to three gates. Their solver statistics are retained.
- Before 18-input repair began, the actual repair heuristic restored a damaged 19-gate, 8-input network in 875 candidate evaluations, reaching zero failing inputs. A separate earlier exhaustive one-gate-neighborhood control also restored it. The live control uses the same stochastic loop as the research search.
- The diversity counter estimated 9937.793 for 10000 known distinct two-gate sequences. Adding those same sequences again left the estimate unchanged.

The 77-gate baseline, planted-gate SAT result and repaired 8-input control all pass independent bitset simulation. The 18-input baseline also passes the repository verifier.

## SorterHunter method

For each of the three inputs, the search used symmetric and asymmetric mode, fixed prefixes of zero, one and two earliest dependency layers, and two seeds for each configuration. The literal prefix is removed from the mutable core. Symmetric mode supplies only mirror representatives with `i + j <= 17`, including self-mirrored gates once. Asymmetric mode supplies the full remaining core. Every serialized prefix-plus-expanded-core input was checked on all binary inputs before launch. The program's initial-size report was then required to match the supplied network size; a mismatch would abort that run. This corrects round 1's initialization error.

Run index `k` ranges from 0 to 35 in `campaign.py`. Seeds are `18001 + 101*k`; escape rates cycle through 300, 1000 and 5000; maximum mutations cycle through 1, 2 and 4 in groups of three runs. `RestartRate=0` leaves the bounded wrapper in charge of restarting from the known inputs. Each input was therefore started 12 times in total (36 runs over 3 inputs). The logs do not record the size of the accepted network after the start. In audit reruns of two of these configurations, the accepted network left 77 gates within the first 0.32 CPU seconds and stayed at 78 to 95 gates for the rest of the run, so nearly all run time in those reruns was spent above 77.

The auditor reran configurations 01 and 03 for 170 s each with a counter added to a clean upstream SorterHunter build. In the first second, the counter recorded 1 and 2 other 77-gate classes, respectively, up to commuting gates. Run 01 last accepted a network of at most 77 gates by 0.32 CPU s and then stayed at 78 to 86 gates. Run 03 did so by 0.26 CPU s and then stayed at 79 to 95 gates. In these configurations, `RestartRate=0` disables internal restarts and the campaign's `EscapeRate` settings of 300 to 5000 insert gates without returning to the start. The drift was measured in two configurations only. The inference that the other runs also drifted rests on the shared restart and escape settings.

Mutation weights are remove 1, swap 1, replace 1, cross 1, swap-intersecting 2 and replace-half 1. The default valid-uphill-step rule remains enabled. `Verbosity=3` prints iteration heartbeats. Timestamped capture records process starts, immutable configuration names, initial sizes, networks, counters and exits. Instrumentation adds no RNG calls and changes no mutation or acceptance rule.

The upstream program was built with Apple Clang 21.0.0 using `-O3 -march=native`. Third-party source and binaries remain in scratch. The included preparation script applies the logging patch to the named upstream revision; the attempt contains our scripts and counter control only.

## SAT method and exact coverage

For a window `(s,w)`, keep gates before `s` and after `s+w` fixed, then synthesize exactly `w-1` gates. Every gate position can select any of the 153 legal comparator pairs. Exactly-one constraints use a sequential-counter encoding. Guarded AND/OR clauses implement the selected comparator; untouched-wire clauses implement identity. Final output constraints require ascending bits after the fixed suffix. No comparator-pair restriction or adjacent-repeat exclusion is used.

Counterexample refinement starts with up to 32 shuffled failing prefix outputs and 20 shuffled prefix outputs, deduplicated. Every SAT model is simulated on all distinct reachable prefix outputs; up to 24 failing outputs are added. A model passing that test is also checked on all 262144 original inputs. CaDiCaL receives conflict budgets of 10000 between status reports. Most queries use a 110-second internal deadline plus a 10-second outer allowance; the final query is shortened to fit the phase cutoff. Seeds are `28000 + query_index`.

`baseline` and `round1` each have order 0 plus two commuting reorderings. Each reordering attempts 10000 random adjacent swaps and permits a swap only for disjoint comparators. Their seeds are 27001 and 27002. The planned 144-query grid uses widths 11 through 14 and offsets 0, 9, 17, 25, 33 and 41. Seed 27182 shuffles the grid; only its first 47 queries ran. All offsets are zero-based, and the following are the actual `(s,w)` pairs:

- `baseline`, order 0: `(9,11)`, `(9,12)`, `(9,13)`, `(17,11)`, `(17,12)`, `(25,11)`, `(25,12)`, `(25,14)`, `(33,13)`, `(41,12)`.
- `baseline`, order 1: `(0,11)`, `(0,14)`, `(9,12)`, `(17,11)`, `(17,14)`, `(25,13)`, `(25,14)`, `(41,11)`, `(41,13)`.
- `baseline`, order 2: `(0,11)`, `(0,13)`, `(0,14)`, `(17,13)`, `(25,11)`, `(25,13)`, `(41,14)`.
- `round1`, order 0: `(0,12)`, `(0,13)`, `(17,11)`, `(33,11)`, `(41,14)`.
- `round1`, order 1: `(0,14)`, `(9,11)`, `(9,12)`, `(9,14)`, `(17,11)`, `(17,13)`, `(25,13)`, `(33,14)`, `(41,11)`, `(41,14)`.
- `round1`, order 2: `(0,14)`, `(9,12)`, `(17,14)`, `(25,11)`, `(25,12)`, `(33,13)`.

All listed queries timed out or were interrupted without an answer. In the auditor's planted control, removing a duplicated gate from a 12-gate mid-network window took 171 s, beyond the campaign's 110-second internal budget. The campaign timeouts therefore leave open whether those windows admit a saving. The auditor's 11- and 12-gate tail queries finished in 8 to 18 s, but the campaign did not sample those tail offsets. Weighted full-input failure counts and the best non-sorting SAT model were retained from query 17 onwards. Earlier SAT models were checked for correctness but their failure counts and objects were not retained. Therefore 48 is the best **measured** 76-gate score, rather than a claim about every transient model from the entire campaign. The best retained SAT candidate fails 1979 inputs; none qualified to improve the deletion starts used by repair.

## Repair method

The exact bitset checker represents every wire on all 262144 inputs and counts the union of unsorted outputs. Cached prefix states allow evaluation from the earliest changed gate. The search ranks every single deletion from both 77-gate inputs and uses the best eight deletions from each as sixteen starts. It also checks retained SAT models for better starts; none beats the 63-input deletion score.

Seed 32003 drives one- or two-gate replacements, comparator swaps and comparator relocations at fixed length 76. A walk restarts after 20000 candidate evaluations. Temperature varies by walk through 0, 1, 4 and 16 and cools within the walk. The best object is saved whenever its score improves; logs record the score trajectory immediately. The retained final object is `repair76.best.json` in scratch. No 75-gate repair was run.

## Inferred and untested

The published 77-gate constructions can be loaded correctly into both SorterHunter modes. These seeded runs supplied no record improvement. The unresolved SAT calls supply no exclusion result for their windows. An audit control showed that the same repair loop could not restore the record with one wrong gate at n = 18 within 4 to 5 minutes (best 43 failures at 240 s and 317 at 300 s). The 8-input controls passed trivially and do not calibrate performance at n = 18. A 48-failure score therefore carries no evidence of closeness. The auditor enumerated all 11,552 single-gate replacements of the 48-failure candidate. The candidate is a local minimum for single-gate replacement. Four replacements tied the score and the other 11,548 scored worse.

Only the named seeds, prefixes and parameter combinations ran. The SAT stage sampled 47 of its 144 planned queries, with no longer per-window budgets, mirror-linked windows, free-tail synthesis or 75-gate repair. This attempt establishes no lower bound on network size.

## Follow-ups

- **SorterHunter (method).** Use `RestartRate` to return to the record every roughly 10^5 to 10^6 iterations, or set `EscapeRate` far above 5000. Log the accepted network size and each new class at or below 77 gates.
- **Repair (method).** Use systematic one- and two-gate neighbourhoods and run a full-size positive control first. The 48-failure score provides no basis for choosing that candidate as a restart point.
- **SAT (time and coverage).** Give selected 11- and 12-gate mid-network windows 20 to 30 minutes each or use a stronger encoding. Sweep tail offsets at widths 11 to 14, including reordered tails. Keep proof certificates for any reported UNSAT.

Report CPU seconds alongside wall time.

## Independent audit

The auditor independently re-simulated the baseline on all 2^18 binary inputs, recounted every SorterHunter run from configs and logs, and confirmed the run counts and starting networks. The auditor also reran two SorterHunter configurations with an accepted-network counter, ran full-size repair controls and tested planted savings with the SAT encoder. Five statements were corrected using this evidence. The audit is an independent assessment backed by reruns. The repository checker marks this writeup unchecked.

## Evidence and reproduction

Evidence is retained in worktree `novel-shelf`, under `.terramind/scratch/sortnet18-r2/`: `budget.json`, `provenance.json`, `build-manifest.json`, `calibration.log`, `cal_hunter8.log`, `cal_repair8.log`, `hll_control.log`, `hunter-lane.log`, all `hunt_*.cfg`, `hunt_*.log` and `hunt_*.summary.json`, `sat-lane.log`, `sat_*.log`, `sat_*.exit.json`, retained candidate objects, `repair.log`, `repair.exit.json`, the final diagnostic JSON files and `evidence-summary.json`. Raw logs and network data are retained for audit and are excluded from this source-only attempt.

Reproduce in a fresh scratch directory. Copy `scripts/` there, create its Python environment with Python 3.12, install NumPy 2.5.5 and python-sat 1.9.dev22, and clone the named SorterHunter revision into `upstream/SorterHunter`. Run `prepare.py`, compile the four upstream C++ translation units with the flags above, and name the binary `SorterHunter` beside the scripts. Run `calibrate.py`, then run the `hunter` and `sat` modes of `campaign.py` together, from the repository root. Both lanes share `budget.json` and the original deadline. Environment variables `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` limit numeric-library threads. `summarize.py` reconciles the logs. The early eight runs used the same search code without the later HLL counter; their exact sampled counts remain available.

The campaign used two single-threaded process lanes. RSS was sampled every five seconds, with termination above 1300000 KiB per child, after the virtual-address-limit setup failed. Highest sampled child RSS was 754800 KiB for SAT, 7600 KiB for SorterHunter and 215456 KiB for repair. Sampling does not certify an instantaneous memory maximum. No Lean, cloud compute or paid API was used. Both declarations remain false.
