# c9 compact replay bundle

Recovered c8 commit: `48949869` (object present locally).  No matching
`origin/swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c8`
ref was present after the reported HTTP 408.

`recovered_s62_w12_t11.cnf.gz` and `recovered_s62_w12_t11.drat.gz` are the
lossless compressed original complete `[62,74) -> 11` CNF and DRAT.  They
decompress to, respectively:

```
dac3f78a4f43fa0bc19501b3aecaf496f456c67878965bb5d79f58f37dc5bc6d
acb48be575061eab0f925cf32b74aecd53e0bce8640104ced908b6a0f399e3c6
```

The preserved DRAT-trim log records `s VERIFIED`; the current runner's direct
replay was interrupted by the execution service's 30-second command ceiling,
so it is not represented as a fresh verification.  No uncompressed duplicate
CNF or proof is committed.

New interval `[61,73) -> 11`, seed `6112`, was chosen after the ledger audit:
it is not contained in certified `[62,74)`, since it extends one comparator
position to the left.  The full initial formula encodes all 63 reachable prefix
states (15,993 variables and 797,852 clauses).  It is retained compressed, but
the solve could not complete: both a `timeout 600s taskset -c 0` launch and a
directly supervised retry were terminated by the same 30-second execution
ceiling before CaDiCaL returned.  This is neither SAT nor UNSAT.

Reproduce on a runner that permits the requested hard deadline:

```sh
cd .terramind/scratch/sort18-c9
timeout --signal=TERM --kill-after=10s 600s taskset -c 0 \
  ../sort18-c4/venv/bin/python -u window_cegis_artifacts.py \
  baseline.json 61 12 600 6112
```
