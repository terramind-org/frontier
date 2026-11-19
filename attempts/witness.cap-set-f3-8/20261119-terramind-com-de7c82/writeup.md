# Testing exchanges around the published 512-point cap

An independently checked proof excludes 513 points for one corrected 32-anchor deletion pool. The larger mixed-slice pool with 813 optional points remains open.

The starting cap has coordinate slices of sizes 192, 160 and 160. An audit found frozen-layer deletions in earlier runs. The corrected model kept the frozen layer, fixed 392 points, and required 121 of 155 optional points subject to 11,948 line constraints. A separate checker accepted the proof. In the final 96 substitutions, 84 repeated a frozen assignment and 12 novel restricted queries were infeasible. None produced a 513-point witness.

[Archived research handoff](https://github.com/terramind-org/frontier/blob/fd6e34531670d20b4db362dbc113bdbfa75be2f6/.terramind/swarm/frontier-cloud-codex-wide/handoffs/perturb-the-eight-dimensional-ca-lpfgz.md). [PR 87](https://github.com/terramind-org/frontier/pull/87) · [PR 91](https://github.com/terramind-org/frontier/pull/91) · [PR 165](https://github.com/terramind-org/frontier/pull/165)
