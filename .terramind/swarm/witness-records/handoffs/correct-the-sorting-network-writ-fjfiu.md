## Done

Edited only `attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/{writeup.md,attempt.yaml}`; no search, no change to logs/ or scripts/. Ran `bun install`. Section references are to the new writeup.

### The 12 audit items (old wording -> new wording)
1. Line 36 "space reachable by this heuristic with this prefix is exhausted quickly at 77; going to 76 needs a very different network or much longer runs" -> "Why it stalled": "These two seeded runs did not report a sorter below 77. They do not establish exhaustion of the reachable search space, or that a different runtime or a different network would be needed."
2. Line 36 "Every window up to 10 gates that finished was UNSAT, so the record is locally optimal against one-window replacement" -> "Every logged shortening query that completed was UNSAT; this establishes that there is no one-gate saving for the enumerated windows with the prefix and suffix fixed, and unsampled windows remain open." No "locally optimal" anywhere.
3. Line 41 "Window SAT ... at most 10 contiguous gates at any offset 43 or later: all UNSAT" -> exact UNSAT sets (w=8 at 29,33,...,69; w=9 at 44 to 68; w=10 at 47 to 67, 21 distinct, 26 lines because 47,52,57,62,67 ran twice), exact timeouts (w=8 s=17 and 25; w=9 s=43; w=10 s=42; w=12 s=65) and "Windows never run" (no w=11; w=10 at s=43 to 46; w=9 below 43; w=8 other offsets; most windows before 43; 13 to 28 gates). Checked against logs/scan_*.txt with a script (62 UNSAT lines, the five non-UNSAT lines are exactly those timeouts).
4. Line 46 "Windows of 11 or more gates" untried -> "no 11-gate window was run; the one 12-gate window at s=65 timed out; windows of 13 to 28 gates untested".
5. Line 47 "Windows starting before gate 43" untried -> "most windows before offset 43 are untested", with the w=8 s=29..41 UNSAT and the s=17, 25 / s=42 timeouts named in the same bullet and in the method section.
6. Line 36 "windows beyond about 10 gates time out within 200 s because ..." -> "The single tested 12-gate window timed out at 200 s; no timing evidence was kept for 11-gate or 14 to 28-gate windows" and "The logs also do not isolate why a window times out".
7. Line 16 "77 gates (12 layers) after at most 10 min" (and the ten-minute timing at lines 8, 36) -> run B "printed a 77-gate, 14-layer sorter (logs/sh_B_output.txt:100) and later a 77-gate, 12-layer sorter (:102); its log has no timestamps"; the saved JSON is the 14-layer one. The ten-minute figure survives only inside the author's-observation bullet.
8. Lines 15-17, 32 durations "1 h 59 min 58 s", "1 h 02 min", "stuck at 78 for the last 100+ minutes", SIGTERM, "60 to 90% of one core", "no process crashed", "after at most 10 min" -> all marked as the author's own unverified observations in one bullet and in "Wall clock and exit status"; retained evidence stated (68 min 9 s of output for A, 56 min 2 s for B, B 58 min 1 s after A, `waitloop.sh` deadline start+7200 s). "2 h" became "scheduled 2 h" in title, heading and claim. No log supports the original statements (Verbosity=1, no timestamps), so none kept as fact.
9. Line 40 "both seeds stop at 77 or 78" as advice -> new section "What these runs do and do not rule out": these two seeds with these two prefixes reported best sizes 78 and 77; another seed, initialization or continuation could behave differently; listed windows are UNSAT as stated.
10. Line 18 "InitialNetwork did not work ... 90 ... probably how self-mirrored gates or the prefix are handled" and "Do not use InitialNetwork in symmetric mode..." -> method bullet says the trial was abandoned after an unexpected size, input not kept, cause of 90 unknown; new section "InitialNetwork in symmetric mode" gives the audit finding (see item 2 below).
11. Line 20 "start from 100 vectors (60 ... 40 random)" -> "start with up to 60 failing and 40 shuffled prefix-output indices, deduplicated (so the actual count can be lower ...)". I added measured numbers from the logs: 30 to 118 vectors encoded out of 30 to 1343 distinct prefix outputs in the UNSAT windows (computed from logs/scan_*.txt).
12. Line 54 "scripts/ has everything run" -> "scripts/ holds the final versions of window_sat.py, scan.py, best_from_sh.py, waitloop.sh and the two main configs cfgA/cfgB (no binaries). Not included: earlier scan configurations, the failed InitialNetwork input, the baseline file, and the SorterHunter source revision and build" (no commit hash, no build log, no lock file).

