## Done
Attempt directory: `attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f`, kind `writeup`.
Title: "SorterHunter (2 prefixes) plus window SAT on the 77-gate record, 2 h, no 76-gate network found".

`bun frontier check` output (verbatim):
```
$ bun src/cli.ts check "attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```
`bun frontier validate` complains only that declarations are false (as expected).

Result: record 77; best reached 77 (SorterHunter run B reproduced a valid 77-gate network, `diagnose`: "ties the best known value"; run A best 78). The verifier says it ties, does not beat; no 76-gate network found, so no witness attempt. For 76 gates the fewest unsorted 0-1 inputs reached was 63 of 262144 (deleting the best single gate from the 77-gate network). Window SAT (CaDiCaL): UNSAT for 8-gate windows at 11 offsets, 9-gate windows at offsets 44-68, 10-gate windows at offsets 47-67 (prefix and suffix of the record fixed); timeouts at 9-gate offset 43, 10-gate offset 42, 12-gate offset 65. Wall clock: 21:19:15 to 23:19 IST (120 min). Run A SorterHunter 2 h on core 1; core 2: window SAT ~1 h then SorterHunter run B ~1 h. Search exit status: processes had no exit of their own and were stopped by SIGTERM at the deadline.
Baseline: the 77-gate network from Dobbelaere's page encoded and diagnosed valid at 77 before the search.

## Deviations
- The brief's SAT line (fix first L layers, leave the whole tail free) was replaced by window SAT (prefix AND suffix fixed, w-1 gates in the window): a free 50+-gate tail is far beyond CaDiCaL in the time available.
- Core 2 was moved from SAT to a second SorterHunter run after ~1 h because windows over 10 gates only time out.
- SorterHunter's `InitialNetwork` seeding from the record did not work in symmetric mode (started from 90 gates), so both runs started from scratch with the record's prefix fixed.
- The own bit-parallel C checker from step 2 was not written: SorterHunter has its own, and the SAT loop checks via numpy; every reported candidate was tested with `bun frontier diagnose`.
- I added `scripts/` and `logs/` (<150 KB) to `files` in attempt.yaml.

## Concerns
- Both cores were shared with five other searches (SorterHunter got 60-90% of a core), so effective compute was under 2 core-hours each.
- The "window UNSAT" statements are exact only for the window form (contiguous in the record's layer order, prefix and suffix fixed, gate choices from all 153 pairs); they do not prove optimality of the record.
- scripts/scan.py is the last of four edited launches; the logs show the parameters used each time.

## Follow-ups
- Windows of 11+ gates with a better encoding (symmetric windows via the record's mirror symmetry, restricted pair sets), windows before gate 43, more SorterHunter seeds/cores with other prefixes, asymmetric mode, starting from the 78-gate 11-layer network.
