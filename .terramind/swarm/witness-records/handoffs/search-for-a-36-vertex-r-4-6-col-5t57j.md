## Done

Filed `attempts/witness.ramsey-4-6/20261117-terramind-com-41765d` as a writeup titled "Fixed-core SAT, Cayley enumeration and annealing, 42 min of 120, no 36-vertex colouring". Both declarations remain false.

Frontier accepted 35 vertices, tying the record. The best 36- and 37-vertex candidates failed diagnosis with 12 and 24 forbidden cliques, respectively. All 7,176 fixed-core formulas from the downloaded 35 returned UNSAT, covering every way to retain 32 to 35 of its vertices. Branch and bound found an exact minimum of 20 violations when all 35 old vertices and edges were fixed. All 16 complete symmetric enumerations found positive minima.

The search ran from 21:23:17 to 22:05:16 UTC on 17 November 2026. The final search lanes exited 0. In worktree `dead-butte`, `.terramind/scratch/ramsey46` retains the control logs, `all-extensions.log`, `results/delete-three.log`, solver and search logs, four sampled DRUP traces, and the saved candidates. The controls restored a valid 35 and found the known valid 17- and 24-vertex colourings. An independent checker replayed the four DRUP traces.

```text
$ bun src/cli.ts check "attempts/witness.ramsey-4-6/20261117-terramind-com-41765d"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun run check` passed typechecking and ran 434 passing tests, one skipped actionlint check and zero failing tests. Repository-wide validation exited 1 on unconfirmed declarations. Attempt-only validation reported the same declaration error as its sole finding.

## Deviations

The first MaxSAT process exited 143 so the exact extension cases could run first. Branch and bound supplied the exact minimum later. The broad unrestricted lane exited 130 when interrupted to switch to colder refinements and SAT repairs. Work ended after 41 minutes and 59 seconds once the remaining campaigns completed.

## Concerns

The 36-vertex six-block family remained UNKNOWN at the last conflict cap. The block results apply to the cycle partitions listed in the writeup. The low-clique candidates give no bound on the edit distance to a valid colouring.

## Follow-ups

Generate 34-vertex colourings with high induced four-vertex path counts and low colour-1 K₄ counts, then test two-vertex extensions. The fixed-core results motivate starting from 34-vertex classes outside the downloaded colouring.
