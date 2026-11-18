# r7 atomic cutoff

This continuation started at r6's exact next-item cursor
`(ed3a9b5b..., 2187, 4133)` on CPU 0.  It was deliberately interrupted only
after atomic case `0249.json` had been written, to avoid spending the remaining
run budget in a much slower new substitution fibre.  No aggregate ledger was
written, so the case files are the authoritative partial record.

Cases 1--249 span 18:51:10Z to 19:03:01Z (711 seconds): 228
`DUPLICATE_PRIOR`, 11 `DUPLICATE_RUN`, and 10 exact restricted `UNSAT`; there
are no prunes, timeouts, or SAT results.  The ten UNSAT cases have planted
validity and zero mismatches in the exhaustive 256-assignment control.  The
positive-gain control is inherited from the evaluator's asserted control.

The exact first unvisited substitution, reconstructed in recorded order from
the last durable case, is
`(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae, 2187, 2360)`.
For this base/drop fibre there are 110 compatible same-slice additions; the
last durable addition, 2340, was its 21st.  Distinct added IDs repeatedly map
to identical frozen sets because the deterministic deletion cover is unchanged,
so the optional-variable set and fingerprint are unchanged as well.