### Items 2 to 6 of the brief
- Item 2: done. InitialNetwork passage replaced (section "InitialNetwork in symmetric mode": symmetric mode mirrors every InitialNetwork gate, self-mirrored i+j=17 once, FixedPrefix not mirrored; full record gives 149; compressed core with i+j<=17 after removing the prefix starts at 77 with no prefix, the 17-gate or the 21-gate prefix; asymmetric accepts the full record; the 90-gate input was not kept, cause unknown). "Do not use InitialNetwork ..." deleted. First bullet of "What remains untried" is now "Start SorterHunter from the record, and from the distinct run-B 77-gate network, with a correctly compressed InitialNetwork ... the most direct search that was not actually run."
- Item 3: done. "What a later attempt should not repeat" replaced by "What these runs do and do not rule out" (two bullets).
- Item 4: done. New title and claim below; `kind: writeup`; declarations unchanged (`rights: false`, `disclosure_complete: false`).
- Item 5: done. Added `NumPy` (provider tool, role exhaustive candidate validation) and `gpt-6.1-sol` (provider openai, role auditor); existing entries untouched. Writeup method also names NumPy as a tool.
- Item 6: done. New "Independent audit" section (controls: planted redundant gate removed; 8-input bubble sort shortened; optimal 8-input windows UNSAT; three reported windows re-solved UNSAT; deletion count 63 recomputed; measured results reproducible, several conclusions overstated, text corrected; opinion backed by reruns, not a repo-verifier check; no UNSAT proof certificates kept). Report not pasted.
- Item 7: wording rules kept (no "solved"; 77 "ties the record and does not beat it"; "not machine-checked" at the top and in the claim).

### New title
SorterHunter (2 seeded runs, record-derived symmetric prefixes) plus window SAT on the 77-gate record, scheduled 2 h, no 76-gate network found

### New claim (in full)
A failed search, on a scheduled 2 h budget, for an 18-input sorting network with 76 gates or fewer; no such network was found and no witness is submitted. Shown (by the retained logs, not machine-checked; run durations and exit signals are the author's unverified observations): two SorterHunter runs (seeds 101 and 22, symmetric mode, no InitialNetwork) with the first 2 or 3 layers of the 77-gate record fixed reported best sizes 78 and 77 (77 only ties the record); and CaDiCaL answered UNSAT, with prefix and suffix fixed and no proof certificates kept, to a one-gate-shorter replacement for these contiguous windows of the record: 8 gates at offsets 29, 33, ..., 69 (11 offsets), 9 gates at offsets 44 to 68, 10 gates at offsets 47 to 67. Timed out without an answer: 8 gates at offsets 17 and 25, 9 gates at offset 43, 10 gates at offset 42, and the single 12-gate window at offset 65. Not run: any 11-gate window, 10-gate offsets 43 to 46, most windows before offset 43, windows of 13 to 28 gates. Not run either: SorterHunter started from the record with a correctly compressed InitialNetwork (in symmetric mode InitialNetwork is mirrored, so the mutable core must be given as one gate per mirror pair; the original 90-gate trial was not kept and its cause is unknown). A second model audited the SAT encoder and the 63-input deletion count, found the measured results reproducible and some conclusions overstated; the text was corrected. This writeup is not checked by any verifier.

### `bun frontier check attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f` (exit 0)
```
$ bun src/cli.ts check "attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

### `bun frontier validate attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f` (exit 1, only the expected declarations complaint)
```
$ bun src/cli.ts validate "attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f"
attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations
- I added facts the auditor did not list but the logs support, all computed from logs/scan_*.txt: the w=10 duplicates (26 lines, 21 distinct), and the encoded-vector range (30 to 118 of 30 to 1343 distinct prefix outputs). I first wrote a wrong range from the audit's three reruns and corrected it against the logs before committing.
- The "Why it stalled" heading is kept (with new content) so the section order is familiar; "What a later attempt should not repeat" was replaced by "What these runs do and do not rule out".
- The adjacent-repeat symmetry-break is described with the auditor's finding (it loses nothing for the prefixes of the logged UNSAT windows) instead of the original "loses nothing since a repeated gate is redundant".
- The brief names the handoff `correct-sortnet18.md`; the generic handoff rule names `correct-the-sorting-network-writ-fjfiu.md`. I committed identical copies of both.
- Old 5-gate sanity check (s=70) kept; the audit reran it.

## Concerns
- The claim in `attempt.yaml` is now long (several sentences). It is accurate, but Agrim may want it shorter before submission; the `bun frontier show` listing uses only the title.
- I found nothing in the audit that I think is wrong. I did not independently rerun any solver (brief: no search); statements about the audit's reruns are the auditor's, reported as such. Run-B "first 77 at about 10 minutes" and all duration/exit/CPU statements remain unverifiable.
- `validate` exits 1 solely because the declarations are false, as required.

## Follow-ups
None.
