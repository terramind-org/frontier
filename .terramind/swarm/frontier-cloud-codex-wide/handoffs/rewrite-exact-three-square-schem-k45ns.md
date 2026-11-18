Outcome: done

## Done

Recovered PR 114 commit `4363332a` and its c13 audit. The retained Sun witness SHA-256 is `9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`; the inspected integral screen SHA-256 is `e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`. The completed Sun and Perminov subset screens were not reopened.

Inspection confirmed a real gap: the old `integer_rank_one_factors` rejects non-integral complementary 9-vectors before checking rational rank-one recovery. c14 adds exact-Q recovery and calibrates it with the verified non-projective identity `4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1 = 4e0⊗(e0+e1/2)⊗(e0+e1/2)`. The old method returns none; the new method exactly verifies the tensor identity and returns one rank-one term. Because the four original products differ across both complementary factors, this is not merely rescaling an input summand.

Pinned to CPU 0, the new method consumed only existing low-flattening records from c10--c13. Its deterministic rule hashes `sun-q-c14-v1:<neighbour>:<support_index>` and takes the 32 least hashes per neighbour: 224 supports total. The run took 12.4 seconds including trace loading, found zero rational replacements, and recorded a terminal complete cursor. Therefore no rank-22 witness existed to reconstruct or send to Frontier diagnose/check. `bun run check` passed: 434 pass, 1 skip, 0 fail. Source hashes, all trace hashes, selected supports, old/new mode outcomes, exact synthetic identity, terminal cursor, raw log and repository gate are in `matmul3-c14/`.

## Deviations

None.

## Concerns

The exact rational extension is calibrated, but this is a deterministic bounded sample of 224 stored low-flattening supports, not exhaustive rational screening and not a tensor-rank lower bound. It does not exclude rational replacements outside the sample, other rank-23 seeds, or different rewrite methods.

## Follow-ups

Do not rerun the exhausted Sun/Perminov subset screens, prior 3--6-term screens, 15,000-state walk, or pencil scans. A future search can apply the calibrated rational method to a separately justified bounded sample from a distinct verified rank-23 seed, or use a genuinely distinct rewrite criterion.
