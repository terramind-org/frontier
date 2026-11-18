Outcome: done

## Done

Created branch `swarm/frontier-cloud-codex--reduce-rational-four-square-mult-9fiet-c5`, read `AGENTS.md`, and used the valid transposed 48-term Lille fixture already retained from the prior cycle at `attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9`.  The fixture is the PR-58-equivalent local source in this checkout: its `c` factors are transposed from the catalogue import, the orientation correction previously required by Frontier.

Baseline checks succeeded:

```text
bun frontier check attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9
verified: Valid witness for witness.matmul-rank-4x4x4 with value 48; ties the best known (Fast matrix multiplication catalogue, <4x4x4:48>).

bun frontier diagnose attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9
problem: witness.matmul-rank-4x4x4 (verifier matmul)
value: 48 (best known 48, lower is better)
valid: yes
result: ties the best known value
```

Ran the new exact flip-walk root analysis pinned to one CPU core:

```text
taskset -c 0 bun /tmp/flipwalk.mjs attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9/witness.json /tmp/flipwalk-r48.json
{"terms":48,"pairCounts":{"a":0,"b":0,"c":0},"positiveControl":"exact scalar tensor equality passed","tValues":["1/1","-1/1","2/1","-2/1","1/2","-1/2"],"generated":0,"mergeable":0,"capped":0,"depthReached":0,"reason":"no pair of projectively proportional factor matrices in any role; no rank-preserving flip is applicable at root"}
```

The positive control used the requested identity exactly over rationals,
`b⊗c + d⊗e = (b+t d)⊗c + d⊗(e-t c)`, with `b=2`, `d=3`, `c=5`, `e=7`, `t=-2`; both sides reduce to the same rational scalar tensor.  The actual 48-term fixture has no pair of projectively proportional factors in `a`, `b`, or `c`, so no legal root flip exists in any cycled role and the walk saturates at depth zero.  No rank-47 candidate was generated; consequently there was no candidate for Frontier to check.  This was not a repetition of the earlier tensor-permutation scan.

Pivoted to the requested seven-deletion Golomb exchange, based on the audited PR-56/remote audit core semantics.  The one-core command was:

```text
taskset -c 0 bun /tmp/golomb7.ts > /tmp/golomb7-output.json
```

Raw final log:

```json
{"started":"2026-11-18T11:21:31.413Z","elapsedMs":651611,"cap":622,"k":7,"expected":672750,"completed":672750,"frozen":888030,"endpointClasses":{"neither":0,"left":296010,"right":296010,"both":80730},"frozenEndpointClasses":{"neither":888030,"left":0,"right":0,"both":0},"leaves":81144,"candidate":null,"firstUnfinished":null,"exit":"completed"}
```

The assertion target was `C(29,7)-C(27,7)=672,750`, and all 672,750 eligible cores completed.  The 80,730 `both` entries explicitly cover deleting both endpoints.  The 888,030 frozen `neither` cores retain both endpoints and have span 623, hence cannot be completed to span at most 622.  There were 81,144 exact completion leaves, no candidate, no timeout, and no uncompleted core.  Active elapsed time was 651.611 seconds (10m51.611s), under the 30-minute budget.

The prescribed practice warm-up and catalogue `show` commands could not run because the checkout contains an unrelated dangling attempt reference; exact first failure:

```text
bun frontier pick --practice
frontier pick: attempts/erdos595.erdos-595.variants.k4-not-cliquefree/20261118-agrim26-63c0a0/attempt.yaml: cannot read: ENOENT: no such file or directory, open '/workspace/repo/attempts/erdos595.erdos-595.variants.k4-not-cliquefree/20261118-agrim26-63c0a0/attempt.yaml'
error: script "frontier" exited with code 1
```

No declarations were changed and no attempt was submitted, pushed, or opened.

## Deviations

The catalog/practice command was blocked by the pre-existing dangling attempt path above, so the local validated fixture and retained prior handoff supplied the source and baseline.  The direct checker and diagnose commands still ran successfully.

The requested flip walk could not generate any neighbor because the exact projective-collision prerequisite is false at the valid root.  I did not fabricate a characteristic-two-only identity or reuse the prior tensor-permutation experiment.

## Concerns

Depth zero is a rigorous limit only for this two-term shared-factor flip graph from this fixed normalized rank-48 scheme; it does not exclude other rank-47 schemes or transformations that first alter the decomposition by another mechanism.

The Golomb result exhausts only seven-deletion/recompletion exchanges around the published 623 seed at cap 622.  It is not a global lower-bound proof.

## Follow-ups

Try a non-shared-factor rank-preserving transformation (for example, a larger support move) before revisiting flip walking; the present shared-factor move has no outgoing edge.  Keep the seven-deletion raw counts as the completed boundary and avoid rerunning it.
