# Recovery of c2-2 without an oversized Git blob

The original `bec2cfd4` proof object was recovered from this checkout's
reachable object database, then split into seven 24 MiB-or-smaller parts.
Every part is listed in `SHA256SUMS`; the concatenated stream has SHA-256
`26281a69dde5616b3cb3c08d23883937b5dee6114eee6f5111edc40b8c3b6fe4`.

To reconstruct outside the repository, copy the parts in bytewise filename
order and run:

```sh
cat parts/query_s56_w11_t10.drat.gz.part-* > query_s56_w11_t10.drat.gz
sha256sum query_s56_w11_t10.drat.gz
gzip -dc query_s56_w11_t10.drat.gz | sha256sum
```

The expected compressed-object digest is the first digest above; the expected
uncompressed DRAT digest is
`df51b9bb7254baa1f0919fd853f76f3aeb5279c26df626af5aba21974693186e`.
For the companion CNF, `gzip -dc query_s56_w11_t10.cnf.gz | sha256sum` must
produce `0b0443fa39a72b31e72ff24baa20ba1096a7d912038ac55724863747e1cc82f9`.

The recovered source, baseline, exact solver/checker commands, checker log,
and original manifest-derived digest records are retained alongside the parts.
No file in this recovery bundle exceeds 25,165,824 bytes.
