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
