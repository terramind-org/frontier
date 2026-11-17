## Done

I corrected `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d/attempt.yaml` and `writeup.md` against `audit-matmul5-r2.md` (gpt-6.2-sol, outcome OVERSTATED). I ran no search and produced no new result. No source, script or log file in the attempt changed. The kind stays `writeup`. The declarations stay `{ rights: false, disclosure_complete: false }`.

Required corrections (old → new):

1. Nonexistence wording.
   - `attempt.yaml` claim. Old: "No GF(2) scheme below 93 was found, so no integer witness exists." New: "This run found no GF(2) scheme with at most 92 terms and produced no integer witness at that size; the negative result covers reported descent minima and saved schemes."
   - `writeup.md` Summary. Old: "...so nothing went to the lift at a rank that could beat the record, and no witness exists." New: "This run found no GF(2) scheme with at most 92 terms and produced no integer witness at that size. Nothing went to the lift at a rank that could beat the record. The run gives no lower bound." The statement that the run gives no lower bound or nonexistence result stays in the claim and at the top of the writeup.
   - Algorithm 1 in the claim. Old: "(Moosbauer-Poole Algorithm 1, L=1e8, M=5e4)". New: "using an adaptation of Moosbauer-Poole Algorithm 1 with default settings L=1e8, M=5e4 and one variant run at L=2e8, M=1e5".
2. Block-count rule.
   - Summary. Old: "So rank 92 needs a 2-block start (3·30 + 2) and rank 91 a 1-block start (3·30 + 1)." New: "While the fixed-term count remains unchanged, two blocks give ranks 3k + 2 and one block gives ranks 3k + 1 ... Collapses can change this count. For example, four and five fixed terms also permit 91 and 92 with 29 full orbits."
   - Not covered. Old: "(3- to 5-block starts can only give ranks 3k + 3 or more)". New: the same auditor wording.
   - I also softened the round-one sentence from "kept its 3 fixed terms, so it could not reach 92" to "kept its 3 fixed terms throughout, so it stayed on ranks 3k + 3".
   - The off-pattern paragraph in Runs now says that fixed terms can also cancel and that the count can change while the rank stays on the pattern. It cites the auditor's replay: the first p4-41 descent reached 107 with five fixed terms, and the 3-block calibration logged three fixed terms at its minima.
3. Moves and descent.
   - Old: plus-transition "..., rank + 3, on two random orbits ...". New: "A plus-transition usually adds a full orbit. Its output orbits can collapse, and fixed terms can cancel."
   - Old: "Descent (Algorithm 1): random flips; ...". New: "Descent: the loop adapts Algorithm 1 with finite move-selection retries, a best-relative plus cap in later runs, and a best-state report at descent end. It records minima after flips and optional greedy reductions."
   - Added: duplicate full orbits remain in the list until a later reduction removes them. Added: the cap removes paths from the printed Algorithm 1, and cap skips were not logged. Added: L and M count one flip per orbit move here and three upstream.
   - Added a "Tracking limits" section with the planted plus-transition drop and the checks of the 57 saved schemes.
4. Calibration counts. Old: "150 s on 2 cores gave lowest 96 over 18 descents; with an extra greedy reduction scan, 99 over 4 descents". New: "The two 150-second calibration processes reported 14 rows for ordinary flips, including one time cut, and 4 rows for greedy, including one time cut. The respective minima were 96 and 99."
5. Counting convention.
   - The claim and the Summary table now say, for the {5} start: "108 unique descents begun, 107 with a reported best, 103 completed without a stall or time cut. Of those 103, 23 finished at 97. Three more reported 97 before stalling or being cut." The table states the reported/regular convention for every start: {4,1} 237/234 with 20 of 234 at 95; {3,2} 113/112; {2,2,1} 116/115.
   - Pool: "44 reported rows, one further descent killed in progress". 0.6% became 0.64%, with the definition (sum of within-descent distinct sampled hashes divided by samples) stated in Method.
   - Kicks: 17% became 16.5%, marked as a lower bound because one kick descent hit the four-million-hash ceiling. "About 90% in fresh descents" became the auditor's per-start figures, 74.7% to 91.5%. I divided its "Distinct/sampled" columns to get them.
   - Inferred: "99.4% repeats ... walk is confined (93 for {2,2,1}, 95 for {4,1})" now reads "In restarts from the five rank-95 {4,1} states, 99.36% of sampled hashes were within-descent repeats". The audit had no restart evidence at 93.
