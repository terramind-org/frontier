Outcome: OVERSTATED

The measured search results survive this audit. The blanket local-optimality and heuristic-exhaustion conclusions do not. Correct the quoted statements in check 5 before presenting this attempt for submission. No network with 76 or fewer gates was found during the audit. This report is an independent opinion supported by reruns, not a Frontier checker verdict on the writeup.

## Done

Paths used below, relative to this worktree unless absolute:

- `P = attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f`.
- `A = /Users/agrim/.terramind/worktrees/frontier/bumpy-quartz/.terramind/scratch/sortnet18` (read only).
- `S = .terramind/scratch/audit-sortnet18` (audit scripts, configurations, outputs and virtualenv).

Read the binding design document, including decisions 9 and 10, and the repository's `AGENTS.md`. Ran `bun install` successfully. Created an independent Python 3.12.1 environment with `uv venv --python 3.12 S/.venv` and `uv pip install --python S/.venv/bin/python python-sat numpy`: python-sat 1.9.dev22 and numpy 2.5.5. Audit runs used one process per test stream, at most two CPU-heavy streams together, and `OPENBLAS_NUM_THREADS=1`; no long search was launched.

### 1. Baseline and run-B network

Ran `bun frontier show witness.sorting-network-size-18`: configured record 77 gates, target at most 76, all 262144 binary inputs checked, smaller value to the lower indexed wire.

Ran these exact diagnostics, without re-encoding either supplied file:

```text
bun frontier diagnose /Users/agrim/.terramind/worktrees/frontier/bumpy-quartz/.terramind/scratch/sortnet18/baseline.json --problem witness.sorting-network-size-18
value: 77; valid: yes; result: ties the best known value

bun frontier diagnose attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/logs/network_77_found_by_SorterHunter_seedB.json --problem witness.sorting-network-size-18
value: 77; valid: yes; result: ties the best known value
```

`S/evidence.py` compared ordered lists and comparator multisets: `BASELINE_EQUALS_B False same_multiset False`. Run B is a distinct construction, rather than a commuting reorder of the record. Parsing the saved source page `A/dl_src/SorterHunter/sorting_networks.html`, lines 350-363, gave `SAVED_PAGE_MATCH 77 True`: the baseline exactly matches its `N18L77D12` row.

An additional comparison found that the submitted JSON matches `P/logs/sh_B_output.txt:100`, the **77-gate, 14-layer** sorter. It does not match the later 77-gate, 12-layer sorter at line 102. Independent depth calculation (`depth[i]=depth[j]=max(depth[i],depth[j])+1` for each gate) returned `PROVIDED_DEPTH 14`.

### 2. SAT encoder: positive controls, negative controls and soundness

Read `P/scripts/window_sat.py:1-145` line by line. `S/tests.py sat` imports that exact file. For the small tests it changes only module globals `N=8` and `PAIRS` to the 28 ordered pairs; the encoding and refinement algorithm are unchanged. Complete output is in `S/sat-tests.log`.

Positive control on 18 wires: insert `(0,17)` at zero-based position 74 in the record. Its neighbors are `(7,8)` and `(9,10)`, so it is not adjacent to an identical gate. Solve the 3-gate window at `s=73` for 2 gates. Output: `SAT`, one round, 23 vectors, about one second; returned full length 77 and independent exhaustive simulation found zero failures. Diagnostics confirmed both sides:

```text
bun frontier diagnose .terramind/scratch/audit-sortnet18/redundant78.json --problem witness.sorting-network-size-18
value: 78; valid: yes; does not reach the best known value
bun frontier diagnose .terramind/scratch/audit-sortnet18/redundant78.sat.json --problem witness.sorting-network-size-18
value: 77; valid: yes; ties the best known value
```

Positive control on eight wires: construct bubble sort as `[(j,j+1) for end in range(7,0,-1) for j in range(end)]`, length 28. Replace the last 10 gates (`s=18,w=10`) by nine: `SAT`, one round, 35 vectors, 0.3 seconds. Independent exhaustive simulation found zero failures. Calling the repository's `src/check/witness/sortnet.ts` verifier directly with `{n:8}` on `S/bubble28.sat.json` returned `{valid:true, violations:[], omitted:0, value:27}`.

