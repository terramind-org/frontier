# c6 exact three-square screen

## Public source and encoding

Downloaded `https://fmm.univ-lille.fr/3x3x3_tensor.mpl.bz2`, linked by the
catalogue's `https://fmm.univ-lille.fr/3x3x3.html` entry for Laderman (1976).
The decompressed Maple file has SHA-256
`0ee5814978ec6b35d2041d00b976b8c3a6b2a0f391836184d803b89c91b97c08`;
the downloaded bzip2 bytes have SHA-256
`c145cff7708b8472de23e0112c0722cae05f08bed2d9883b8dbf98cbb843169e`.

`parse_laderman.py` specializes the catalogue family at `l=1` and converts
each triad to Frontier's factor convention `(T1, T2, transpose(T3))`.
`frontier-laderman-diagnose.txt` reports the resulting 23-term integer
witness valid and tied with the known value. Its SHA-256 is
`df73f753490ea690fdad3b99805e054d6ae29f95d6a998ee28ebc1f228c779d0`.

`normalized-term-comparison.json` uses only term-order-insensitive,
independent projective normalization of the three factors. It finds one
shared normalized triad and 22 unique triads on each side against the pinned
Perminov fixture. This establishes nonidentity under those limited operations,
not inequivalence under tensor-factor basis changes. The Laderman source has
zero shared normalized single-factor pairs, so it cannot enter the seven
split/merge-neighbour construction; the failed, auditable setup is in
`seven-term-run.log`.

## Seven-term fallback

`seven_term_perminov.py` uses only support size seven and has a passed exact
seven-to-one planted control. It was CPU-pinned with `taskset -c 0` from the
validated Perminov seed SHA-256
`80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`.

The run was interrupted after the first durable checkpoint because one
neighbour took 704.2148303985596 seconds, projecting past the 30-minute cap.
`seven-term-perminov-checkpoint.json` records the exact completed range:
neighbour 0 / move `[0,2,4]`, all `C(23,7)=245157` supports, 31,848
low-flattening cases, zero constructive reductions, minimum maximum factor
rank 5. Resume at neighbour 1 and support `[0,1,2,3,4,5,6]`; no candidate
exists. The interrupted process exited 130 and did not invalidate the
checkpoint.