6. Success per flip. Old: "The descent finds 93 from the paper's start within a minute, so its success rate per flip is not obviously worse than the paper's, but the throughput is lower." New: "This build reached 93 from the same start in under a minute in the reported runs. The paper gives a laptop time and a throughput range across inputs and hardware. These figures alone cannot compare success per flip." I added the flip-unit difference. "6 to 10 million" became the recount's 5.9 to 10.3. I removed "throughput a few times lower than the paper" from Inferred and "the paper's implementation is several times faster" from the follow-ups. The audit's same-machine figure is 1.25 times.
7. Equivalence. Old: "...at least 5 classes ... So the search finds rank-93 schemes not equivalent to the published one." New: the auditor's paragraph ("Seven of nine GF(2) schemes differ from the Lille baseline by the aggregate factor-rank invariant. ... leave prior discovery and equivalence within matching signatures open."), plus the frequencies and "at least six GF(2) symmetry classes". Added to Measured: "The 95 and 97 reproduce endpoints already named in the upstream 5x5 run manager", with the upstream link.
8. Files and lift.
   - Old: "with `--paper-plus` and no `--plus-cap` the RNG path is the same." New: "Pass an explicit high cap to the shipped code for an uncapped reproduction. Its default cap is 30."
   - Added a scratch-independent `./c3flip ...` launch line. I checked its flags against the shipped arg parser.
   - `launch.sh`, `autolift.sh` and `tune.sh` are now labelled as a recipe for the original scratch layout. I left the scripts themselves unchanged, as the rules require.
   - The lift equation is now `J(x0)·y = −F(x_m)/2^m mod 2`, with the note that the sign has no effect in characteristic two.
   - Added: the in-script exact test uses `int64` and the repository verifier is authoritative. Added: the lift's restricted choices mean a failure would not be an obstruction.

Item 2 (auditor's measurements, all marked as the audit's):
- The "Independent audit" section carries:
  - the 2x2 replay: 20 runs reached 7, none reached 6;
  - the 3x3 replay: 20 of 20 reached 23 at L=300000, M=1000;
  - the 4x4 one-block runs (16×49, 4×52) and the upstream 4x4 C3 × Z2 runs (20/20 at 49);
  - the 600-second calibration replays: 57 and 58 completed, 93 hit 4 and 3 times, first hits at 256 s and 5 s, the rank histogram, 14.10 and 13.95 M orbit flips/s, 119 and 103 MiB;
  - the negative replay of the first three p4-41 descents (107, 95, 98, same hashes);
  - the upstream comparison (1 in 12 runs at 93, 17.59 M orbit flips/s, about 1.25×);
  - low-rank yield per core-hour: default 16 rank-95 rows in 3,506 core-seconds (16.4/h), doubled 4 in 2,041 (7.1/h);
  - the 11 diagnosed lifts.
- Runs gained:
  - 225.1 core-minutes and 100.42 billion flips, plus at least 1.074 billion in killed work;
  - "The logs give sample counts but no exact unique-state totals, CPU utilisation or memory use";
  - when the best values first appeared (95 at 5 min 34 s into the first {4,1} run, 98 at 37 s, 97 at 60 s; none improved; the last 95 at 21:14:04);
  - 898 plus moves against 821 reductions in the overflowed descent.
- Calibration now says that the retained self-test, 2x2 and 3x3 logs are incomplete and that the audit's reruns reproduced the outcomes.
- Inferred carries the auditor's geometric extrapolation (1.49% per descent, 67 descents, about 3% chance of zero hits, 1.27% upper limit), with "expected time to 92 unresolved".
- The tracking omissions are in "Tracking limits":
  - rank after each kind of move not recorded;
  - duplicate full orbits not cancelled;
  - capacity handling (the check runs before the greedy/plus call; a possible `renameOcc` abort);
  - cap skips not logged;
  - the 64-draw stall.

  "Stuck (no flip available)" is now "stuck (64 failed flip draws)".

