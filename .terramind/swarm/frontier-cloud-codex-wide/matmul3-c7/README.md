# c7: resumable seven-term screen

This directory continues the exact Perminov rank-23 screen from c6. The source certificate is `perminov-cr58-cn122.json`, SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`. `baseline-witness.json` is the decoded witness; `frontier-baseline-diagnose.json` records that it is valid at rank 23 and ties the known value.

`seven_term_checkpointed.py` enumerates lexicographic seven-subsets of the fixed seven shared-factor rewrites. Its durable cursor contains a neighbour, a zero-based support index, and the exact first unvisited support. The real run used:

```sh
taskset -c 0 python3 seven_term_checkpointed.py perminov-cr58-cn122.json seven-term-resume-result.json --support-size 7 --start-neighbour 1 --start-support-index 0 --checkpoint seven-term-resume-checkpoint.json --checkpoint-every 1000 --control-output seven-term-resume-planted.json --trace seven-term-resume.trace
```

It was intentionally interrupted at the durable cursor in `seven-term-resume-checkpoint.json`. Neighbour 1 is complete and neighbour 2 is partial. Resume with `--start-neighbour 2 --start-support-index 7843`.

The accepted checkpoint control comprises `checkpoint-control-*`: an uninterrupted 50-support trace and the concatenation of an interrupted 20-support trace plus resumed 30-support trace are byte-identical, SHA-256 `3f848349132bdcc042c056f0b86fe625537afdcf0b9474f6405865bf0d118eef`. The earlier `control-*` artifacts remain as audit evidence only: they exposed that the first implementation applied its stop counter only after low-flattening supports. That defect was fixed before the accepted control or real run.

No candidate was emitted, so no candidate witness exists to diagnose or check. All controls use the planted seven-identical-summands-to-one exact reduction.
