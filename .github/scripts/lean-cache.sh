#!/usr/bin/env bash
# The Lean cache (lean/.lake: Mathlib's and formal-conjectures' compiled files, ~8 GB) has exactly one
# trusted writer: the `warm` job of .github/workflows/lean-cache.yml, on main, which never runs attempt code.
# Every reader checks through the REST API, BEFORE restoring, that the entry it is about to restore is the one
# that writer made. Restoring is extracting a tar archive with absolute paths, so restoring an archive that
# attempt code wrote would hand that code the judge's machine; checking afterwards would be too late.
#
# Why the API check is needed: any job (also one running attempt code) can reach the runner's cache token
# and write cache entries into its own ref's scope: refs/pull/N/merge for a PR, refs/heads/main for
# record.yml. A restore looks in the run's own scope before main's, so a fixed key alone proves nothing.
#
# Key format: lean-v1-<os>-<sha256 of lean/{lake-manifest.json,lean-toolchain,lakefile.toml}>-r<run id>-<run attempt>-<nonce>
# The nonce (128 random bits, chosen by the warm job right before it saves) means nobody can create the key
# before the warm job does; once it exists in main's scope it cannot be overwritten.
#
# An entry is trusted when, through the API:
#   - it is the only cache entry with that exact key (in any scope, any version), and its ref is refs/heads/main;
#   - the run id and attempt in its key are a successful run of .github/workflows/lean-cache.yml, event push,
#     workflow_dispatch or schedule, on main of this repository;
#   - it was created inside that run attempt's time window (an entry re-created after eviction is not).
#
#   lean-cache.sh prefix                 key prefix for the current lean/ files
#   lean-cache.sh resolve                newest trusted entry: prints key=… and id=… (both empty if none)
#   lean-cache.sh check <key> <id>       exit 0 iff <id> is still the only entry with <key>, on main
#   lean-cache.sh absent <key>           exit 0 iff no entry has <key>
#   lean-cache.sh own <key> <since>      exit 0 iff exactly one entry has <key>, on main, created at or after <since>
#
# Needs gh, jq, GH_TOKEN (actions: read) and GITHUB_REPOSITORY. Run from the root of a main checkout.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}"
WARM_WORKFLOW=".github/workflows/lean-cache.yml"

die() { echo "lean-cache: $*" >&2; exit 1; }

prefix() {
  local h
  h="$(cat lean/lake-manifest.json lean/lean-toolchain lean/lakefile.toml | sha256sum | cut -c1-64)"
  echo "lean-v1-${RUNNER_OS:-Linux}-$h-"
}

# All entries whose key starts with $1, one compact JSON object per line.
entries() {
  gh api --paginate "repos/$REPO/actions/caches?key=$1&per_page=100" \
    --jq '.actions_caches[] | {id, key, ref, version, created_at, size_in_bytes}'
}

epoch() { date -u -d "$1" +%s; }

# Entries with exactly key $1.
exact() { entries "$1" | jq -c --arg k "$1" 'select(.key == $k)'; }

trusted_run_window() { # <run id> <attempt>: prints "<start> <end>" (epoch seconds) or fails
  local run
  run="$(gh api "repos/$REPO/actions/runs/$1/attempts/$2")" || return 1
  jq -e --arg wf "$WARM_WORKFLOW" --arg repo "$REPO" '
    .path == $wf and (.event == "push" or .event == "workflow_dispatch" or .event == "schedule")
    and .head_branch == "main" and .head_repository.full_name == $repo and .repository.full_name == $repo
    and .status == "completed" and .conclusion == "success"' <<<"$run" >/dev/null || return 1
  echo "$(epoch "$(jq -r .run_started_at <<<"$run")") $(epoch "$(jq -r .updated_at <<<"$run")")"
}

resolve() {
  local p all key id ref created run attempt window start end t n
  p="$(prefix)"
  all="$(entries "$p")" || { echo "cannot list cache entries; continuing without the Lean cache" >&2; echo "key="; echo "id="; return 0; }
  # newest first
  while IFS=$'\t' read -r key id ref created; do
    [[ -n "$key" ]] || continue
    [[ "$key" =~ ^${p}r([0-9]+)-([0-9]+)-[0-9a-f]{32}$ ]] || { echo "skip $key: not a warm-job key" >&2; continue; }
    run="${BASH_REMATCH[1]}"; attempt="${BASH_REMATCH[2]}"
    [[ "$ref" == refs/heads/main ]] || { echo "skip $key: ref $ref" >&2; continue; }
    n="$(jq -c --arg k "$key" 'select(.key == $k)' <<<"$all" | wc -l)"
    (( n == 1 )) || { echo "skip $key: $n entries share this key" >&2; continue; }
    window="$(trusted_run_window "$run" "$attempt")" || { echo "skip $key: run $run/$attempt is not a successful lean-cache run on main" >&2; continue; }
    start="${window% *}"; end="${window#* }"; t="$(epoch "$created")"
    (( start <= t && t <= end )) || { echo "skip $key: created $created, outside run $run/$attempt" >&2; continue; }
    echo "trusted cache entry $id: $key (run $run attempt $attempt)" >&2
    echo "key=$key"; echo "id=$id"
    return 0
  done < <(jq -rs 'sort_by(.created_at) | reverse | .[] | [.key, (.id|tostring), .ref, .created_at] | @tsv' <<<"$all")
  echo "no trusted cache entry for $p" >&2
  echo "key="; echo "id="
}

case "${1-}" in
  prefix) prefix ;;
  resolve) resolve ;;
  check)
    [[ $# -eq 3 ]] || die "usage: lean-cache.sh check <key> <id>"
    got="$(exact "$2")"
    jq -se --arg id "$3" 'length == 1 and (.[0].id|tostring) == $id and .[0].ref == "refs/heads/main"' <<<"$got" >/dev/null ||
      { echo "entries with key $2:" >&2; echo "$got" >&2; die "cache entry $3 is not the only entry with key $2"; } ;;
  absent)
    [[ $# -eq 2 ]] || die "usage: lean-cache.sh absent <key>"
    [[ -z "$(exact "$2")" ]] || die "an entry with key $2 already exists" ;;
  own)
    [[ $# -eq 3 ]] || die "usage: lean-cache.sh own <key> <since>"
    for try in 1 2 3 4 5 6; do   # the list can lag a few seconds behind a save
      got="$(exact "$2")"
      [[ -n "$got" ]] && break
      sleep 10
    done
    jq -se --argjson since "$(epoch "$3")" '
      length == 1 and .[0].ref == "refs/heads/main"
      and ((.[0].created_at | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601) >= $since)' <<<"$got" >/dev/null ||
      { echo "entries with key $2:" >&2; echo "$got" >&2; die "the saved entry is not exactly one new entry on main"; }
    echo "saved: $got" >&2 ;;
  *) die "usage: lean-cache.sh prefix|resolve|check|absent|own …" ;;
esac
