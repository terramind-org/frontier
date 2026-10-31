## Done
- Six computer-science witness problems from the research report (all marked verified there), each `problems/witness.<slug>.yaml` written with `writeYaml` after `Problem.parse` + `problemIssues`: `matmul-rank-3x3x3` (best 23, Z), `matmul-rank-4x4x4` (48, Q), `matmul-rank-5x5x5` (93, Z), `sorting-network-size-13` (45), `sorting-network-size-18` (77), `superpermutation-7` (5905). Best-known values, sources and quotes come from the report; unverified items (Blaeser 19 over Z, Dumas et al. paper, derivations of lower bounds 44/68, the group thread, claimed 5898 bound) are said to be unverified in the notes or left out.
- Three verifiers, `src/check/witness/{matmul,sortnet,superperm}.ts`, each with strict shape checks, unknown keys rejected, first violation named, complexity in the header. matmul is exact BigInt over a common denominator; sortnet is the 0-1 principle with 2^n-bit BigInts (n <= 24); superperm counts distinct permutation windows. `common.ts` unchanged.
- Tests: `matmul.test.ts` (10), `sortnet.test.ts` (8, incl. 300 random networks cross-checked against an independent brute force), `superperm.test.ts` (6), `cs-tier.test.ts` (19: every problem through `checkAttempt`, the real `bun frontier check` CLI with a lowered best known to hit "beats", an empty-object rejection, and an invalid sorting network), plus `cs-constructions.ts` (schoolbook, Strassen, Kronecker square, Batcher, greedy superpermutation).
- Real records, run once locally from the researcher's converted files in /tmp/csr: matmul 3x3x3 valid 23 (2 ms), 4x4x4 over Q valid 48 (2 ms), 5x5x5 valid 93 (2 ms); sorting networks 13 -> 45, 17 -> 71, 18 -> 77 valid, each invalid with the last gate removed (counterexample named); all four 5905-character superpermutation attachments valid at 5905, and the 46188-character n = 8 word valid with n = 8 (25 ms). Script: /tmp/csr/run-records.ts (not committed).
- Fixtures README updated: no record committed (sources state no redistribution licence); sources and SHA-256 recorded.
- Checks: `bun run check` -> tsc clean, `205 pass, 18 skip, 0 fail`, `ok: 1485 problems, 0 attempts`. The 18 skips are the Lean checker tests (no lean/.lake in this worktree). `bun frontier validate` ok.
- README.md / AGENTS.md state no witness-problem count, so nothing to update.

## Deviations
- The task said to use `bun frontier check`; the tier test also uses `checkAttempt` directly (same code path as the CLI) plus one real CLI spawn per problem.
- The existing `tier.test.ts` id list (rejects `{}`) is not extended (not my file); `cs-tier.test.ts` covers the six new ids instead.
- Witness format limits chosen by me: matmul n 2..8, at most 1000 terms; sortnet n 2..24, at most 5000 gates; superperm n 2..9, word at most 2,000,000 chars, digits only, no whitespace (the group's raw files carry two bytes of whitespace; trim before submitting).

## Concerns
- The matmul convention: c is added to C as stored (the fmm catalogue stores it transposed; the researcher's converted files, which I verified, use the stored-as-is form). Stated in the problem format.
- Superpermutation 5905 rests on Wikipedia, a third-party README and the attachments; the thread was never opened. The record may move; the note says so.
- Best-known note for 4x4x4: Epoch AI judges in a different ring; stated in the note.
- Sorting-network lower bounds 44 and 68 are the Dobbelaere page's, not independently derived.

## Follow-ups
- Cycle 3: the tier.test.ts id list could include the new ids; the site task should render the formats (long text with JSON examples).
- Optional extra problem if wanted: sorting network n = 17 (71 gates) verified with the same verifier; depth objective would need a verifier change.
