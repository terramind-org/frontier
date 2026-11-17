## Done

Created `attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40/`, kind `writeup`, titled “Exclusion plateaus, stabilizer models and full-line SAT, 104.4 min of a 120 min budget, no cap above 512 found”. It contains the writeup and 15 original source files. Both declarations remain false; no Frontier submission or review was run.

Largest valid cap: 512, a tie. Research walks retained three labelled 512-caps; the full stabilizer model adds a fourth. All four have one signed-coordinate canonical class and minimum outside blocking count four. One complete saved 448-cap grew to the original 512-cap; the other stayed at 448. The independently constructed 112-by-4 literature product grew from 448 to 449; its continuation remained at 449. The 45-by-9 product stayed at 405.

Symmetry results (incumbent / upper bound): 124 variables, 512 / 512, OPTIMAL; 1,220 variables with weakened hint, 508 / 3,872, FEASIBLE; 300 variables, 512 / 1,392, FEASIBLE; 1,220 variables with complete hint, 512 / 3,872, FEASIBLE. The 512 bound applies only to the full signed-coordinate stabilizer restriction. Full-space SAT at cardinality 513 returned UNKNOWN after 600.32 seconds, with no witness or global bound.

Search envelope: 2026-11-17 19:07:18–20:51:40 UTC, 104 minutes 22 seconds of the 120-minute budget. Completed search processes exited 0. The dropped initial calibration exited 1; the deliberately stopped secondary walk exited 143. All search processes have ended.

Evidence remains in worktree `tame-aurora`, `.terramind/scratch/capset8-r2/`: phase JSONL logs and source snapshots, start/end/exit files, `visited/`, `interruptions.jsonl`, `summary-final.json`, `final-metrics.json`, verifier outputs and `repo-check.out`. The exact inner checker rechecked 133 retained files. Calibration restored five deleted baseline points, found the excluded equal-size refill, grew a dimension-four cap from 12 to 20, restored the region control from 19 to 20, and passed independent coordinate/orbit checks. The SAT encoder separately found 20 from a 12-point hint. The repo verifier accepted the baseline, products and reported gains, and rejected the broken 513 control.

Verbatim output of `bun frontier check`:

```text
$ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

The attempt check exits 0. Attempt-specific validation exits 1 solely for the protected false declarations. Python source compilation, shell syntax and file/privacy checks pass. `bun run check` passed TypeScript and reported 434 pass, 1 skip, 0 fail across 34 test files; its final validation exited 1 for false declarations and pre-existing absolute paths in the matrix-multiplication and Schur attempts.

## Deviations

The first incremental symmetry encoder failed its known-20 calibration and was dropped. Complete orbit-line models replaced it. Every sampled region-plus-boundary removal freed the entire space, so all 24 oversized CP-SAT models were skipped; a complete unrestricted SAT decision model at 513 replaced maximization for that case.

The second saved-448 walk was stopped after it recovered the original 512-cap, releasing its core for full-space SAT. Its 65 completed solver calls and interrupted call 79 are recorded explicitly. A complete-hint retry replaced the unproductive weakened-hint symmetry configuration. The final continuation used the 449 literature-product branch to preserve starting-point diversity. The budget was an upper limit; 104 minutes 22 seconds were used.

## Concerns

No record was beaten. The remaining subgroup bounds are loose, and SAT UNKNOWN gives no impossibility result. Canonicalization covers coordinate permutations and independent negations, not the full affine group. Historical 448 inputs, coordinates and detailed logs remain in scratch for independent audit rather than being embedded as data dumps.

Two single-worker search streams were configured; no OS resource sandbox was installed. A brief independent control overlapped both streams. Peak RSS was logged per process, with a maximum of 1.324 GiB; this is not an aggregate resource certificate. Scratch usage was 164M.

The full repository gate remains blocked by deliberately false declarations and existing local-path entries in `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/writeup.md` and `attempts/witness.schur-7/20261117-terramind-com-c8ca32/run.sh`. Existing attempts were left unchanged. The branch includes the required merge of `origin/main`.

## Follow-ups

Run the independent cross-model audit against retained scratch, then the closing check on the merged swarm branch. Land the existing path corrections through their owning tasks. Further research should seek different 512 canonical classes, exclude known labelled images more effectively, and strengthen the unrestricted SAT model. The retained smaller-cap trajectories are available as future starts.
