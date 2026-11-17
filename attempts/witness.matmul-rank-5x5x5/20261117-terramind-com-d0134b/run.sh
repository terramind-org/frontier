#!/bin/sh
# Run from repo root. Two search threads, one per walk. All products stay in scratch.
printf 'start_utc='; date -u +%FT%TZ
printf 'command: search baseline.mask 6064 scratch\n'
.terramind/scratch/matmul5/search-v2 .terramind/scratch/matmul5/baseline.mask 6064 .terramind/scratch/matmul5
status=$?
printf 'search_exit_status=%s\n' "$status"
printf 'end_utc='; date -u +%FT%TZ
exit "$status"
