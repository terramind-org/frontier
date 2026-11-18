# c8: continued checkpointed seven-term screen

This bounded continuation starts precisely at the c7 durable cursor: neighbour
2, support index 7,843, support `[0,1,3,9,12,13,16]`. It uses the unchanged
c7 screen (`seven_term_checkpointed.py`, SHA-256
`f5e0f615b98328989d26ba77fe7f08f3bcb424b225a2fab5e012d7452538238d`)
and Perminov source certificate (`perminov-cr58-cn122.json`, SHA-256
`80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`).

The c7 accepted restart-control reference is the byte-identical 50-support
trace at SHA-256 `3f848349132bdcc042c056f0b86fe625537afdcf0b9474f6405865bf0d118eef`.
The c8 command runs on CPU 0, checks the planted seven-to-one exact reduction,
and writes a durable checkpoint after every 1,000 visited supports.

It tested 475,000 new seven-subsets in 1,269.2146425247192 seconds. Neighbour
2 is now complete; neighbour 3 is partial. No constructive reduction or
candidate was emitted. Resume only at neighbour 3, support index 237,686,
first unvisited support `[7,10,14,15,16,21,22]`.

`frontier-baseline-diagnose-c8.json` records that the decoded 23-term baseline
is valid and ties the known value. `repository-check.txt` records the passing
repository gate. `artifacts-sha256.txt` hashes the retained c8 package.
