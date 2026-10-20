#!/usr/bin/env bash
# frontier proof checker runner.
#
#   check-attempt.sh <solution.lean> <problemDecl> <proof|disproof>
#       Both phases on this machine (what `bun frontier check` runs).
#   check-attempt.sh --phase build <solution.lean> <out-dir>
#       Phase 1 only (CI `build` job): pre-check, compile, leave the attempt's build files in <out-dir>.
#   check-attempt.sh --phase check <out-dir> <problemDecl> <proof|disproof>
#       Phase 2 only (CI `check` job, which never checks out PR code): judge the files from <out-dir>.
#
# Output: exactly one JSON line on stdout matching `VerdictResult` (src/schema.ts), exit 0, whenever a
# verdict was reached (verified, rejected, or error for a timeout). Exit 3 for internal errors (Lean or the
# lean/ project not set up, Check.lean crashed), with a message on stderr. `--phase build` prints nothing
# on stdout; its outcome is <out-dir>/status ("ok" or "rejected") plus <out-dir>/reason.txt.
#
# Phase 1 (build): a fresh temp copy of lean/ whose .lake/packages is a symlink to the shared, already set
#   up lean/.lake/packages (Mathlib cache, formal-conjectures build); solution.lean becomes
#   Attempt/Solution.lean and `lake build Attempt` runs with a timeout (CHECK_TIMEOUT seconds, default
#   1200). A compiler error is a `rejected` verdict whose reason is the first errors (≤ 2,000 chars).
# Phase 2 (check): a second fresh temp copy made from the pristine lean/ (never the phase-1 dir). Only the
#   Attempt/Solution .olean/.ilean files from phase 1 are copied in; then Check.lean runs there. Check.lean
#   never elaborates attempt source: it replays the attempt's constants through the kernel.
#
# Tamper resistance between the phases (local mode): right before attempt code first runs, the script
#   takes one digest of every file the check reads that the attempt's compile-time code could reach:
#   lean/'s Check.lean, lakefile.toml, lake-manifest.json, lean-toolchain, this script (content hashes),
#   all of lean/.lake/packages (sources, oleans, package lakefiles; .git excluded) and the Lean toolchain
#   directory (content hashes of the small files, plus a path/inode/mode/size/mtime/ctime manifest of
#   every file; CHECK_INTEGRITY=hash adds content hashes of everything; see integrity_digest for exactly
#   what each detects). The digest stays in this
#   shell's memory only. It is compared once more after phase 2; any difference discards the verdict and
#   gives `rejected` ("changed during the check"). Processes left over from phase 1's build are killed when
#   it ends. In CI the phases run in separate jobs and phase 2 starts from a cache the trusted check job
#   saved, so the digest there is a second line of defence.
#
# Progress (local mode) goes to stderr: "[1/3] building attempt…", "[2/3] kernel replay and statement
# check…", "[3/3] integrity check…". `check-attempt.sh --precheck <solution.lean>` runs only the source
# pre-check below and prints its reason (nothing when the source passes); it needs no Lean.
#
# Source red flags, rejected before anything is built (defence in depth; the kernel replay and the axiom
# check are what make a verdict sound). `--` and `/- … -/` comments are ignored (strip_comments follows
# Lean's lexer: strings, char literals and «names» are respected, doc comments are kept and scanned, and a
# source where the boundaries could be ambiguous is scanned with its comments). Notation commands
# (notation, notation3, infix/infixl/infixr, prefix, postfix, local or scoped) are allowed: they only add
# syntax that expands to terms. Each match names the token and the line:
#   - `axiom` declarations
#   - `unsafe` code
#   - `implemented_by`, `extern` (swap compiled code for a declaration)
#   - `set_option debug.skipKernelTC` (or any mention of skipKernelTC)
#   - commands that run code while compiling: `#eval`, `run_cmd`, `run_elab`, `run_meta`, `run_tac`,
#     `by_elab`, `elab`, `elab_rules`, `macro`, `macro_rules`, `syntax`, `declare_syntax_cat`,
#     `initialize`, `builtin_initialize`, `simproc`, `dsimproc`, `meta`
#   - attributes that register compile-time code: tactic, command_elab, term_elab, macro, init,
#     builtin_*, env_linter, implemented_by, extern, export, csimp, delab, app_unexpander, norm_num,
#     positivity, *_code_action*, widget_module
#   - imports outside this allow-list (module name roots): Mathlib, FormalConjectures,
#     FormalConjecturesForMathlib, FormalConjecturesUtil, Batteries, Aesop, Qq, Plausible, Init, Std.
#     `Lean.*` meta imports are deliberately not allowed. Check.lean re-checks the compiled imports
#     against the same list.

