# Handoff: Build tamper-resistant Lean proof checker (lean-checker)

## Done

- `lean/lean-toolchain`: `leanprover/lean4:v4.33.1` (confirmed against formal-conjectures@197f7f8's `lean-toolchain`).
- `lean/lakefile.toml`: package `frontier_check`; requires `formal_conjectures` from git at rev
  `197f7f8dcc457f556754f826389d2ec7a0d85b92` (Mathlib `v4.33.1` → `0df444a…` comes transitively). Library
  `Attempt` with the single module `Attempt.Solution`.
- `lean/lake-manifest.json`: produced by `lake update`; pins every package rev.
- `lean/Attempt/Solution.lean`: an empty namespace so the Lake project is well formed. The runner overwrites it in a
  scratch copy; it is never judged.
- `lean/Check.lean` (phase 2, `lake env lean --run Check.lean <module> <decl> <proof|disproof>`). Kernel replay
  uses core `Lean.Environment.replay` (`Lean.Replay`) in the `leanchecker` style: the toolchain now ships
  `leanchecker` (formerly lean4checker), and I mirrored its `replayFromImports`. It reads every .olean part of the
  attempt module, builds an environment from the module's imports only, and replays every attempt constant through
  the kernel. Then, in order:
  1. Every import must be on the allow-list.
  2. The problem decl must exist in the imports and must not be defined by the attempt.
  3. No `unsafe` or `partial` constants (replay silently skips those).
  4. Kernel replay must succeed.
  5. `OpenProblemsAttempt.solution` must exist and be a theorem.
  6. Universe parameters must be equal, and `Meta.isDefEq` (default transparency) must hold against the type, or
     `Not type` for a disproof.
  7. `collectAxioms` must be ⊆ {propext, Classical.choice, Quot.sound}.

  The reasons are "uses sorry", "uses native_decide" (`Lean.ofReduceBool`, `Lean.trustCompiler`, and Lean 4.33's
  per-use `<decl>._native.native_decide.ax_<n>` axioms) and "uses axiom X". It prints one `VerdictResult` JSON
  line (toolchain, fc_commit read from the manifest, target, axioms sorted, reason). It exits 0 for any verdict
  and non-zero only on internal errors.

  For the Meta-level checks, `importModules` routes the module through the same import state with
  `loadExts := false`, and Check.lean confirms that its constants equal the ones just replayed. The attempt's own
  environment-extension data (attributes, the precomputed axiom table) is therefore never trusted, and
  `collectAxioms` walks proof bodies from scratch.
- `lean/check-attempt.sh`:
  - **Local mode** `<solution.lean> <decl> <kind>` runs both phases. Modes `--phase build <solution> <out>` and
    `--phase check <out> <decl> <kind>` are for the two CI jobs.
  - **Pre-check (the allow-list and red flags are documented in the header).** It rejects `axiom`, `unsafe`,
    `implemented_by`, `extern`, `skipKernelTC` and code-running commands (`#eval`, `run_cmd`, `run_elab`,
    `run_meta`, `run_tac`, `by_elab`, `elab`, `macro`, `syntax`, `initialize`, `simproc`, `meta`). It also rejects
    code-registering attributes such as `@[tactic …]` and `@[norm_num …]`, and imports outside Mathlib,
    FormalConjectures*, Batteries, Aesop, Qq, Plausible, Init and Std. Check.lean re-checks the imports.
  - **Phase 1.** A fresh temp copy of `lean/` with `.lake/packages` symlinked (no re-download). It first runs
    `lake build` on the attempt's allow-listed imports in the pristine project, then `lake build Attempt` under
    `CHECK_TIMEOUT` (default 1200 s, process-group kill). A compile error becomes a `rejected` verdict with the
    errors from the first `error` line on, truncated to 2,000 chars, temp paths stripped.
  - **Phase 2.** A second fresh copy from pristine `lean/`, receiving only `Solution.olean*`/`.ilean`, made
    read-only. In the CI check phase, a build status other than `ok` can only produce a rejection.
  - **Tamper resistance: I implemented hash verification.** Right before attempt code first runs, the script
    takes a per-file sha256 digest, path-sorted, over Check.lean, the lakefile, manifest, toolchain file, the
    script itself, all of `lean/.lake/packages` (`.git` excluded) and the toolchain dir. The digest lives only in
    the shell's memory. It is verified again before phase 2 and after it, and a mismatch means `rejected` with a
    warning. Each hash takes about 15 s (8-way parallel).
- `src/check/proof.ts`: implements the checker contract. It looks for `lake` on PATH, then `~/.elan/bin`; if
  neither is found it returns `error` "Lean is not installed here; CI will check this attempt". Otherwise it runs
  the runner and parses the last JSON line with `VerdictResult.parse`. A non-zero exit, unparseable output or the
  outer timeout (2×CHECK_TIMEOUT+15 min) becomes `error`. It locates `lean/` relative to its own file, not
  `repoRoot`, so it also works on fixture repos.
- `.github/workflows/lean-check.yml`: a reusable workflow (`workflow_call`, input `attempt_dir`, output
  `verdict`), `permissions: contents: read`, no secrets. Actions are pinned to full SHAs (checkout v7.0.1, cache
  v6.1.0 restore/save, upload v7.0.2, download v8.0.2, setup-bun v2.2.0). elan is installed from
  `elan-init.sh@55dc2814…`, verified with sha256 `a620ff16…`.
  - **`build`:** checks out the caller's ref into `pr/` (attempt files only) and `main` into `base/` (lean/ and the
    runner). It restores the cache without saving it, runs `lake exe cache get` and phase 1, then uploads only the
    build dir.
  - **`check`:** checks out `main` only. It reads `attempt.yaml` and `solution.lean` from the PR commit with
    `git show` (as data) and takes the decl from main's `problems/` (via bun and the zod schemas). On a cache miss
    it does `cache get` plus `lake build FormalConjecturesUtil` and saves the cache *before* touching the artifact.
    It then runs phase 2 (the pre-check runs on the PR's own source) and sets `verdict` plus a job summary.
  - The YAML parses, and the inline bun snippet was run locally against the fixture repo. The workflow has not
    been run on GitHub.
- Fixtures (`test/fixtures/proof/`):
  - `solutions/{good,sorry,changed,axiom,native-decide,forge,disproof-of-true}.lean`.
  - A fixture repo `repo/` (own package.json; problem `erdos1.erdos-1.variants.weaker` and the good proof attempt
    `20261018-agrim-a00001`; `bun frontier validate` there says `ok: 1 problems, 1 attempts`).
  - `good.lean` is the upstream proof of `Erdos1.erdos_1.variants.weaker`, renamed.
- Tests (`test/check/proof/proof.test.ts`). The Lean tests run with up to three concurrent Lean runs; with Lean
  absent they skip and print `SKIPPING Lean checker tests: …`.
  - No Lean → error verdict.
  - (a) `bun frontier check --json` → verified, axioms [Classical.choice, Quot.sound, propext].
  - (b) → "uses sorry".
  - (c) weakened statement → type mismatch.
  - (d) pre-check → "an axiom declaration", and an unchecked build through phase 2 → "uses axiom
    OpenProblemsAttempt.cheat".
  - (e) → "uses native_decide".
  - (f) pre-check rejects the `run_cmd` forge. A plain `lake build` of the same source (which really does add
    `solution := True.intro` under `debug.skipKernelTC`) through phase 2 → "kernel replay failed: …".
  - (g) the disproof-direction rejection (target `negation`), plus a documented skip of a positive disproof.
  - A compile error → "does not compile: …".
  - Six pre-check cases: Lean import, `#eval`, skipKernelTC, implemented_by, `@[tactic]`, foreign import.
- **Verification on this machine:**
  - Clean run of `bun test test/check/proof`: 17 pass, 1 fail. The one failure was the (g) regex: the rejection
    was correct, but the type prints as `Not …` because extensions are not loaded. I fixed the regex and re-ran
    that test: 1 pass.
  - An earlier run had false "tamper" verdicts. I had edited Check.lean and check-attempt.sh while it was running,
    so the integrity hash flagged real modifications.
  - `cd test/fixtures/proof/repo && bun ../../../../src/cli.ts check attempts/erdos1.erdos-1.variants.weaker/20261018-agrim-a00001`
    printed `verified: proof checked: OpenProblemsAttempt.solution proves Erdos1.erdos_1.variants.weaker (axioms:
    Classical.choice, Quot.sound, propext)` in 4:46.
  - `bun run check` (tsc, bun test, validate) exit 0: `74 pass, 0 fail, Ran 74 tests across 5 files. [1338.00s]`
    and `ok: 0 problems, 0 attempts`. The Lean tests ran in it because Lean is set up in this worktree.
- **Disk:**
  - ~25 GiB free at the start. Free space then swung between 0.6 and 28 GiB while other processes on the machine
    used and released space.
  - Lean used: `~/.elan` 2.7 G, `lean/.lake` 7.8 G (Mathlib from `lake exe cache get`, never built from source;
    FC built only up to `FormalConjectures.ErdosProblems.«1»`, which pulls in all of FormalConjecturesForMathlib),
    and `~/.cache/mathlib` 0.44 G. About 11 GiB total.
  - 14 GiB free at handoff.

## Deviations

- The runner has `--phase build|check` subcommands in addition to the 3-argument local form, so that the CI jobs
  can run the phases separately.
- Phase 1 also copies `solution.lean` into its output, and phase 2 re-runs the pre-check on the PR's real source
  (CI overwrites the artifact's copy).
- Before phase 1, the runner `lake build`s the attempt's allow-listed imports in the pristine project. Without
  that, phase 1 would write FC build outputs into the shared packages and trip the integrity hash, and CI's check
  job would lack those oleans.
- The pre-check scans raw text, comments included, because stripping comments in shell can be fooled by string
  literals. A comment saying "axiom" is rejected.
- Check.lean imports the attempt module (via `importModulesCore`/`finalizeImport`, extensions off) for the Meta
  checks rather than using the replay result directly. `Environment.ofKernelEnv` does not expose newly replayed
  constants to `find?`/MetaM in 4.33. Check.lean verifies that the imported constants equal the replayed ones.
- Axioms are sorted by string, so `Classical.choice, Quot.sound, propext`.
- (g): no positive disproof fixture (see Concerns). Its replacement is a rejection test of the direction.
- `bun frontier check` on the good fixture runs from inside `test/fixtures/proof/repo/` (the fixture repo has its
  own package.json, like `test/fixtures/core/*`). From the main repo root, `validate` would say the dir is not
  under `attempts/`.
- No files outside my ownership changed.

## Concerns

- **PR verdicts are advisory.** On `pull_request`, the workflow files come from the PR's merge ref, so a PR can
  rewrite `lean-check.yml` itself. Only the `record` run on `main` after merge (where `validate --changed` has
  kept workflows pristine) is authoritative. The ci task should treat it that way.
- **Malicious .olean loading.** Loading an attacker-supplied .olean (compacted region) is not memory-safe in
  principle; this is a known limitation shared with leanchecker. The check job saves the cache before reading the
  artifact so a compromise cannot persist. The verdict of such a run is still only as good as the Lean runtime.
- **Local tamper resistance is detection, not prevention.** Attempt compile-time code runs as the user, and a
  process forked during phase 1 could act after the last hash. Nothing stops reading the user's files. The
  textual pre-check is not complete: Mathlib has many ways to register meta code. The kernel replay, the
  statement check and the axiom check are what make a `verified` sound. Integrity hashing costs about 45 s per
  local check.
- **Concurrent local checks** share `lean/.lake/packages`. A concurrent `lake build` that legitimately builds a
  new FC module would change the digest and give another running check a false "tamper" rejection. My
  concurrent tests passed because all needed modules were already built.
- **(g) is a skip.** A quick search of FC@197f7f8 found no short false statement to refute (solved statements are
  stated to be true). A positive verified disproof has not been demonstrated.
- **Problems using `answer(…)`.** Some open FC problems use `answer(sorry) ↔ P` (deprecated elaborator). Their
  declaration type mentions `sorry`, so any attempt would carry `sorryAx`, and filling in the answer changes the
  statement. Such problems cannot currently be proof-checked. That is a design question for import-fc and the
  lead.
- Error messages print terms without notation (`Not`, `Exists fun …`, `instHDiv.hDiv`) because extensions are
  deliberately not loaded.
- **Speed.** A local check takes about 5 min (phase 1 compile ~1.5 min, Mathlib import in phase 2 ~1.3 min, three
  hashes). The Lean test suite takes ~12 min here.
- The workflow has not been run on GitHub: cache sizes (~8 GB of `.lake` plus the toolchain), the
  `git fetch <sha>` of a PR merge commit, and `lake exe cache get` on a restored cache are untested there.
- The elan installer is fetched by commit URL plus sha256, but elan then downloads the toolchain release itself
  (no pinned hash beyond elan's own handling).

## Follow-ups

- ci: call `lean-check.yml` for proof/disproof attempts and record its `verdict` output, but record only from
  the `main` run. Also decide whether PR runs should even attempt the check, given the advisory nature above.
- import-fc / lead: decide how `answer(sorry)` problems are represented. Excluding them, or a disproof/answer
  scheme, are both possible.
- Optional: pretty-print mismatch messages using an environment with extensions loaded, for display only.
- Nucleus Spaces timed out (504) on every call this session, so this task has no Spaces issue.
