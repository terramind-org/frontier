Outcome: done

## Done

Created branch `swarm/frontier-cloud-codex--reduce-rational-four-square-mult-9fiet-c7`, read `AGENTS.md`, and used a clean detached Frontier worktree at `abaabcbd` (`/tmp/frontier-clean-c7-UlJ1Id`) plus disposable research at `/tmp/matmul3-c7-Cu9o3N`. No attempt files or declarations were retained in the swarm checkout.

Recovered the public Perminov `cr58_cn122` certificate from `https://github.com/trylogical/cn122_add55`, source path:

```text
external/FastMatrixMultiplication/schemes/results/addition_reduced_ZT/3x3x3_m23_cr58_cn122_ZT_reduced.json
SHA-256 80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a
```

Decoded all 23 ternary factors exactly, correcting its column-major output map to Frontier's row-major `c` convention. The first materialization deliberately exposed the orientation issue (36 exact violations, e.g. the coefficient of `A[0][0] * B[0][1]` appeared in `C[1][0]`); after output transpose, the disposable baseline passed:

```text
bun frontier check attempts/witness.matmul-rank-3x3x3/20261118-agrim26-3ec3af
verified: Valid witness for witness.matmul-rank-3x3x3 with value 23; ties the best known

bun frontier diagnose attempts/witness.matmul-rank-3x3x3/20261118-agrim26-3ec3af
valid: yes
result: ties the best known value
```

Ran `taskset -c 0 python3 /tmp/matmul3-c7-Cu9o3N/pencil_scan.py <source>` (final elapsed 2.113 s) on every 3- and 4-term subset in every role: 10,626 subsets/role. For each subset with factor-span exactly two, it built the two rational 9x9 pencil slices, Gaussian-eliminated them over `Fraction`, and required both shared row and shared column spaces before a compressed square slice could be simultaneously diagonalized. Counts were:

```text
Perminov: role a span-2 82 / eligible 0; b 76 / 0; c 79 / 0.
Lille l=1: role a span-2 16 / eligible 0; b 16 / 0; c 16 / 0.
```

The two apparent Perminov `(rank(M0),rank(M1),row-union-rank)=(2,2,2)` supports in the earlier screening were rejected after the added column-union test: their common row spaces do not give a common column space, so they are not compressible square pencils. No diagonalization transform, rank-one lift, or local rewrite was asserted; actual reductions and rank-22 candidates were both zero.

Exact controls passed. A planted three-term span-two pencil reconstructed exactly as two rank-one terms (`plantedReducingPencilExact: true`), and the negative control was the rational pencil `(I, [[0,1],[-1,0]])`, whose characteristic polynomial is `x^2+1` and hence has no rational simultaneous diagonalization.

After the Perminov finite scope exhausted, rotated to the distinct public Lille/Laderman family at `https://fmm.univ-lille.fr/3x3x3_tensor.mpl.bz2`. Its decompressed source SHA-256 is `0ee5814978ec6b35d2041d00b976b8c3a6b2a0f391836184d803b89c91b97c08`; the same exact `l=1` scan took 1.716 s and also had no eligible compression or reduction. The scripts and raw JSON logs were intentionally left only in disposable scratch as requested; the commands and complete finite counts are above.

No rank-22 candidate was generated, so there was no candidate witness to run through Frontier. No submission, push, merge, or declaration change was made.

## Deviations

The requested simultaneous diagonalization was not invoked on a real support: the exact necessary common-row/common-column-space test rejected every span-two support before that stage. This avoids claiming a rank-one lift without a valid compressed square pencil.

The first Frontier import had the documented third-factor transpose mismatch; it was treated as a negative orientation control and fixed before baseline verification.

## Concerns

This exhausts only 3- and 4-term supports of two specified rank-23 decompositions. It is not a lower bound and does not rule out larger-support transformations, other parameter choices, or rank 22.

## Follow-ups

Try 5-term supports with a certified pencil-compression criterion or a different public rank-23 orbit. Do not repeat this 3/4-term scan without widening its support size or changing the seed.