Items 3 to 8:
- Follow-ups ("What a later attempt could try"): the audit's leads come first, each labelled. Method: fix the tracking omissions before any long run. Time: the 32 core-hour split (24 {4,1} / 6.4 {5} / 1.6 {3,2}, control settings, the first-four-hours sub-split, cap 30, about 3,700 descents, skip pool restarts). Method: save {5} schemes through rank 100 and test the diagonal-split identity (six terms plus I^{⊗3} = X^{⊗3} + Y^{⊗3} over GF(2)) on rank-97 states over the 15 splits. Method: keep C3 × Z2 out until it is reproduced at n = 4. Time (throughput): profiling, LTO and PGO. After those come the 6x6 trick (method), the other partition types (method) and the lift note.
- Title: unchanged. The audit says it is accurate.
- Claim: rewritten as shown below.
- Disclosure: kept every entry. Added `Frontier` (tool, diagnosis), `uv` (tool, lift-runner) and `gpt-6.2-sol` (openai, auditor). I am claude-opus-5-5, the author model, so there is no corrections entry.
- Privacy: `grep -rn -E "/Users/|/home/"` on the attempt directory returned no match (exit 1). No personal names.
- "Independent audit" section added. It says what was re-run and what was confirmed, that statements were corrected, and that the audit is an opinion backed by reruns, not a repository check. The report is not pasted.
- Wording scan: no "exhausted", "locally optimal", "rigid", "does not work", "do not repeat", "solved" or "confined" remain. The scan's only hit is "unresolved".

Title in full: "C3 flip descents from 2-block {4,1},{3,2} and 1-block diagonal starts, scheduled 2 h, no rank-92 scheme found (best GF(2): 95, 98, 97)"

Claim in full: "Records an unsuccessful 2-hour, 2-core search for a 5x5 matrix multiplication scheme of rank 92 or less: C3-symmetric flip-graph descents over GF(2) from diagonal-partition starts, using an adaptation of Moosbauer-Poole Algorithm 1 with default settings L=1e8, M=5e4 and one variant run at L=2e8, M=1e5. Lowest reported GF(2) ranks: 95 from {4,1} (237 reported fresh descents, 234 regular, i.e. without a stall, overflow or time cut, 20 of them ending at 95), 98 from {3,2} (113 reported, 112 regular), 97 from the 1-block start (108 unique descents begun, 107 with a reported best, 103 regular, 23 of those ending at 97), against targets 92, 92 and 91. This run found no GF(2) scheme with at most 92 terms and produced no integer witness at that size; the negative result covers reported descent minima and saved schemes. Calibration: the same code reached 93 from the paper's {{1,5},{2,4},{3}} start in 8 of 115 regular descents, and a C3-symmetric Hensel lift turned the published scheme's mod-2 reduction and every rank-93 scheme found into integer schemes the repository verifier accepts at 93 (ties, not improvements). An independent audit by a second model re-ran controls and recounted the logs; its measurements are marked in the writeup. This writeup is not machine-checked and gives no lower bound or nonexistence result."

`bun frontier check attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d` (exit 0):

```text
$ bun src/cli.ts check "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun frontier validate attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d` (exit 1, only the declarations complaint):

```text
$ bun src/cli.ts validate "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d"
attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-1de22d/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

`bun run check`: `tsc --noEmit` passed; 434 tests pass, 1 skip, 0 fail (2,481 expect() calls). It exited 1 at validate, which lists only the 13 attempts on this branch whose declarations are intentionally false.

## Deviations

- I wrote the handoff under both names the brief gives, `correct-matmul5-r2.md` and `correct-the-c3-descent-writeup-3qa5m.md`, with identical content. The audit did the same.
- The audit asked to "ship a scratch-independent launch example or label the shell scripts as a scratch layout recipe". I did both in `writeup.md` and did not edit the scripts. The rules allow changes to search files only for privacy.
- I did not use the audit's statement that the logs lack fixed-term counts at minima. Each `DESCENT` row in `c3flip.cpp` logs `orbits=` and `fixed=` for the descent's best state. The retained logs show 95 = 31 + 2 fixed, 97 = 32 + 1 and 98 = 32 + 2 at every reported minimum of those ranks, so the Summary column's decompositions stand. The writeup says intermediate counts are not logged. This matches the audit's follow-up to log counts at minima.
- Beyond the audit's bullets, and in line with them, I changed "about 90% in fresh descents" to the auditor's per-start ratios and "within a minute" to "in the reported runs". I also removed the unsupported "walk is confined ... 93 for {2,2,1}".

## Concerns

None. I found nothing in the audit contradicted by the attempt's files. The one nuance on fixed-term logging is under Deviations.

## Follow-ups

None.
