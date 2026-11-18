Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c9` from recovered `8cd3a708`; made no attempt, submission, declaration change, push, PR, or merge.
- Recovered and matched the third McKay fixture (`f7b6530fc32e2544bd0b37fce3a9d605691254db49027f4514d68cd3f5249135`), encoder (`7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`), lexicographic ordering, and prior suffix checkpoint (`2dc190ccfb1dece5b662476f6afc96cac7022a2b183be79ab4031d3d975046ad`). Repeated the exhaustive 262,144-assignment encoder/scanner equivalence and planted 39-to-42 reconstruction controls successfully; the c9 control result hash is `0fcc24f3f57570b6469bfc809e0827efb69646cf4990d87e9254c96348a9be8d`.
- Retried only index 8,250 (`[14,16,37]`) under a separately retained 120-second cap: UNSAT in 0.38711730700015323 seconds and 1,982 decisions (result hash `11af7d2477de2327be4884388f3efc163a5dd3aafea144201c271a1bf765a0ab`). This retry does not overwrite its original eight-second timeout.
- Ran only the formerly unvisited third-seed suffix, indices 8,251–11,479, on one `taskset -c 0` core. All 3,229 cases are UNSAT; 0 timeout, 0 SAT; 6,440,548 decisions; 1,134.517853319001 seconds; cursor 11,480. Result hash: `18718f9038c0c91e2f613ab54311fd69ee692e7cf74a45f157c1dbaddc1b1060`.
- Audited every third-seed segment: each index 0–11,479 is covered exactly once by a final UNSAT classification, with historical timeout records at 3,395 and 8,250 retained separately and superseded only by their respective successful retries. There are no third-seed gaps, unresolved indices, timeouts, or SAT candidates.
- With the third seed exhausted, selected a fourth McKay fixture from source hash `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`, line 2. Fixture hash: `57e68639f884e6ccf769367b37f9ac103f9df5c41b55f455f9ad63845e00299a`; provenance hash: `7b2f4011e64a21a3f433e69d3a68cae38a784f56398d49b6c3a0c1331104e7c8`. Its degree sequence differs from Exoo, alternate, and third seeds and each color-swapped complement; it is independently K5-free. Its exhaustive and planted controls passed (control hash `c9b82e95d15270eb15defbeb1a6489393235a241a15a79c730ae9ee2d5851a09`).
- Ran the fourth seed separately from index 0 on one pinned core for 560.2091778150007 seconds: 1,583 UNSAT, 1 timeout, 0 SAT; 3,133,080 decisions. Index 1,583 (`[1,35,40]`) is unresolved; first unvisited cursor is 1,584. Result hash: `641282897ad408703aba2b1da41a80f3464f9a453f7341903a941c6360d8ead5`.
- No 43-vertex SAT candidate arose, so Frontier `diagnose` and `check` were inapplicable. `bun run check` passed: 434 tests passed, 1 skipped, and validation reported 18,618 problems and 0 attempts.

## Deviations

- The first c9 control invocation did not launch because the fresh sandbox lacked PySAT; its stderr is retained. Restored the pinned `python-sat==1.9.dev23` dependency in `/tmp/ramsey-c9-venv`, then repeated controls and all measured work. Both sweeps used the managed foreground shell with raw stdout/stderr and exit status 0.

## Concerns

- This only excludes the tested frozen-39-core/four-insertion families; it does not determine `R(5,5)`.
- The fourth seed's index 1,583 is unresolved and indices 1,584–11,479 are unvisited; neither category is UNSAT.
- No SAT candidate arose for independent Frontier validation. Declarations remain false and publication remains pending human approval.

## Follow-ups

1. Re-run only fourth-seed index 1,583 with a separately recorded longer cap, then resume at 1,584 using the saved fixture and ordering.
2. Validate any SAT candidate with disposable Frontier `diagnose` and `check` before any claim.
3. On exhausting the fourth seed, pivot only with a recorded color-swap-aware inequivalence certificate and fixture/order hashes.
