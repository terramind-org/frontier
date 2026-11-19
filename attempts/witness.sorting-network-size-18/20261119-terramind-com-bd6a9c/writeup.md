# Testing shorter windows in an 18-wire sorting network

A checked SAT certificate excludes replacing comparators [48,59) of the published 77-comparator network with ten comparators while keeping the rest fixed.

All 262,144 binary inputs were used to check the starting network. Three enumerations agreed on the 218 states entering this window. CaDiCaL found the complete formula infeasible and an independent drat-trim replay accepted the proof. Earlier windows have their own certificates. The search left [58,70), [59,75) and [42,54) open. A different 76-comparator network remains possible.

[Archived research handoff](https://github.com/terramind-org/frontier/blob/fd6e34531670d20b4db362dbc113bdbfa75be2f6/.terramind/swarm/frontier-cloud-codex-wide/handoffs/resynthesize-interior-sorting-ne-ve95w.md). [PR 154](https://github.com/terramind-org/frontier/pull/154) · [PR 163](https://github.com/terramind-org/frontier/pull/163)