Negative controls on eight wires: use the 19-gate network from `A/dl_src/SorterHunter/Networks/Sorters/Sort_8_19_6.json`, independently verify all 256 inputs, then test every four-gate window (`s=0..15`) for a three-gate replacement. All 16 returned `UNSAT` in 0.0-0.2 seconds each. The unshortened 19- and 28-gate networks both had zero failures under an independent bitset checker.

Reran the requested three original negatives on the unchanged encoder:

```text
s=69,w=8,T=7:   UNSAT, 30 prefix vectors, 30 encoded, 1 round, 1.8 s
s=68,w=9,T=8:   UNSAT, 33 prefix vectors, 33 encoded, 1 round, 2.6 s
s=67,w=10,T=9:  UNSAT, 36 prefix vectors, 36 encoded, 1 round, 4.7 s
```

Also reran the author's stated sanity check at `s=70,w=5`: `target=5` was `SAT` (1.4 s); `target=4` was `UNSAT` (1.5 s), in `S/sanity.log`.

Encoding findings:

- Lines 51-55 encode at least one and pairwise at most one pair per position. All 153 legal pairs are available.
- Lines 57-63 make `untouched` equivalent to no selected gate touching the wire. Lines 81-92 correctly encode identity on untouched wires and AND/OR on the selected pair.
- Lines 94-99 allocate fresh AND/OR outputs for each fixed suffix gate, reading both old inputs before updating the wire map. Lines 100-101 require ascending output.
- Lines 40-42 take the supplied record's actual prefix and suffix with the stated half-open offsets. `all_inputs`, `apply` and the repository verifier agree on zero-based wires and comparator direction.
- UNSAT on the encoded subset is sufficient. SAT is accepted only after all distinct prefix outputs pass (`123-128`). The refinement adds real counterexamples. No bug was found that turns a satisfiable recorded instance into UNSAT.
- The adjacent-repeat restriction at lines 64-67 deserves more justification than merely saying duplicates are redundant, because the encoding uses an exact replacement length. `S/extra.py` exhaustively enumerated each prefix used by the recorded UNSAT windows and counted comparator pairs already ordered on every prefix output. The minimum was **42**. Thus two different redundant pairs are available at each such prefix. Remove adjacent duplicates from any proposed replacement, then pad its beginning to the required length by alternating these redundant pairs, choosing the final padding pair different from the first remaining gate. This preserves every reachable input and satisfies the restriction. It therefore excludes no genuine saving for these specific instances. This is not a claim about arbitrary inputs to this general-purpose script.
- As another control, removing only the repeat restriction and rerunning the same three windows still returned `UNSAT` (2.1, 2.9, 5.2 s), recorded in `S/extra.log`.

### 3. Search execution, runtime evidence and InitialNetwork

`S/evidence.py` parsed every network line and compared retained files byte for byte. Both SorterHunter logs and all four SAT logs match the author's scratch originals. Run A contains 59 printed networks, improving from 115 gates to 78; best lines are `P/logs/sh_A_output.txt:110,112`, with 79 gates/11 layers at line 118. Run B contains 52 networks, improving from 111 to 77; its two 77-gate results are at lines 100 and 102. No shorter network occurs in either log.

The retained logs show real exploration, not a step-zero loop. They lack timestamps or iteration heartbeats because `Verbosity=1`. File birth/modification times from `S/evidence.log`, in UTC:

```text
search_start.txt: 2026-11-17 15:49:15.553625; contents 1794930555
sh_A.out: birth 15:49:15.551115; last write 16:57:24.951946
startB.txt: 16:47:16.226680; contents 1794934036
sh_B.out: birth 16:47:16.219831; last write 17:43:18.326491
```

These support an A observation interval of 68 min 9 s and a B interval of 56 min 2 s; B started 58 min 1 s after A. The saved `waitloop.sh` specifies `search_start+7200`, which supports an intended two-hour deadline. A quiet logfile does not establish when its process stopped. The retained evidence cannot certify the claimed 1:59:58/1:02 durations, SIGTERM exits, CPU utilization, first-77 time, or lack of crashes after the last output.

Reproduced both configurations using the author's binary with only `Verbosity=3` and an explicitly empty `InitialNetwork`, for eight seconds each (`S/sh_repro.py`, `S/cfgA_verbose.log`, `S/cfgB_verbose.log`). Both emitted the original initial lengths 115/111, reached 78, and recorded about 23.6/21.5 million iterations; B also printed `Restart.`. The audit driver terminated and reaped every trial, recording exit `-15`. These short reruns support that the configurations mutate, evaluate and restart; they do not reconstruct historical uptime.

