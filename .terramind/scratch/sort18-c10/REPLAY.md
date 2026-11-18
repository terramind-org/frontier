# c10 compact certificate bundle

This bundle preserves two complete, fixed-prefix/fixed-suffix sorting-window
UNSAT proofs against the same 77-comparator baseline.  No uncompressed CNF or
DRAT is retained.

## Recovered control: `[62,74) -> 11`

The baseline is SHA-256
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.
The recovered compressed CNF and DRAT decompress to:

```
dac3f78a4f43fa0bc19501b3aecaf496f456c67878965bb5d79f58f37dc5bc6d  CNF
acb48be575061eab0f925cf32b74aecd53e0bce8640104ced908b6a0f399e3c6  DRAT
```

Fresh c10 DRAT-trim replay: `s VERIFIED` in 129.094 seconds.  Its raw checker
output is `recovered_s62_w12_t11.drat-trim.fresh.log`.

## Fresh query: `[61,73) -> 11`

The exact one-core invocation was:

```sh
timeout --signal=TERM --kill-after=10s 600s taskset -c 0 \
  /workspace/repo/.terramind/scratch/sort18-c4/venv/bin/python -u \
  window_cegis_artifacts.py baseline.json 61 12 600 6112
```

The external supervisor exited 0 after 185 seconds; CaDiCaL 1.5.3 returned
UNSAT in 182.635 seconds.  The initial CNF contains all 63 reachable prefix
states, 15,993 variables, and 797,852 clauses, so no incremental CEGIS gap
remains.  The decompressed payload hashes are:

```
72dee4cc5d29ba8ccaa1200da13f3adcfadec15104f816df24817a4fe5830899  CNF
fbd58de6d405e22bdfa4c17b4670b89eb2d7c7a7becbc0a54f751bf41be17739  DRAT
```

Fresh DRAT-trim replay: `s VERIFIED` in 229.206 seconds.  The raw log is
`query_s61_w12_t11.drat-trim.fresh.log`.  The retained new proof is the
lossless `query_s61_w12_t11.drat.xz` archive (the working gzip copy is not
part of the bundle).  `MANIFEST.sha256` covers every retained object;
`sha256sum -c MANIFEST.sha256` checks the bundle.

These are fixed-window exclusions only.  They are not a lower bound for every
18-wire sorting network and do not rule out a different 76-comparator network.