set -euo pipefail

ALLOWED_IMPORT_ROOTS=(Mathlib FormalConjectures FormalConjecturesForMathlib FormalConjecturesUtil
  Batteries Aesop Qq Plausible Init Std)
CHECK_TIMEOUT="${CHECK_TIMEOUT:-1200}"
CHECK_INTEGRITY="${CHECK_INTEGRITY:-manifest}"   # manifest | hash, see integrity_digest
if command -v sha256sum >/dev/null 2>&1; then SHA=(sha256sum); else SHA=(shasum -a 256); fi
if command -v b3sum >/dev/null 2>&1; then CONTENT_HASH=(b3sum); else CONTENT_HASH=("${SHA[@]}"); fi
NPROC="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 8)"
LEAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH=""

die() { echo "check-attempt: $*" >&2; exit 3; }

cleanup() { if [[ -n "$SCRATCH" && -d "$SCRATCH" ]]; then chmod -R u+w "$SCRATCH" 2>/dev/null || true; rm -rf "$SCRATCH"; fi; }
trap cleanup EXIT

# ------------------------------------------------------------------ tools

# Progress for humans, on stderr (stdout carries only the verdict line).
progress() { echo "$*" >&2; }

SETUP_HINT="If another checkout already has a built lean/.lake, symlink it (ln -s <that checkout>/lean/.lake $LEAN_DIR/.lake); otherwise run 'lake exe cache get' once in $LEAN_DIR (downloads about 8 GB)."

require_lean() {
  if ! command -v lake >/dev/null 2>&1; then
    [[ -x "$HOME/.elan/bin/lake" ]] || die "lake is not installed (install elan: https://github.com/leanprover/elan)"
    export PATH="$HOME/.elan/bin:$PATH"
  fi
  [[ -d "$LEAN_DIR/.lake/packages/formal_conjectures" && -d "$LEAN_DIR/.lake/packages/mathlib" ]] ||
    die "lean/ is not set up: $LEAN_DIR/.lake/packages has no Mathlib or formal_conjectures. $SETUP_HINT"
  [[ -f "$LEAN_DIR/.lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean" ]] ||
    die "lean/ is not set up: Mathlib's compiled files (.olean) are missing from $LEAN_DIR/.lake/packages/mathlib. $SETUP_HINT"
  TOOLCHAIN="$(tr -d '[:space:]' < "$LEAN_DIR/lean-toolchain")"
  FC_COMMIT="$(awk '/"name": "formal_conjectures"/{found=1} found==0 && /"rev":/{rev=$2} found==1{print rev; exit}' \
    "$LEAN_DIR/lake-manifest.json" | tr -d '",')"
  [[ "$FC_COMMIT" =~ ^[0-9a-f]{40}$ ]] || die "could not read the formal_conjectures rev from lake-manifest.json"
}

# ------------------------------------------------------------------ JSON output

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; s="${s//$'\n'/\\n}"; s="${s//$'\r'/\\r}"; s="${s//$'\t'/\\t}"
  # drop the remaining control characters
  printf '%s' "$s" | LC_ALL=C tr -d '\000-\010\013\014\016-\037'
}

# verdict <result> <summary> <target> [reason]
verdict() {
  local result="$1" summary="$2" target="$3" reason="${4-}"
  local lean="{\"toolchain\":\"$(json_escape "$TOOLCHAIN")\",\"fc_commit\":\"$FC_COMMIT\",\"target\":\"$target\",\"axioms\":[]"
  [[ -n "$reason" ]] && lean+=",\"reason\":\"$(json_escape "$reason")\""
  lean+="}"
  printf '{"checker":"lean","result":"%s","summary":"%s","lean":%s}\n' "$result" "$(json_escape "$summary")" "$lean"
}