Source tracing resolves the expansion mechanism:

- `A/dl_src/SorterHunter/SorterHunter.cpp:600-604` copies `FixedPrefix` literally. It is not mirror-expanded.
- Lines 627-643 load `InitialNetwork` as the mutable core, expand only that core, append the postfix, and test it on prefix outputs. Lines 669-679 append prefix to core for total size reporting.
- `hutils.cpp:148-159` inserts each supplied core gate and its mirror, except self-mirrored gates (`i+j=17`), which are inserted once. `sample_config.txt:53` explicitly warns that InitialNetwork is mirrored.

`S/sh_repro.py` ran five bounded starting-network trials. Full 77-gate record supplied directly in symmetric mode with no prefix prints `Initial network size: 149`. A correct compressed core, retaining one mirror representative with `i+j<=17`, starts at **77**, with no prefix, the 17-gate prefix, or the 21-gate prefix. For a fixed prefix, remove its gates before compressing the tail. An asymmetric full-record start also prints 77. Independent exhaustive enumeration confirmed zero failures for all three compressed-record expansions.

Thus InitialNetwork works. Neither self-mirrored gates nor the fixed prefix are silently duplicated in runs A/B, which have no InitialNetwork. The original 90-gate experiment's config and log are absent; 90 cannot be attributed to a specific erroneous encoding from retained evidence. Common full-record and compressed-tail inputs reproduce 149 and 77, not 90.

There is no hard target-length setting preventing 76. `SorterHunter.cpp:717-745` mutates and accepts any valid sorter, and `checkImproved:499-516` reports size/depth improvements without a 77 floor. Removal mutations can remove a self-mirrored gate (one gate) or a mirror pair (two gates). Symmetry and the fixed prefixes restrict the searched family, but both prefixes can represent the record exactly, as the 77-gate starts demonstrate. This does not establish that a 76-gate sorter exists in that family.

### 4. Independent single-deletion counts

Ran `OPENBLAS_NUM_THREADS=1 S/.venv/bin/python -u S/tests.py delete` on both original JSON files. Unlike the author's matrix routine, this code stores each binary input as a uint32 and updates it by XORing both bits only when the lower wire contains 1 and the upper wire contains 0:

```python
x = np.arange(1 << 18, dtype=np.uint32)
for deleted in range(len(gates)):
    v = x.copy()
    for k, (i, j) in enumerate(gates):
        if k == deleted:
            continue
        swap = ((v >> i) & 1) & (1 - ((v >> j) & 1))
        v ^= (swap << i) | (swap << j)
    bad = np.logical_or.reduce([
        ((v >> i) & 1) > ((v >> (i + 1)) & 1) for i in range(17)
    ])
    counts.append(int(bad.sum()))
```

`S/deletion.log` records all 77 counts for each network: baseline minimum **63**, deleting gate 33 or 40; supplied run-B network minimum **63**, deleting gate 33 or 34. Positions are zero-based. `bun frontier diagnose S/broken76.json --problem witness.sorting-network-size-18` independently rejected baseline-minus-gate-33: `value:76; valid:no; 63 of the 2^18 0-1 inputs end with wire 0 above wire 1`. Claim (d) holds for the supplied files.

### 5. Text against evidence and required corrections

The title and `attempt.yaml:6` accurately describe the observed best gate counts and the narrow logged SAT ranges. Their two-hour wording needs to distinguish a scheduled budget from independently recorded runtime. `kind:writeup`, CC BY 4.0 and both false declarations are correct (`attempt.yaml:4,43-46`). The writeup explicitly says it is not machine-checked (`writeup.md:3`), calls 77 a tie (`:8`), and does not claim a research success.

SAT log census, recomputed from JSON lines:

- `w=8`: 11 UNSAT lines, 11 offsets `{29,33,37,41,45,49,53,57,61,65,69}` (`logs/scan_w8.txt:1-11`). Timeouts: `s=17`, 240 s (`scan_first.txt:1`); `s=25`, 200 s (`scan_w8.txt:12`).
- `w=9`: 25 UNSAT lines and distinct offsets 44-68 (`scan_w9_11_10.txt:1-25`); `s=43` timeout, 150 s (`:26`).
- `w=10`: **26 UNSAT lines but 21 distinct offsets**, 47-67. Five offsets 47,52,57,62,67 were tested twice (`scan_w10_12.txt:1-5` and `scan_w9_11_10.txt:27-47`). `s=42` timeout, 200 s (`scan_w10_12.txt:6`).
- `w=12`: `s=65` timeout, 200 s (`scan_w10_12.txt:7`). No `w=11` result exists.

