## Done
- `package.json` (scripts exactly per design), `tsconfig.json` (strict, ESNext, bundler, allowImportingTsExtensions, noEmit, types bun, plus noUncheckedIndexedAccess/verbatimModuleSyntax), `bun.lock`; deps zod 4, yaml 2, dev typescript 7.0.2, @types/bun. `.gitignore` already had `dist/ .lake/ node_modules/`.
- `src/ids.ts`: `problemIdFromLeanName`, `newAttemptId`, `isProblemId`, `isAttemptId` per design (NFKD, guillemets, 120-char cap; throws if nothing usable).
- `src/schema.ts`: design schemas verbatim + types; `problemIssues`, `attemptIssues`, `isSafeRelativePath`, `KIND_FILE`, `KIND_TIER`.
- `src/repo.ts`: `repoRoot`, `loadProblems/loadProblem/loadAttempts` (all take an optional root, last arg), `writeYaml/writeJson/toYaml/toJson` (schema key order via zod introspection, remaining keys alphabetical, `lineWidth: 0`, trailing newline; schema guessed from record shape when not passed), `scanProblems/scanAttempts` (per-file parse errors), `problemStatus`, `loadAll`.
- `src/args.ts` (new, small): `parse` wrapper over `node:util` parseArgs + `UsageError` (exit 2 with command help).
- `src/cli.ts`: dispatcher; lists every `src/commands/*.ts` in help (so `import`, `submit`, `record` appear by existing); unknown command exit 2; `<cmd> --help`.
- Commands `list show pick new validate check index` per the table. Exports other tasks can reuse: `validateAttemptDir`, `validateRepo`, `changedIssues`, `checkAttempt`, `buildIndex`, `scaffoldAttempt`, `pickProblem`.
- Licences: `LICENSE`, `LICENSE-DATA` (CC BY 4.0 legalcode, fetched), `NOTICE`, `licenses/Apache-2.0.txt` (fetched).
- Tests: `test/core/{ids,schema,repo,commands}.test.ts`, fixtures `test/fixtures/core/{good,bad}` (good: 6 problems, 5 attempts incl. verdicts; bad: one broken rule per attempt).
- Verified: `bun run check` → tsc clean, 56 tests pass, `ok: 0 problems, 0 attempts`. `bun frontier --help` lists the 7 commands; `bun frontier index` and `pick` run on the empty repo (pick exits 1 "No open problem matches").

## Deviations
- Disproof template with binders: `theorem solution : ¬ (∀ <binders>, <type>)` rather than keeping binders as parameters, because `theorem solution (n : ℕ) : ¬ P n` is not the negation of `∀ n, P n` and the checker compares against `¬ <decl type>`. Proof template keeps binders as written. Statements without binders give plain `¬ (type)`.
- Template always uses `theorem solution` (a `lemma` source becomes `theorem`); a short comment block follows the `import` line.
- `problemIssues` also rejects a `witness` block on a proof problem and a `lean` block on a witness problem (spec only required "iff").
- `record-improved` requires the witness verdict's `result === 'verified'` as well as `beats_best_known`.
- `new` puts the submitter in `people` as `{name: login, github: login, role: 'submitter'}`.
- `validate` also rejects symlinks inside attempt dirs, duplicate attempt ids, `verdict.attempt` ≠ id, and for `--changed` an already-existing attempt directory.
- Handoff also written to `build-schema-repo-loader-and-cor-kam0m.md` (same text) because the dispatch named both paths.

## Concerns
- Lean statements are copied verbatim from the problem; if they rely on the source file's `namespace`/`open`, `solution.lean` will not elaborate without the agent adding them. The importer should keep statements fully qualified or this template needs `open` lines.
- Statement parsing finds the first depth-0 `:` after the name; unusual syntax (e.g. `theorem foo : T` preceded by `variable`-bound binders, or `⟨⟩`-less custom brackets) is untested against real formal-conjectures data.
- `check` dispatches by `existsSync(src/check/<tier>.ts)` then dynamic import; a checker that throws becomes an `error` verdict (exit 0).
- `validate` with no `--changed` reads every file; fine at 1,472 problems but not benchmarked.
- TypeScript is 7.0.2 (native); it resolved from `typescript` latest and works with the check script.

## Follow-ups
- import-fc: keep `lean.statement` self-contained (see concern 1); sort by id and use `writeYaml` (it infers the Problem key order).
- ci: `bun frontier validate --changed origin/main...HEAD` is the PR gate; `buildIndex` throws on an invalid repo.
