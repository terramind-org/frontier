Outcome: done

## Done

Recovered PR 86 commit `8f88f3bd43ea549c5040b74a8d65e8be27eab27a` and verified the c8 seed (`80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`), unchanged screen (`f5e0f615b98328989d26ba77fe7f08f3bcb424b225a2fab5e012d7452538238d`), checkpoint, and accepted c7 restart-control trace (`3f848349132bdcc042c056f0b86fe625537afdcf0b9474f6405865bf0d118eef`).

The CPU-0 run resumed at neighbour 3, support 237686 (`[7,10,14,15,16,21,22]`). It passed the planted seven-to-one control, ran 1500.006588 seconds, and covered 540172 new supports with zero reductions: neighbour 3 remaining 7471 supports (658 low-flattening); neighbour 4 all 245157 (31021); neighbour 5 all 245157 (29920); neighbour 6 first 42387 (5935). No rank-22 candidate was emitted.

The exact next cursor is neighbour 6, support 42387, first unvisited `[0,3,6,9,17,21,22]`. The baseline Frontier diagnose is valid at rank 23 and ties the known value. `bun run check` passed: 434 pass, 1 skip, 0 fail. Artifacts, logs, trace, checkpoint/result, seed, script, hashes, planted control and baseline evidence are in `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c9/`.

## Deviations

The c8 script did not atomically replace JSON progress files, so c9 adds atomic writes and a graceful time cutoff. The mathematical criterion and search domain are unchanged. The hash manifest excludes the generated Python bytecode-cache directory.

## Concerns

This only excludes the integral constructive-factorization criterion over the covered supports. It is not a tensor-rank lower bound and does not rule out the remaining neighbour-6 supports, rational/non-integral replacements, other rank-23 schemes, or different reductions.

## Follow-ups

Resume only neighbour 6 at `--start-support-index 42387`, then stop when its remaining 202770 supports are complete. Do not rerun neighbours 0–5, support sizes 3–6, the 15,000-state walk, or the exhausted pencil scans.