truncate2000() { local s="$1"; if (( ${#s} > 2000 )); then printf '%s…' "${s:0:2000}"; else printf '%s' "$s"; fi; }

target_of() { [[ "$1" == disproof ]] && echo negation || echo statement; }

# ------------------------------------------------------------------ helpers

# run_with_timeout <seconds> <log> cmd... — runs cmd in its own process group; 124 on timeout.
run_with_timeout() {
  local secs="$1" log="$2"; shift 2
  set -m
  "$@" >"$log" 2>&1 &
  local pid=$!
  set +m
  local waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if (( waited >= secs * 10 )); then
      kill -TERM -- "-$pid" 2>/dev/null || true
      sleep 2
      kill -KILL -- "-$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      return 124
    fi
    sleep 0.1
    waited=$((waited + 1))
  done
  local rc=0
  wait "$pid" || rc=$?
  # Whatever the command left running in its process group (e.g. a process forked by attempt code) dies now.
  kill -KILL -- "-$pid" 2>/dev/null || true
  return "$rc"
}

# strip_comments <src> <dst>: <dst> is <src> with `--` line comments and `/- … -/` block comments (nested)
# replaced by a space, newlines kept so line numbers do not move. It follows Lean's own lexer: comments
# are not recognised inside string literals ("…", r"…", r#"…"#), char literals ('"', '\''), or «escaped
# identifiers», and doc comments (`/-- … -/`, `/-! … -/`) are kept, since Lean parses them as tokens and may
# elaborate their contents. Where a source could make Lean and this lexer disagree on where a comment
# starts (a string literal containing `--`, `/-`, `\"`, `«` or `»`, which a notation could turn into a
# token; an apostrophe after a non-ASCII symbol that may open a char literal; an unterminated literal),
# <dst> is an exact copy of <src>, i.e. comments are scanned too. The exit status is 0 when comments were
# stripped and 10 when they were kept.
STRIP_COMMENTS_PL='
use strict; use warnings;
local $/; my $s = <STDIN>; $s = "" unless defined $s;
my $o = ""; my $amb = 0; my $n = length $s; pos($s) = 0;
my $charlit = qr{\x27(?:\\(?:x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]*\}|.)|[^\x27\\\x80-\xff]|[\xc0-\xff][\x80-\xbf]+)\x27}s;
sub block { my $d = 1; my $nl = "";
  while ($d > 0) {
    if ($s =~ /\G\/-/gc) { $d++ } elsif ($s =~ /\G-\//gc) { $d-- }
    elsif ($s =~ /\G\n/gc) { $nl .= "\n" } elsif ($s =~ /\G./sgc) { } else { last } }
  return $nl; }
while (pos($s) < $n) {
  if ($s =~ /\G--[^\n]*/gc) { $o .= " "; next }
  if ($s =~ /\G\/-[-!]/gc) { my $st = pos($s) - 3; block(); $o .= substr($s, $st, pos($s) - $st); next }
  if ($s =~ /\G\/-/gc) { $o .= " " . block(); next }
  if ($s =~ /\G(?<![.])r(#*)"/gc) { my $h = $1; if ($s =~ /\G.*?"\Q$h\E/sgc) { $o .= "r$h\"" . $&; next } $amb = 1; last }
  if ($s =~ /\G"(?:[^"\\]|\\.)*"/sgc) { $o .= $&; $amb = 1 if $& =~ m{--|/-|\\"|\xc2[\xab\xbb]}; next }
  if ($s =~ /\G"/gc) { $amb = 1; last }
  if ($s =~ /\G\xc2\xab.*?\xc2\xbb/sgc) { $o .= $&; next }
  if ($s =~ /\G\xc2\xab/gc) { $amb = 1; last }
  if ($s =~ /\G$charlit/gc) { $o .= $&; next }
  if ($s =~ /\G[0-9][0-9A-Za-z_]*/gc) { $o .= $&; next }
  if ($s =~ /\G(?:[A-Za-z_]|(?!\xc2[\xab\xbb])[\x80-\xff])(?:[A-Za-z0-9_\x27!?]|(?!\xc2[\xab\xbb])[\x80-\xff])*/gc) {
    my $w = $&; $o .= $w;
    # `→\x27"\x27`: Lean lexes a char literal after a symbol, this lexer an identifier; do not guess.
    if ($w =~ /[\x80-\xff][^\x80-\xff]*\x27$/ && substr($s, pos($s) - 1) =~ /\A$charlit/) { $amb = 1; last }
    next }
  $s =~ /\G./sgc; $o .= $&;
}
if ($amb) { print $s; exit 10 } print $o; exit 0;
'
strip_comments() { LC_ALL=C perl -e "$STRIP_COMMENTS_PL" <"$1" >"$2"; }

# Print the reason for the first red flag in the source, or nothing.
precheck() {
  local src="$1" pat name hit tok scan note rc=0
  scan="$(mktemp "$SCRATCH/scan.XXXXXX")"
  strip_comments "$src" "$scan" || rc=$?
  case "$rc" in
    0) note="comments are ignored" ;;
    10) note="comments were scanned too, because a string literal, char literal or «name» in this file makes comment boundaries ambiguous" ;;
    *) die "could not scan the source for comments (perl exit $rc)" ;;
  esac
  local B="(^|[^A-Za-z0-9_'.])"   # identifier boundary before a keyword
  local A="([^A-Za-z0-9_'!?]|\$)" # identifier boundary after it
  local checks=(
    "an axiom declaration|${B}axiom${A}"
    "unsafe code|${B}unsafe${A}"
    "@[implemented_by]|${B}implemented_by${A}"
    "@[extern]|${B}extern${A}"
    "set_option debug.skipKernelTC|skipKernelTC"
    "#eval|#eval"
    "run_cmd|${B}run_cmd${A}"
    "run_elab|${B}run_elab${A}"
    "run_meta|${B}run_meta${A}"
    "run_tac|${B}run_tac${A}"
    "by_elab|${B}by_elab${A}"
    "elab|${B}elab(_rules)?${A}"
    "macro|${B}macro(_rules)?${A}"
    "syntax|${B}(syntax|declare_syntax_cat)${A}"
    "initialize|${B}(builtin_)?initialize${A}"
    "simproc|${B}(d|builtin_|builtin_d)?simproc(_decl)?${A}"
    "meta code|${B}meta${A}"
    "an attribute that registers compile-time code|(@\[|attribute[[:space:]]*\[)([^]]*[^A-Za-z0-9_'.])?(tactic|command_elab|term_elab|macro|init|builtin_[A-Za-z_]+|env_linter|export|csimp|delab|app_unexpander|norm_num|positivity|[a-z_]*code_action[a-z_]*|widget_module)${A}"
  )
  for entry in "${checks[@]}"; do
    name="${entry%%|*}"; pat="${entry#*|}"
    if hit="$(grep -noE -m1 -- "$pat" "$scan" | head -n1)"; then
      tok="$(sed -E 's/^[^A-Za-z0-9_#@]+//; s/[^A-Za-z0-9_]+$//' <<<"${hit#*:}")"
      echo "source uses ${name}: \`${tok}\` on line ${hit%%:*} (${note}); the pre-check rejects this before anything is compiled"
      return
    fi
  done
  # imports: `import A B`, also `public import`, `meta import`, `import all`
  local line mod root ok
  while IFS= read -r line; do
    line="${line%%--*}"   # still needed when comments were kept (ambiguous source)
    line="$(sed -E 's/^[[:space:]]*((public|private|meta)[[:space:]]+)*import[[:space:]]+(all[[:space:]]+)?//' <<<"$line")"
    for mod in $line; do
      root="${mod%%.*}"; root="${root//«/}"; root="${root//»/}"
      ok=0
      for r in "${ALLOWED_IMPORT_ROOTS[@]}"; do [[ "$root" == "$r" ]] && ok=1; done
      if (( ! ok )); then
        echo "imports $mod, which is not on the allow-list (Mathlib, FormalConjectures*, Batteries, Aesop, Qq, Plausible, Init, Std)"
        return
      fi
    done
  done < <(grep -E '^[[:space:]]*((public|private|meta)[[:space:]]+)*import[[:space:]]' "$scan" || true)
}

# Module names imported by the source (already allow-listed by precheck), comments stripped.
imports_of() {
  local scan
  scan="$(mktemp "$SCRATCH/imports.XXXXXX")"
  strip_comments "$1" "$scan" || true
  grep -E '^[[:space:]]*((public|private|meta)[[:space:]]+)*import[[:space:]]' "$scan" |
    sed -E 's/--.*//; s/^[[:space:]]*((public|private|meta)[[:space:]]+)*import[[:space:]]+(all[[:space:]]+)?//' |
    tr -s '[:space:]' '\n' | grep -v '^$' || true
}

# Build the (allow-listed, upstream) modules the attempt imports in the pristine project, so that phase 1
# finds them up to date and writes nothing into the shared packages.
prebuild_imports() {
  local mods=() m
  while IFS= read -r m; do [[ "$m" == Init* || "$m" == Std* ]] || mods+=("$m"); done < <(imports_of "$1")
  (( ${#mods[@]} )) || return 0
  (cd "$LEAN_DIR" && lake build "${mods[@]}" >"$SCRATCH/prebuild.log" 2>&1) || return 1
}

# integrity_digest: one digest over everything the check reads that attempt code could reach: lean/'s
# Check.lean, lakefile.toml, lake-manifest.json, lean-toolchain and this script, the package store
# (lean/.lake/packages, .git excluded, symlinks followed) and the Lean toolchain directory.
#   Always: the checker's own small files are content-hashed, and every file (small files included) gets a
#     manifest line: path, device, inode, mode, size, mtime and ctime. Any write, truncate, rename-over,
#     delete, re-create or chmod by a non-root process changes the inode or the ctime, and ctime cannot be
#     set back without root (or changing the system clock), so this detects every modification the
#     attempt's code could make as the user, including one that is later undone (writing the old content
#     back still moves ctime). About 5–10 s for ~160,000 files. It does not detect a change made by root.
#   CHECK_INTEGRITY=hash adds a content hash of every file (b3sum if installed, else sha256sum or shasum,
#     in parallel); several minutes over 7.8 GB. It only adds coverage for changes made as root.
integrity_digest() {
  local tc_dir
  tc_dir="$(cd "$LEAN_DIR" && lean --print-prefix)"
  {
    (cd "$LEAN_DIR" && "${SHA[@]}" Check.lean lakefile.toml lake-manifest.json lean-toolchain check-attempt.sh)
    { printf '%s\0' "$LEAN_DIR"/{Check.lean,lakefile.toml,lake-manifest.json,lean-toolchain,check-attempt.sh}
      find -L "$LEAN_DIR/.lake/packages" "$tc_dir" -path '*/.git' -prune -o -type f -print0; } |
      LC_ALL=C perl -MTime::HiRes=stat -0 -ne 'chomp; my @s = stat($_);
        print @s ? sprintf("%s %s %o %s %.9f %.9f %s\n", @s[0,1,2,7,9,10], $_) : "missing $_\n"'
    if [[ "$CHECK_INTEGRITY" == hash ]]; then
      find -L "$LEAN_DIR/.lake/packages" "$tc_dir" -path '*/.git' -prune -o -type f -print0 |
        xargs -0 -P "$NPROC" -n 500 "${CONTENT_HASH[@]}"
    fi
  } | LC_ALL=C sort | "${SHA[@]}" | cut -d' ' -f1
}

# Fresh project copy (no build output) at $1 sharing the package store.
fresh_copy() {
  local dst="$1"
  mkdir -p "$dst/Attempt" "$dst/.lake"
  cp "$LEAN_DIR"/{Check.lean,lakefile.toml,lake-manifest.json,lean-toolchain} "$dst/"
  ln -s "$LEAN_DIR/.lake/packages" "$dst/.lake/packages"
}

# ------------------------------------------------------------------ phases

# phase1 <solution.lean> <out-dir>: writes <out-dir>/status (ok|rejected), reason.txt, and build files.
phase1() {
  local src="$1" out="$2" reason
  mkdir -p "$out"
  cp "$src" "$out/solution.lean"
  reason="$(precheck "$src")"
  if [[ -n "$reason" ]]; then echo rejected >"$out/status"; printf '%s' "$reason" >"$out/reason.txt"; return; fi
  if ! prebuild_imports "$src"; then
    echo rejected >"$out/status"
    printf 'could not build the imported modules: %s' "$(grep -m3 -iE 'error|unknown' "$SCRATCH/prebuild.log" | tr '\n' ' ')" >"$out/reason.txt"
    return
  fi
  [[ -n "${BEFORE_PHASE1:-}" ]] && "$BEFORE_PHASE1"
  local work="$SCRATCH/phase1"
  fresh_copy "$work"
  rm -f "$work/Check.lean"
  cp "$src" "$work/Attempt/Solution.lean"
  local rc=0
  (cd "$work" && run_with_timeout "$CHECK_TIMEOUT" "$SCRATCH/build.log" lake build Attempt) || rc=$?
  if (( rc == 124 )); then echo timeout >"$out/status"; printf 'build timed out after %ss' "$CHECK_TIMEOUT" >"$out/reason.txt"; return; fi
  if (( rc != 0 )); then
    local errs
    errs="$(sed -n '/error/,$p' "$SCRATCH/build.log" | sed "s#$work/##g")"
    [[ -n "$errs" ]] || errs="$(tail -n 20 "$SCRATCH/build.log")"
    echo rejected >"$out/status"
    printf 'does not compile: %s' "$(truncate2000 "$errs")" >"$out/reason.txt"
    return
  fi
  local lib="$work/.lake/build/lib/lean/Attempt"
  [[ -f "$lib/Solution.olean" ]] || die "lake build succeeded but produced no Solution.olean"
  mkdir -p "$out/build"
  cp "$lib"/Solution.olean* "$out/build/"
  [[ -f "$lib/Solution.ilean" ]] && cp "$lib/Solution.ilean" "$out/build/"
  echo ok >"$out/status"
}

# phase2 <out-dir> <decl> <kind> <prebuild|no-prebuild>: prints the verdict line.
phase2() {
  local out="$1" decl="$2" kind="$3" prebuild="$4" target status reason
  target="$(target_of "$kind")"
  status="$(head -n1 "$out/status" 2>/dev/null || echo missing)"
  reason="$(head -c 4000 "$out/reason.txt" 2>/dev/null || true)"
  # Never trust a build-phase outcome other than "ok": it can only make the attempt fail.
  case "$status" in
    ok) ;;
    timeout) verdict error "check timed out: $reason" "$target" "$reason"; return ;;
    *) reason="$(truncate2000 "${reason:-the build phase produced no result}")"
       verdict rejected "rejected: $reason" "$target" "$reason"; return ;;
  esac
  # Re-run the source pre-check on the solution shipped with the build (cheap defence in depth).
  if [[ -f "$out/solution.lean" ]]; then
    reason="$(precheck "$out/solution.lean")"
    if [[ -n "$reason" ]]; then verdict rejected "rejected: $reason" "$target" "$reason"; return; fi
    if [[ "$prebuild" == prebuild ]]; then
      prebuild_imports "$out/solution.lean" || die "could not build the imported modules in the pristine project"
    fi
  fi
  local work="$SCRATCH/phase2"
  fresh_copy "$work"
  mkdir -p "$work/.lake/build/lib/lean/Attempt"
  local f
  for f in "$out"/build/Solution.olean "$out"/build/Solution.olean.server "$out"/build/Solution.olean.private "$out"/build/Solution.ilean; do
    [[ -f "$f" ]] && cp "$f" "$work/.lake/build/lib/lean/Attempt/"
  done
  [[ -f "$work/.lake/build/lib/lean/Attempt/Solution.olean" ]] || {
    verdict rejected "rejected: the build produced no Solution.olean" "$target" "the build produced no Solution.olean"; return; }
  chmod -R a-w "$work/Check.lean" "$work/.lake/build"
  local rc=0
  (cd "$work" && run_with_timeout "$CHECK_TIMEOUT" "$SCRATCH/check.log" \
    lake env lean --run Check.lean Attempt.Solution "$decl" "$kind") || rc=$?
  if (( rc == 124 )); then verdict error "check timed out after ${CHECK_TIMEOUT}s" "$target" "check timed out"; return; fi
  local line
  line="$(grep -E '^\{"checker":"lean"' "$SCRATCH/check.log" | tail -n1 || true)"
  if (( rc != 0 )) || [[ -z "$line" ]]; then
    echo "Check.lean failed (exit $rc):" >&2; tail -n 30 "$SCRATCH/check.log" >&2
    exit 3
  fi
  printf '%s\n' "$line"
}

# ------------------------------------------------------------------ main

# Everything below runs from inside one function, which bash parses completely before running it: the
# script file changing on disk while a check runs cannot change what this run does.
main() {

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/frontier-check.XXXXXX")"

if [[ "${1-}" == --precheck ]]; then
  [[ $# -eq 2 && -f "$2" ]] || die "usage: check-attempt.sh --precheck <solution.lean>"
  precheck "$2"
  exit 0
fi

[[ "$CHECK_INTEGRITY" == manifest || "$CHECK_INTEGRITY" == hash ]] ||
  die "CHECK_INTEGRITY must be manifest or hash, got $CHECK_INTEGRITY"
require_lean

if [[ "${1-}" == --phase ]]; then
  case "${2-}" in
    build) [[ $# -eq 4 ]] || die "usage: check-attempt.sh --phase build <solution.lean> <out-dir>"
           [[ -f "$3" ]] || die "no such file: $3"
           phase1 "$(cd "$(dirname "$3")" && pwd)/$(basename "$3")" "$4" ;;
    check) [[ $# -eq 5 ]] || die "usage: check-attempt.sh --phase check <out-dir> <problemDecl> <proof|disproof>"
           [[ "$5" == proof || "$5" == disproof ]] || die "kind must be proof or disproof"
           phase2 "$3" "$4" "$5" prebuild ;;
    *) die "unknown phase: ${2-}" ;;
  esac
  exit 0
fi

[[ $# -eq 3 ]] || die "usage: check-attempt.sh <solution.lean> <problemDecl> <proof|disproof>"
SRC="$1"; DECL="$2"; KIND="$3"
[[ -f "$SRC" ]] || die "no such file: $SRC"
[[ "$KIND" == proof || "$KIND" == disproof ]] || die "kind must be proof or disproof"
SRC="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
TARGET="$(target_of "$KIND")"

# One integrity snapshot right before attempt code first runs (after the trusted prebuild of the imports),
# one comparison after phase 2. Phase 2 runs on whatever is on disk; if anything changed, its verdict is
# discarded here. Phase 1's leftover processes are killed when its build ends (run_with_timeout).
H0=""
record_digest() { H0="$(integrity_digest)"; }
BEFORE_PHASE1=record_digest

progress "[1/3] building attempt…"
phase1 "$SRC" "$SCRATCH/out"
if [[ "$(head -n1 "$SCRATCH/out/status")" == ok ]]; then
  progress "[2/3] kernel replay and statement check…"
fi
# Imports were built in the pristine project before phase 1, so phase 2 does not build them again.
RESULT="$(phase2 "$SCRATCH/out" "$DECL" "$KIND" no-prebuild)"
if [[ -n "$H0" ]]; then
  progress "[3/3] integrity check…"
  if [[ "$(integrity_digest)" != "$H0" ]]; then
    tamper_reason="files the checker relies on (Check.lean, lean/.lake/packages or the Lean toolchain) changed during the check; the verdict is discarded. If you were building other Lean modules in this lean/ at the same time, run the check again; otherwise treat lean/.lake as compromised by the attempt and rebuild it"
    echo "check-attempt: WARNING: $tamper_reason" >&2
    verdict rejected "rejected: $tamper_reason" "$TARGET" "$tamper_reason"
    exit 0
  fi
fi
printf '%s\n' "$RESULT"
}

main "$@"; exit $?
