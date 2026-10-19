# Witness test fixtures

Only fixtures whose licence allows redistribution are committed here. Every other verifier is tested on
witnesses built by documented constructions in `test/check/witness/*.test.ts`.

| File | What | Source | Licence |
|---|---|---|---|
| `cap-set-f3-8-size512.json` | The 512-point cap set in F_3^8 found by FunSearch, as `{"points": [...]}` | https://raw.githubusercontent.com/google-deepmind/funsearch/main/cap_set/n8_size512.txt (SHA-256 of the original `8d6df45c3039b6a7ee1aae7216b100c3f4c075179dc6471f4f51b968a26d8905`, one JSON array per line; converted to one JSON object) | The repository README (section "License and disclaimer") says all software is Apache-2.0 and "All other materials are licensed under the Creative Commons Attribution 4.0 International License (CC-BY)". Credit: B. Romera-Paredes, M. Barekatain, A. Novikov et al., Nature 625, 468-475 (2024), DOI 10.1038/s41586-023-06924-6. |
| `covering-13-7-4-size30.json` | A 30-block covering design C(13,7,4) as `{"blocks": [...]}` | La Jolla Covering Repository final dataset, D. M. Gordon, Zenodo DOI 10.5281/zenodo.19735294 (entry `C(13,7,4)` of `covers.json`) | CC BY 4.0, "Copyright (c) 2024, Daniel M. Gordon" |

Not committed (no licence stated by the source), but checked once by hand against the verifiers while developing them
(all valid, same values as the cited records): Exoo's `g55.42` (R(5,5), 42 vertices) and `r4.6.35` (R(4,6), 35 vertices)
from http://cs.indstate.edu/ge/RAMSEY; the 604-vector kissing configuration in dimension 11 from
https://github.com/togethercomputer/EinsteinArena-new-SOTA; the 29-mark Golomb ruler of length 623 from
https://cube20.org/golomb/ (its 29 integers appear in `test/check/witness/golomb.test.ts` as a plain list of numbers).

## Computer-science problems (cycle 2)

None of these record witnesses is committed: the sources state no licence that allows redistribution. Each was downloaded
on 2026-10-19, converted to the formats in the problem files, and checked once by hand with the real verifiers (all valid,
same values as the cited records, each in under 5 ms):

| Problem | Record | Source | Converted file SHA-256 |
|---|---|---|---|
| `witness.matmul-rank-3x3x3` | rank 23 (Laderman 1976) | https://fmm.univ-lille.fr/3x3x3_tensor.mpl.bz2 (SHA-256 `c145cff7708b8472de23e0112c0722cae05f08bed2d9883b8dbf98cbb843169e`), parameter l = 1, third matrix of each triad transposed | `54e3800c...c9695b0` |
| `witness.matmul-rank-4x4x4` | rank 48 over Q | https://fmm.univ-lille.fr/4x4x4_tensor.mpl.bz2 (`5e6c6488e9982961d8d476dcc09972ce7de7a74a1deb0c913fbd309679ba2c49`), same conversion | `48cf826d...ebd04` |
| `witness.matmul-rank-5x5x5` | rank 93 (Moosbauer and Poole 2025) | https://fmm.univ-lille.fr/5x5x5_tensor.mpl.bz2 (`087fcb6c29dbfc3d376536e0a86a316b6f710c7e83ac988db264267a74ca328e`), same conversion | `56770a09...5e7e3` |
| `witness.sorting-network-size-13` | 45 gates | the 13-input section of https://bertdobbelaere.github.io/sorting_networks.html (page snapshot SHA-256 `fb08a5cd90a460607586be0f753fa19baedc1e5fe1c7d4247efc1923e6dfd0f6`), layers flattened in order | `47bb7e74...c7141` |
| `witness.sorting-network-size-18` | 77 gates | the 18-input section of the same page | `219344d4...f5ded4` |
| `witness.superpermutation-7` | length 5905 (A. Teodorescu, 2026-08-17) | the four attachments `5905_7_sol1..4.txt` of https://groups.google.com/g/superpermutators/c/D5sKkV2jBuc, whitespace trimmed (bare word of `sol1`: `98564c93f955c9256ca69c819e1b106a2be79e3286be2635d8374bc5595be6ac`) | n/a (the file is the word) |

The tests instead use documented constructions (`test/check/witness/cs-constructions.ts`): the schoolbook scheme, Strassen's
7-term scheme and its Kronecker square (rank 49 for 4x4), Batcher's odd-even merge sort, and a greedy superpermutation.
The fmm catalogue files and the Dobbelaere page also verified a 71-gate network on 17 inputs.
