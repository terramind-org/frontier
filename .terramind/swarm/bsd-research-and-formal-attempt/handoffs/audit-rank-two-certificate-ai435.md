Outcome: done

## Done

- Independently audited the Mellin normalization, coefficient construction, interval summation, signed rounding, and both truncation tails for the 389a1 second-derivative computation.
- Found and fixed the invalid `t >= 80` tail rate: the old implementation used `80c` where the uniform bound over `1<=n<=80` only supports `c`. Replaced it with the exact integral from `T=80` at rate `c`. Corrected tail bound: `0.00120320082963199065235169216373544008`. The corrected completed-derivative enclosure is `(4.33260943049475451282027568640961753, 5.19755742831913992224203383539767095)`, still strictly positive.
- Updated `audit.md` and the saved stdout; audited the matching LMFDB curve and sign records, Magma modular-symbol exact-rational semantics, and published 389a1 2-descent transcript. The handoff distinguishes the curve-specific result from general weak or strong BSD and notes that the Magma computation was not rerun locally.
- Ran `bun install` successfully with Bun 1.4.5. `bun run check` passed: TypeScript check, 434 tests passed / 1 skipped / 0 failed, and validation reported 18,618 problems and 0 attempts.

## Deviations

- Made one focused correction to the task's inherited interval script because its old `t`-tail bound was unsound; this is within the audit task's request to fix actual integration defects.
- No Frontier attempt or submission was made.

## Concerns

- `next_minus`/`next_plus` use the default 28-digit context, while arithmetic uses precision 36. This widens conservatively but means the outward step is not one 36-digit ulp. Python Decimal behavior is part of the trust base.
- The Magma rank-two descent and modular-symbol outputs are handbook transcripts, not independently portable certificates. Magma was unavailable for local reproduction.

## Follow-ups

- None.