The listed ranges and timeouts at `writeup.md:23-28` are accurate. Correct the following statements:

1. `writeup.md:36`: "the space reachable by this heuristic with this prefix is exhausted quickly at 77; going to 76 needs a very different network or much longer runs". Replace with: "These two seeded runs did not report a sorter below 77. They do not establish exhaustion of the reachable search space or a necessary runtime or structural change."
2. `writeup.md:36`: "Every window up to 10 gates that finished was UNSAT, so the record is locally optimal against one-window replacement." Replace with: "Every logged shortening query that completed was UNSAT. This establishes no one-gate saving for the enumerated windows with the prefix and suffix fixed; unsampled windows remain open."
3. `writeup.md:41`: "Window SAT with a window of at most 10 contiguous gates of the record at any offset 43 or later: all UNSAT." Replace with the exact three sets above. In particular, `(s=43,w=9)` timed out, `(s=43..46,w=10)` has no UNSAT result, and the 8-gate scan sampled every fourth offset. Results for these windows do not cover all smaller windows and all offsets.
4. `writeup.md:46`: "Windows of 11 or more gates" under "What remains untried". Replace with: "11-gate windows were not run; one 12-gate window at s=65 timed out; other larger windows remain untested." `attempt.yaml:6` may retain "Not shown: anything about windows of 11 or more gates" if it means no result, but should mention the 12-gate timeout for clarity.
5. `writeup.md:47`: "Windows starting before gate 43" under "What remains untried". Replace with: "Most early windows remain untested; w=8 at s=29,33,37,41 was UNSAT, w=8 at s=17,25 timed out, and w=10 at s=42 timed out."
6. `writeup.md:36`: "windows beyond about 10 gates time out within 200 s because ...". Replace with: "The single tested 12-gate window timed out at 200 s. No timing evidence was retained for 11 or 14-28 gates, and these logs do not isolate the cause of solver difficulty."
7. `writeup.md:16`: "77 gates (12 layers) after at most 10 min", and `:8,36`'s ten-minute timing. Replace with: "Run B printed a 77-gate, 14-layer sorter and later a 77-gate, 12-layer sorter; its untimed log does not record when either first appeared. The saved JSON is the 14-layer one." Gate count remains 77 either way.
8. `writeup.md:15-17,32`: "Ran 1 h 59 min 58 s", "ran 1 h 02 min", "Stuck at 78 for the last 100+ minutes", "Both were stopped by SIGTERM", "about 60 to 90% of one core", and "no process crashed". Qualify these as the author's unverified runtime observations, or supply timestamped process/exit/CPU evidence. The retained files support the observation intervals in check 3, a two-hour intended deadline, and no logged improvement below 78/77. They do not establish these exact timings, exits or utilization. Use "scheduled 2 h budget" in the title/claim until supported.
9. `writeup.md:40`: "both seeds stop at 77 or 78" as advice not to repeat the method. Replace with: "These runs reported best sizes 78 and 77; another seed, initialization, or continuation could behave differently."
10. `writeup.md:18`: "InitialNetwork did not work ... started from 90 gates ... probably how self-mirrored gates or the prefix are handled". Replace with: "The initial trial was abandoned after an unexpected reported size; its configuration and output were not retained. Correctly compressed InitialNetwork inputs start at 77. The historical 90-gate observation cannot be diagnosed exactly from the saved files."
11. `writeup.md:20`: "start from 100 vectors (60 ... 40 random)". Replace with: "start with up to 60 failing and 40 shuffled prefix-output indices, then deduplicate; actual distinct counts can be lower." The rerun tail windows encode 30,33,36 vectors, not 100 (`window_sat.py:103-109`).
12. `writeup.md:54`: "scripts/ has everything run". Replace with: "scripts/ contains the final versions of the listed scripts and the two main configs. Earlier scan configurations, the failed InitialNetwork input, baseline.json, and the SorterHunter source/build are not included in the attempt." `writeup.md:28` itself acknowledges earlier scan parameters were edited. No source revision or dependency lock was retained in the attempt, so exact historical reproduction needs the preserved scratch and additional provenance.

