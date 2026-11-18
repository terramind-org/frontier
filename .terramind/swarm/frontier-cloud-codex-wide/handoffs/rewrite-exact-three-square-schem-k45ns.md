Outcome: done

## Done

Created `swarm/frontier-cloud-codex-wide--rewrite-exact-three-square-schem-k45ns-c6`, read `AGENTS.md`, and retained a new primary-source attempt under `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c6/`. Downloaded the public Fast Matrix Multiplication catalogue's Laderman tensor source (`3x3x3_tensor.mpl.bz2`): compressed SHA-256 `c145cff7708b8472de23e0112c0722cae05f08bed2d9883b8dbf98cbb843169e`, decompressed SHA-256 `0ee5814978ec6b35d2041d00b976b8c3a6b2a0f391836184d803b89c91b97c08`.

`parse_laderman.py` specializes its exact parameterized source at `l=1`, applies the documented catalogue/Frontier output convention, and produces `laderman-frontier-witness.json` (SHA-256 `df73f753490ea690fdad3b99805e054d6ae29f95d6a998ee28ebc1f228c779d0`). Frontier diagnose reports it valid at rank 23, tied with the known value. The normalized, order-insensitive term comparison to the pinned Perminov fixture found one common triad and 22 unique triads on each side. That establishes nonidentity under term permutation plus independent factor scaling, but does not prove tensor-orbit inequivalence.

Laderman has zero shared normalized factor pairs, so no split/merge neighbour can be constructed for the designated reduction criterion. The source test is preserved in `seven-term-run.log`. I therefore used the permitted fallback: a CPU-0 (`taskset -c 0`) checkpointed seven-term scan from the validated Perminov seed (`80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`). Its exact seven-to-one planted control passed.

The run completed neighbour 0 / move `[0,2,4]`: all `C(23,7)=245157` supports, 31,848 low-flattening cases, minimum maximum factor rank 5, zero constructive integer reductions. It checkpointed after 704.2148303985596 seconds. The process was stopped with SIGINT after that durable checkpoint because a seven-neighbour completion projected beyond the 30-minute cap. No candidate exists, so no candidate diagnose/check was applicable. `seven-term-perminov-checkpoint.json` is the exact resume cursor: neighbour 1, first support `[0,1,2,3,4,5,6]`; the interrupted process exited 130. `bun run check` passed: 434 pass, 1 skip, 0 fail. `artifacts-sha256.txt` covers c6 retained evidence.

## Deviations

The desired distinct Laderman source was verified, but it is incompatible with the requested shared-factor split/merge screen: there are zero legal pairs, rather than seven. This is an audited property of the decoded exact source, not a failed verifier encoding. Used the lead-authorized seven-term Perminov fallback.

The seven-term screen's first-neighbour checkpoint granularity is coarse (704 seconds). It was stopped after the first complete range rather than pretending the remaining six neighbours were searched. No declarations were changed and no attempt was submitted.

## Concerns

The completed screen is a negative result only for the corrected constructive factorization criterion on one neighbour. It is not a tensor-rank lower bound, does not establish orbit inequivalence, and leaves Perminov neighbours 1--6 entirely unvisited at support size seven.

## Follow-ups

Implement resumable in-neighbour checkpoints (including exact combination rank/cursor) before continuing neighbour 1; then run only the unvisited seven-term ranges. Alternatively identify a distinct rank-23 source with at least one shared factor pair, rather than repeating support sizes 3--6 or the exhausted scans/walk.
