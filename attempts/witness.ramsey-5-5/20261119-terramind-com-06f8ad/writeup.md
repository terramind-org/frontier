# Trying to extend 42-vertex Ramsey colourings to 43 vertices

The fifth McKay seed exhausted all 11,480 triples without a 43-vertex extension. On the sixth seed 4,304 triples were infeasible and one timed out.

For each deletion triple the remaining 39 vertices and their edge colours were held fixed. The solver tried inserting four vertices while forbidding monochromatic five-cliques. Planted reconstruction and an exhaustive small control tested the encoding. On the sixth seed the timeout was tuple [5,33,34] at index 4,304. Index 4,305 is the first unvisited tuple. These counts apply to those seeds and this insertion rule.

[Archived research handoff](https://github.com/terramind-org/frontier/blob/fd6e34531670d20b4db362dbc113bdbfa75be2f6/.terramind/swarm/frontier-cloud-codex-wide/handoffs/extend-a-39-vertex-ramsey-core-zstgo.md). [PR 152](https://github.com/terramind-org/frontier/pull/152) · [PR 162](https://github.com/terramind-org/frontier/pull/162)
