## Done
- `problems/witness.{cap-set-f3-7,cap-set-f3-8,ramsey-5-5,ramsey-4-6,golomb-ruler-29,schur-7,kissing-number-11,covering-design-13-7-4}.yaml`: written with `writeYaml` after `Problem.parse` + `problemIssues`; best-known values and references are the ones quoted in the research report; `bun frontier validate` reports ok (1479 problems).
- `src/check/witness/{capset,ramsey,golomb,schur,kissing,covering}.ts`: one `verify(witness, params)` each (exact integer arithmetic, BigInt in `kissing` over Z[√2] and in the `ramsey` bitsets, strict shape checks, unknown keys rejected, first violation named); `common.ts` holds shared helpers. Complexity is stated in each file's header.
- `src/check/witness.ts`: tier checker (missing/invalid/oversized witness.json → rejected; unknown verifier or verifier crash → error; fills `witness` block with beats/ties in the objective's direction).
- Tests `test/check/witness/*.test.ts` (53 tests) and fixtures `test/fixtures/witness/` (512-point cap set, CC-BY per the FunSearch README; 30-block C(13,7,4), CC-BY 4.0; README records sources and licences).
- Verification: `bun run check` → tsc clean, 140 pass / 0 fail, validate ok. The real records (FunSearch 512 cap set, Exoo g55.42 and r4.6.35, EinsteinArena 604 kissing file, Golomb 623) were downloaded and run once through the verifiers (all valid with the record value; SHA-256 match the report; each < 80 ms). `bun frontier check` on a temp fixture attempt is tested through the real CLI and prints `verified: Valid witness for witness.cap-set-f3-8 with value 512; beats the best known (500, …).` (with best_known lowered).

## Deviations
- Fixtures without a redistribution licence (Exoo files, kissing file, Schur xls, Golomb zip) are not committed. Tests use documented constructions instead: Paley(17)/Paley(37) for Ramsey, Erdős–Turán and the 5-mark optimum for Golomb, the 3S+1 recursion (N=1093) for Schur, the D_11 root system (220 vectors) for kissing, a coordinate slice of the 512 cap set for n=7. The Golomb 623 list is inlined in tests as a plain list of integers.
- Schur record (1696) was not converted from the arXiv xls, so it is untested on the record itself.
- Summary text is generic ("Valid witness for <id> with value N; ties the best known (<label>).") rather than "Valid cap set of size 112 in F_3^7…", since the checker has no per-verifier noun.
- kissing.ts also exports `sign` (for a direct exact-sign test). Verifier limits not in the spec: Ramsey n ≤ 128, Schur N ≤ 5000, kissing ≤ 2000 vectors, covering v ≤ 52 and C(v,t) ≤ 5e6.
- Statements omit the Ramsey R(4,6) upper bound 40 and the cap-set n=8 upper bound 771 (report marks them weakly sourced/UNVERIFIED). `witness.cap-set-f3-7` is included (best-known value verified in Gijswijt) although the holder of 236 is unconfirmed; the note says so.

## Concerns
- The 604 kissing value is from a table that "is moving"; the note says to re-read it before claiming a record.
- Golomb 623 is a computed dataset, not independently confirmed.
- The checker accepts witness.json up to 5 MB, but `validate` caps attempt files at 1 MB (kissing at 2000 vectors may exceed it only for very large integers).
- Reference URLs for Exoo EJC P66 and Fredricksen–Sweet R32 follow the EJC URL pattern and were not opened.

## Follow-ups
- Convert Rowley's S(7)≥1696 xls to JSON and add it as a fixture if arXiv's licence permits.
- Add R(5,6) (Exoo 59) and R(4,7) as further Ramsey problems; the `ramsey` verifier already supports them.
