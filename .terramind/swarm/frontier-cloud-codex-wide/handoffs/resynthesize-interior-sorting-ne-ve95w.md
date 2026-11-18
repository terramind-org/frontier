Outcome: done

## Done

Created branch `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c6`
from c5 and recovered its pinned baseline and encoder. The prior handoff commit
is `f8a6d41e`; the requested PR 73 could not be inspected because this sandbox
has no `gh` executable. The recovered c5 artifacts, rather than any PR
description, supplied the experiment inputs.

Repeated Frontier diagnosis before searching. The published converted
Dobbelaere/SorterHunter `Sort_18_77_12` baseline is valid on all 262144 binary
inputs at 77 comparators, tying the current record. The planted redundant-gate
positive control resynthesized in c4 is also valid at 77 comparators. The two
diagnosis logs are retained. Baseline SHA-256:
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.

Used the recovered fixed-prefix/fixed-suffix encoding, with an artifact-only
copy that records each initial DIMACS CNF and requests a CaDiCaL DRAT proof.
Every position in the candidate window can select any of the 153 legal
comparators; adjacent equal comparators are excluded as redundant. Python
3.13, numpy 2.5.5, python-sat 1.9.dev23/Cadical153, GNU `timeout`, and
`taskset -c 0` were used. Encoder SHA-256:
`aa431630311ab48938ff390f09276d2afe58863687a436d44b63d8a44a262e7e`.

Required lane, with an OS-enforced deadline:

```
timeout --signal=TERM --kill-after=10s 600s taskset -c 0 \
  ../sort18-c4/venv/bin/python -u window_cegis_artifacts.py \
  baseline.json 59 16 600 59116
```

`s=59,w=16,target=15,seed=59116` had 68 distinct reachable prefix states. It
encoded all 68 before its first solve, wrote a complete 22,421-variable,
1,157,713-clause CNF, and was ended by the external supervisor after 600 wall
seconds (`runner_exit=124`), with no result or proof trace. It is unresolved,
not UNSAT. Raw-log SHA-256:
`8728ca5f3045016f5563d66ec668c0099363d0877aab037ef0827dca33c6b9e1`;
CNF SHA-256:
`75445bcd621995701126eb1546217ea4197be517dbfc68739744fea45a1737e0`.

As required after the timeout, pivoted to the distinct, untested smaller tail
window:

```
timeout --signal=TERM --kill-after=10s 600s taskset -c 0 \
  ../sort18-c4/venv/bin/python -u window_cegis_artifacts.py \
  baseline.json 65 10 600 65110
```

`s=65,w=10,target=9,seed=65110` had 40 reachable prefix states; all 40 were
present before CaDiCaL's first solve, so its one-round UNSAT result is a proof
of the complete fixed-prefix/fixed-suffix 9-gate window query, not a
counterexample-selected subproblem. It returned in 6.670 s. Its
8,899-variable, 454,121-clause CNF and 1,788,453-line DRAT trace were retained.
Independent DRAT-trim verification reported `s VERIFIED` in 3.527 s (82,288
input clauses and 109,077 lemmas in the proof core). The derived LRAT is also
retained. SHA-256 values: raw log
`0962776dd7013177e11d604fca2a888219294422d1cd71d174b61cd8d5e5804b`,
CNF `7df69b840ac55b9082a4c17a8a7c253c02dd236416202795e2dc533e9b73ab65`,
DRAT `046787f9a96b05cfa909e329797d5bf57ade2ec86458334fea28fef9c49481ea`,
DRAT-trim log `0bfbfcd56994b23ee06fbb59043484389522b3f929578dd4dd52bb74c362b5d1`,
and LRAT `97b11c14bf6f6ade06e1ed5a63d8d02318c4dabab153db52e904c7f9e0943478`.

Compressed reproducibility artifacts (the two CNFs, the verified DRAT and the
LRAT), source encoder, baseline, and raw logs are force-added under
`.terramind/scratch/sort18-c6/`. No SAT candidate was produced; consequently
there is no 76-gate candidate to diagnose. No attempt scaffold, declaration
change, submission, merge, or local-machine computation was made.

## Deviations

The artifact capture copy of the existing encoder adds DIMACS and DRAT output;
it does not alter its sorting-window constraints. PR 73 could not be read in
this runner because `gh` is absent. DRAT-trim was fetched and compiled in a
temporary cloud directory for independent checking; its upstream Makefile
needed `-D_GNU_SOURCE` on this environment. The c6 source, logs, and compressed
artifacts were committed so this is not transcript-only evidence.

## Concerns

The verified UNSAT result is narrow: it only rules out a 9-comparator
replacement at slots `[65,75)` with this 77-gate baseline's prefix and suffix
fixed. It does not rule out a 76-comparator network generally, nor does it
settle the timed-out `[59,75)` query. `s=42,w=12` remains unresolved as
instructed. The retained DRAT certifies the encoded fixed-window SAT formula;
the link from that formula to the sorting-network claim depends on replaying the
included encoder and its exhaustive reachable-prefix construction.

## Follow-ups

Independently replay `s=65,w=10` from the compressed CNF/DRAT pair and rerun
the Python encoder to check its CNF hash. Resume the unresolved
`s=59,w=16,target=15,seed=59116` only with a different solver/configuration or
a materially longer external budget. Sweep other untested smaller tail windows
with proof-producing solvers, keeping the interpretation limited to each fixed
prefix/suffix window.
