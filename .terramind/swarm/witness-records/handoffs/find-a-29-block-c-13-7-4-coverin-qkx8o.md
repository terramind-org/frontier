Frontier accepted 30 blocks, tying 30.

## Done

Filed the writeup `attempts/witness.covering-design-13-7-4/20261117-terramind-com-4fe5d5`, titled “Prior-art check for C(13,7,4), lower bound 30 reported, search stopped before launch.” The October 2026 preprint gives the lower bound of 30 using the published minimum-link classification and an exact finite obstruction. [Hexagon preprint](https://hexagonmath.org/2610.00669v1)

The 30-block baseline passed Frontier and a separate Python enumeration. Deleting its first block left 22 uncovered four-subsets. Both diagnose commands exited 0 and reported opposite validity. Logs are under `.terramind/scratch/covering13/` in worktree `royal-brook`. See `prior-art.md`, `baseline.log`, `check.log`, `validate.log`, and `repo-check.log`. The baseline checks started and ended at 2026-11-17T22:34:11Z, using about 0.32 wall seconds and 0.16 CPU seconds combined.

`bun frontier check` returned:

```text
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Direct validation reported only the two unconfirmed declarations, which remain false. In `bun run check`, typecheck passed and tests reported 434 passed, 1 skipped (actionlint), 0 failed. The gate exited 1 at validation because of unconfirmed declarations across the swarm attempts.

## Deviations

The brief's prior-art stop condition fired. No search lane or solver calibration ran, and the two-hour search budget was unused. The baseline came from the preprint's copy of the La Jolla covering because the historical entry was unavailable. The handoff uses the full task filename specified in the final handoff instructions.

## Concerns

The preprint takes the published minimum-link classification as input. This task reviewed the reduction and verified the construction. Independent replay of the finite lower-bound enumeration and a fresh Lean build remain outstanding.

## Follow-ups

Audit the classification transcription and replay the lower-bound computation before a separate catalog-status update. The search slot is available for an open problem.
