# Original c13 recovery provenance

The completed original commit is `bcb02c4d2b7eff796c013b4f62aa4159b96b557a`
(`Record certified interior sorting window`), descended from published commit
`209a9d68`. Its local recovery ref is
`swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c13-recovery`.

The exact original transcript, source encoder, baseline, solver log, checker
log, commands, exits, timestamp files, manifest and compact proof parts were
recovered from that commit. Its only oversized new object was
`query_s48_w11_t10.drat.gz` (131,360,533 bytes), whose SHA-256 is
`2f70baaebd553cdfeb774f10071ec7886d603a0c657ee1c51dfe075442651850`.
This recovery branch deliberately does not track that object: six ordered
parts reassemble byte-for-byte to the same digest. The compressed CNF is
8,129,401 bytes and remains tracked as one object.

No persisted push-rejection log was present in the clone. The oversized DRAT
object is sufficient to explain GitHub's 100 MiB object-limit rejection; no
force-push was attempted.
