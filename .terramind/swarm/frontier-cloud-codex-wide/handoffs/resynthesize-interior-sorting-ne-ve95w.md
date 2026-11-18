Outcome: done

## Done

Recovered the original `bec2cfd4` commit object from reachable local Git
objects, beginning this work from the requested clean `13fdeb47` ancestor.
The original c2-2 manifest's retained files validate; its omitted oversized
DRAT stream was reassembled from seven individually hashable parts and matches
both the original compressed digest
`26281a69dde5616b3cb3c08d23883937b5dee6114eee6f5111edc40b8c3b6fe4`
and original decompressed DRAT digest
`df51b9bb7254baa1f0919fd853f76f3aeb5279c26df626af5aba21974693186e`.
The CNF decompressed digest also matches
`0b0443fa39a72b31e72ff24baa20ba1096a7d912038ac55724863747e1cc82f9`.

The new recovery bundle is
`.terramind/scratch/sort18-c2-2-recovered/`. It retains the source, baseline,
commands, checker log, original manifest, hashes, and seven proof chunks of at
most 25,165,824 bytes, with exact reassembly instructions. The original 166.6
MiB blob is not in this branch's outgoing ancestry.

`[55,66) -> 10`, seed `5511`, is fresh and non-implied by the certified
exterior-window ledger because it starts before `[56,67)`. The corrected
complete initial CNF included every 104 reachable prefix state (24,590
variables; 1,123,571 clauses). One-core CaDiCaL returned UNSAT in 218.722s;
the 600s supervisor exited 0. Independent DRAT-trim exited 0, reported `s
VERIFIED`, and took 67.019s. Its compact replay bundle is
`.terramind/scratch/sort18-c5/`; it holds the baseline, encoder, commands,
logs, compressed CNF, three <=24 MiB proof chunks, and decompression hashes.

The earlier run in `incomplete-initial-100-state-query/` was detected to have
encoded only 100 of 104 states. Its log is preserved as a failed control; its
raw CNF/proof are deliberately not versioned and its UNSAT result is not used.
No 76-comparator candidate was produced. `bun run check` passed: 434 passed,
1 skipped, 0 failed.

## Deviations

The requested branch name already names the recovered `bec2cfd4` branch, so
to avoid altering it this work used
`swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c2-2-recovery`
from `13fdeb47`. The original c2-2 manifest cannot directly validate its
single DRAT filename because that file is intentionally absent; all remaining
entries validate and the concatenated chunk stream validates to its recorded
compressed and decompressed hashes.

## Concerns

Both exclusions apply only to fixed prefix/suffix windows of this particular
77-comparator baseline; neither is a global lower bound. `[58,70)`, `[59,75)`,
and `[42,54)` remain unresolved.

## Follow-ups

Select a fresh non-implied interval outside `[55,66)` and the later certified
exterior windows, retaining all reachable prefix states before the first solve
and keeping traces split below the remote per-file size limit.