`attempt.yaml:28-40` discloses the stated author/planner models and both search engines. NumPy performs exhaustive candidate validation (`window_sat.py:12,42,123-124`) but has no tool entry; add `NumPy` with its evaluation role before affirming complete disclosure. Python-sat is the CaDiCaL binding; the prose names it and NumPy, while clang++ and uv are described as build/setup tools. No evidence of another author model appears in these files; files alone cannot establish that none was used. Both declaration flags remain false.

Verification of the report's repository context: `bun run check` ran the exact repository gate. Typecheck passed; tests reported **426 pass, 1 skip, 0 fail, 2426 expect() calls**, across 34 files in 9.51 s. The skip is actionlint. The final validation stage failed only because this attempt's declarations are intentionally unconfirmed, so the overall command exited 1. Left those declarations unchanged. `bun frontier check P` returned `unchecked: Writeups are not machine-checked.` Lean tests were not applicable.

### 6. What a stronger attempt should try

Use corrected 77-gate starts rather than abandoning InitialNetwork: asymmetric mode accepts the full record; symmetric mode accepts the compressed mutable tail after removing the literal fixed prefix. Search from both the record and the distinct run-B construction, and from the retained 78-gate/11-layer alternative. The input configurations and exhaustive checks in check 3 establish these starts are usable.

Vary seeds, greedy or unrelated prefixes, and asymmetric mode; the original `cfgA.txt` and `cfgB.txt` both fix record-derived symmetric prefixes. Their logs provide no experiment for those alternatives. Address the actual SAT coverage gaps, especially untested offsets and larger windows, reorder commuting gates before choosing windows, and consider noncontiguous or mirror-linked windows and free-tail synthesis. The current encoder uses pairwise exactly-one clauses over all 153 pairs at every gate (`window_sat.py:51-55`); compare sequential/cardinality or layer encodings rather than inferring from one timeout that larger synthesis is impractical. Do not prune legal pair choices without a justified equivalence or a clearly stated restricted search.

## Deviations

Could not reconstruct the exact historical 90-gate InitialNetwork trial: neither its input nor output exists among the supplied retained files. Executed full-record, compressed-record, compressed-tail and asymmetric controls instead, establishing the expansion semantics and working 77-gate starts. The unexplained historical number remains unverified.

Could not certify the original whole-budget runtime, stop signals, utilization or time to first 77; timestamped heartbeats, exit records and CPU samples were not retained. Reported the strongest intervals supported by file metadata and tested present-day mutation/restart behavior instead.

No attempt or problem source was changed. An initial Python import generated a bytecode cache under the attempt's scripts directory; removed only that audit-generated cache and disabled further bytecode writes. `git diff` and `git status --short` confirmed no tracked attempt changes. Only the two explicitly requested report paths are committed; the second is an identical handoff copy for task routing.

The requested full repository gate cannot pass while the binding false-declaration requirement holds. Its typecheck and tests passed; the intentional validation failure is recorded above.

## Concerns

The tested SAT negatives are sound under the inspected encoding, but no independently checked UNSAT proof certificates were retained. Only the three requested 18-wire negatives were rerun; the rest were checked through source analysis and the logged census. An UNSAT solver answer is not a Frontier verdict on this writeup.

Source provenance is incomplete: the attempt identifies a date and master branch rather than a revision, and retains no original build log or dependency lock. The available source and executable were sufficient for the short controls, but cannot prove the author's "one line added" provenance claim or all historical process behavior.

Blanket recommendations against repeating these methods would mislead later work. Retain the exact negative windows and the observed best sizes; remove claims of heuristic exhaustion and general local optimality.

## Follow-ups

Return the attempt to its author for the check-5 corrections, include the working InitialNetwork recipe, and disclose NumPy before any declaration approval. Preserve the historical runtime statements as unverified observations unless independent process records can be recovered.

A new search should save immutable configs, the baseline and starting objects, source revision, dependency versions, timestamped iteration/checkpoint logs, peak memory/CPU samples and explicit start/end/exit records. Keep SAT proof certificates where supported and positive controls beside the encoder. Re-run the corrected initialization and broader search choices from check 6 with a fresh budget; do not count these seconds-long audit controls as the missing research run.
