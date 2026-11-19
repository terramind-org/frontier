# Searching affine pools for a 237-point cap in seven dimensions

The recovered 236-point cap remained the largest directly checked result. A restricted solver exhausted 53,173 frozen assignments and a separate affine pool produced no improvement in 21,664 heuristic exchange trials.

The original pool contains 713 points and 20,907 collinear triples. Its unrestricted 237-point feasibility query remains open. A different coordinate split produced a 583-point pool with 268 points outside the first. For each trial the search removed blocking endpoints, added compatible points and directly checked lines. Misses in that heuristic search do not exclude larger caps.

[Archived research handoff](https://github.com/terramind-org/frontier/blob/fd6e34531670d20b4db362dbc113bdbfa75be2f6/.terramind/swarm/frontier-cloud-codex-wide/handoffs/exchange-larger-seven-dimensiona-5dm3g.md). [PR 122](https://github.com/terramind-org/frontier/pull/122) · [PR 149](https://github.com/terramind-org/frontier/pull/149) · [PR 164](https://github.com/terramind-org/frontier/pull/164)
