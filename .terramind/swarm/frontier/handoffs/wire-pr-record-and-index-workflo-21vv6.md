## Done

- `src/commands/record.ts`: `bun frontier record <attempt-dir> --result-file <json> [--run-url url] [--force]`. Parses the file with `VerdictResult`, builds a `Verdict` (attempt id from `attempt.yaml`, `checked_at` now, `checker_version` = `git rev-parse HEAD` of the repo root, optional `run_url`), writes `verdict.json` with `writeJson`. Refuses to overwrite unless `--force`. Exported `recordVerdict()` for tests.
- `.github/workflows/pr.yml` (`on: pull_request`, `contents: read`):
  - `validate`: full-history checkout, pinned setup-bun, `bun install --frozen-lockfile`, `frontier validate --changed origin/<base>...HEAD`, `bun run check`, then a `bun -e` step that uses `changedIssues` + `loadProblem` to output `attempt_dir`, `tier`, `kind` (empty for a code PR, which skips everything after).
  - `witness` (kind witness): `frontier check --json`, summary table; `proof` (kind proof/disproof): `uses: ./.github/workflows/lean-check.yml`; `proof-summary` writes the verdict table; `writeup` writes "UNCHECKED: write-ups are recorded, not verified".
  - `rejected` passes; `error`, a missing verdict or an invalid submission fails. `attempt-check` is the single job to mark as the required status check (passes when every needed job is success or skipped).
- `.github/workflows/record.yml` (push to main on `attempts/**`, `workflow_dispatch`, `concurrency: record`): `find` (bun script, max 20 attempts lacking `verdict.json`) -> `quick` matrix (witness/writeup via `frontier check --json`, uploads artifact `verdict-<dir>`) and `lean` matrix (`lean-check.yml`, `fail-fast: false`) -> `record` (only job with `contents: write`): downloads `verdict-*`, validates each dir name, runs `bun frontier record --run-url`, commits as `github-actions[bot]` "Record verdicts for <n> attempts", pushes with rebase+retry (3 times). It runs only our CLI on JSON.
- `.github/workflows/index.yml`: `bun frontier index`, then `gh release upload index dist/index.json --clobber` or `gh release create index`. Triggers: push to main, `workflow_dispatch`, and `workflow_run` of `record` (see Deviations).
- `.github/workflows/automerge.yml`: `workflow_run` of `pr`, gated on `vars.AUTO_MERGE == 'true'`, conclusion success, event pull_request. Finds the single open PR for the head sha, re-reads `pulls/<n>/files` and merges (`gh pr merge --squash --match-head-commit`) only if every file is *added*, directly inside one `attempts/<p>/<a>/`, none is `verdict.json`. No checkout of PR code.
- `.github/workflows/lean-check.yml`: focused patch (see Deviations).
- Tests: `test/record/record.test.ts` (record command, 4 tests) and `test/record/workflows.test.ts` (no `pull_request_target`; write permissions only where allowed; a single write job in record.yml; all third-party `uses:` sha-pinned with a `# vX` comment; automerge gated; plus an actionlint test that runs when `actionlint` is on PATH).
- Verification: `bun run check` -> tsc clean, 153 pass / 17 skip (Lean tests skip without Lean) / 0 fail, `ok: 1479 problems, 0 attempts`. actionlint 1.7.12 (release binary in /tmp) reports zero findings on all five workflows. The workflows have not run on GitHub.

### Walkthroughs
- **Witness PR:** PR opened -> `pr.yml` validate (rules + `bun run check`) detects kind witness -> `witness` job runs the verifier and writes the table (REJECTED still passes) -> `attempt-check` green -> maintainer (or automerge) merges -> push to main runs `record.yml`: `find` lists the dir, `quick` checks it, `record` writes `verdict.json` and pushes the commit -> `index.yml` fires from `workflow_run` and republishes `index.json`.
- **Proof PR:** same until detection (kind proof/disproof) -> `proof` calls lean-check (build job compiles the attempt, separate check job judges it) -> `proof-summary` shows the verdict -> merge -> `record.yml` runs lean-check in the `lean` matrix, `record` picks up the `verdict-lean-...` artifact and records it.
- **Write-up PR:** validate -> `writeup` job prints UNCHECKED -> merge -> record.yml `quick` produces an `unchecked` verdict, recorded the same way.

## Deviations

- Patched `lean-check.yml` (owned by lean-checker), one focused change: artifact names now carry the attempt dir (`attempt-build-<dir>`), because a matrix of attempts in `record.yml` would otherwise collide on the fixed name `attempt-build` in one workflow run; and the `check` job additionally uploads its verdict as artifact `verdict-<dir>` (`{dir, result}`), because job outputs of matrix jobs overwrite each other and the `record` job cannot read them. The `verdict` workflow output is unchanged.
- `index.yml` also triggers on `workflow_run` of `record`: pushes made with `GITHUB_TOKEN` do not trigger push workflows, so otherwise the index would never include the new verdicts.
- `record` never records `error` results (a checker/infra failure, not a judgement); the attempt stays unrecorded and is retried by the next run or a `workflow_dispatch`.
- The `record` job checks out the triggering commit (not the tip of main) so `checker_version` is the commit the checks ran on, and pushes `HEAD:refs/heads/main`.
- Branch is passed to commands via `env` (`BASE_REF`) rather than interpolated into the script, same behaviour.

## Concerns

- Never run on GitHub; the shell/jq bits are only linted by actionlint (shellcheck-level), plus the bun snippets smoke-tested locally. First real run needs eyes.
- The `record` push needs branch protection to allow `github-actions[bot]` to push to main (or a bypass); otherwise verdicts cannot be committed.
- `bun run check` in `pr.yml` executes the PR's own code with a read-only token and no secrets; `validate --changed` also fails any PR that edits non-attempt files,. Neither step has a write token or secrets.
- More than 20 unrecorded attempts need follow-up `workflow_dispatch` runs.
- `automerge` finds the PR through `commits/<sha>/pulls`, which should include fork PRs but was not exercised. The `lean` matrix caller job in `record.yml` relies on GitHub allowing `strategy.matrix` with `uses:` (it does).
- Parallel lean-check runs each try to save the Lean cache; losers get a harmless "unable to reserve cache" warning.
- If `download-artifact` finds no `verdict-*` artifact (all checks errored) the `record` job fails; that is intended noise.

## Follow-ups

- Mark `attempt-check` as the required status check and set `AUTO_MERGE` (default off) in the repo settings when it is created.
- terramind.org site task should read `https://github.com/terramind-org/frontier/releases/download/index/index.json`.
