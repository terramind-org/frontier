Outcome: done

## Done

Recovered the c4 handoff commit `d1525bf1a4c730b82b7c6ed2299713a9e0bbc07e`
locally after its failed push.  Its ignored scratch directory also survived, so
this run used the identical encoder and published 77-comparator baseline rather
than relying on transcript-only evidence.

Repeated Frontier's exhaustive witness diagnosis before the new search:

- `baseline.json` is valid with value 77 and ties the best known value.
- The planted redundant-gate positive-control candidate (`candidate_s73_w3.json`)
  is valid with value 77 and ties the best known value.

The baseline is the converted Dobbelaere/SorterHunter `Sort_18_77_12` network:
`baseline.json` SHA-256
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.
The fixed-prefix/fixed-suffix CEGIS encoder was unchanged from c4:
`window_cegis.py` SHA-256
`80d0fd74b9d21890a7c8e3bff196c61498ede94ff59d44693e9427da7b426912`.
Runtime: Python 3.13; numpy 2.5.5; python-sat 1.9.dev23; Cadical153.  Each
search was pinned to CPU 0 with `taskset -c 0` and supervised externally with
GNU `timeout --signal=TERM --kill-after=10s 600s`.

New measured tail-offset runs, both exact under the same fixed-prefix/fixed-
suffix formulation and both unresolved (not UNSAT):

- `s=61,w=14,target=13,seed=61114`: 63 distinct prefix states.  Command:
  `timeout --signal=TERM --kill-after=10s 600s taskset -c 0 ./venv/bin/python -u window_cegis.py baseline.json 61 14 600 61114`.
  It remained in its first CaDiCaL `solve()` call, emitted no CEGIS round or
  result, and was ended by the OS supervisor after exactly 600 wall seconds
  (`runner_exit=124`).  Log SHA-256:
  `4b517f2ac93346dbb66af413a38ca875e0cf9f87f0dceb1f4fd55d70f6d30d5b`.
- Adjacent tail offset `s=60,w=15,target=14,seed=60115`: 65 distinct prefix
  states.  Command:
  `timeout --signal=TERM --kill-after=10s 600s taskset -c 0 ./venv/bin/python -u window_cegis.py baseline.json 60 15 600 60115`.
  It likewise remained in its first solve call and was ended by the OS
  supervisor after exactly 600 wall seconds (`runner_exit=124`).  Log SHA-256:
  `cdedd14c5e11fd9097c05a536087192568c943b589cf99f855d9ba63aae4b94f`.

The c4 handoff records earlier completed UNSAT outcomes for `s=64,w=11`,
`s=63,w=12`, and `s=62,w=13`; this c5 run does not elevate them or add a
certificate.  No 76-gate candidate was produced, so no candidate diagnosis
was applicable.  `s=42,w=12` was not rerun and remains unresolved as required.
No attempt scaffold, declaration change, submission, or merge was made.

## Deviations

The request's “adjacent untested tail offsets” was interpreted as the immediate
next offset (`s=60`) after the required `s=61` run.  Two independent 600-second
lanes consumed the meaningful remaining single-CPU budget; a third query would
not have received the requested externally enforced full deadline.  Python-sat's
Cadical153 binding did not expose a checked proof-certificate artifact in this
existing encoder, and these two runs timed out before an UNSAT result for which
one could be emitted.

## Concerns

Neither timeout is negative evidence: both are incomplete searches interrupted
inside the first SAT solve.  The existing c4 UNSAT results have no independently
checked proof certificates and constrain only their fixed contiguous windows,
not 76-comparator networks in general.  The raw c5 logs remain intentionally
disposable in `.terramind/scratch/sort18-c4/`; hashes and commands above are the
committed reproducibility record.

## Follow-ups

Resume the next adjacent tail offset as `s=59,w=16,target=15` with a fresh
external deadline and seed `59116`; retain the same encoder/baseline hashes.
For hard windows, replace or augment the binding with a solver path that can
write DRAT/LRAT proofs before treating a returned UNSAT as independently
checkable.  Keep `s=42,w=12` out of the queue unless an independent route is
specifically chosen.
