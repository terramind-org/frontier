Outcome: done

## Done

Recovered PR 110 commit `5dfb8d2c` and verified c8 before expanding it. The 29-mark baseline has SHA-256 `4abf52852534694883bf06274aef015bb4d803b9641cad2170ddeb071bdcf7fa`. The independent c8 reconstruction produced its exact 9,920-state stream in the recorded ordinal order, matched every c8 state record, and confirmed the zero and positive brute-force controls (0/0 and 1/1 respectively). A fresh disposable witness scaffold retained false declarations and passed Frontier `check`; direct `diagnose` likewise found the 623 ruler valid and tied the best known value. The scaffold was removed. Evidence and this handoff are committed on this branch.

Ran the expanded two-block family on one CPU (`taskset -c 0`) for 563,917 ms, exit 0. Domain: ordered increasing cut pairs from `[6,10,16,23,24]`; distinct middle/last offsets in `[-64,-1]`; at least one offset below `-32`; both joins ordered; span at most 622; translation/reflection canonicalization; c8 canonical keys excluded. It generated 30,400 raw offset pairs, of which 22,839 were canonical valid states in the expanded-only family. There were zero c8 overlaps and zero reflection duplicates in this restricted new domain.

All 22,839 states completed across ten cut-pair partitions. Exact endpoint conflict branching generated zero four-mark deletion sets, hence zero filtered or feasible cores, zero insertion-frontier coordinates, zero four-coordinate candidates, and zero unfinished states. Per-state inner checkpoints, partition completion records, `progress.json`, code, timing, raw result, baseline controls and repository gate are under `search-nonlocal-golomb-construct-kidfh-c9/`. The first unvisited state is `complete`.

`bun run check` passed: 434 pass, 1 skip, 0 fail; validation reported `ok: 18618 problems, 0 attempts`. No proposed improvement existed, so no candidate Frontier check/diagnose was required.

## Deviations

The image lacks `/usr/bin/time`; the first attempted timed launch never ran. The recorded actual run used `Date.now()` around the single-core command and completed successfully. No coverage is attributed to the failed launch.

## Concerns

This exhausts only exact four-mark repairs in the stated two-block offset extension. It does not exclude other cut locations, offsets outside `[-64,-1]`, or repairs requiring five or more changed marks.

## Follow-ups

Use a five-mark hitting-set deletion search on these or new two-block states, or partition a different internal exchange family while retaining the seed and control verification protocol.
