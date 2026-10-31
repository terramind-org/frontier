## Done
- `src/import/lean-parse.ts`: `parseLeanFile` now also returns `sorryDefs` (every `def`/`abbrev`, any modifiers, whose body after `:=` is exactly `sorry`, with full name = namespaces + name, and the name as written). `OpenDecl` gained `namespace`. New `referencesSorryDef(decl, defs)` matches a statement's dotted identifier tokens by the written name, or by any namespace-prefix resolution of the declaration's namespace to the full name (including field-style continuations); conservative.
- `src/import/formal-conjectures.ts`: adds tag `answer-required` (exported `ANSWER_REQUIRED`) when the statement references a sorry def of the same file.
- `problems/*.yaml`: re-imported from formal-conjectures 197f7f8 (`/tmp/wesolve-research/formal-conjectures`, `--date 2026-10-18`). **167 problems tagged `answer-required`.** The diff is exactly 167 insertions of `  - answer-required`; `sources/formal-conjectures.json` unchanged.
- `src/check/proof.ts`: tagged problems return the specified `unchecked` verdict before Lean is run.
- `src/commands/pick.ts`: `pickProblem(rows, seed, tier?, tag?)`; `--tag`; `answer-required` excluded unless `--tag answer-required`.
- `src/commands/new.ts`: `--kind proof|disproof` on a tagged problem exits 2 with a message pointing to `--kind writeup`.
- Docs: one paragraph in AGENTS.md (CLAUDE.md is a symlink to it) and a short "Answer problems" section in README.md.
- Tests: `test/import/parse.test.ts` (direct `.answer` def, namespace-relative and full-name references, unreferenced sorry def, real-body def, look-alike name), `test/import/import.test.ts` (end-to-end tags), `test/core/commands.test.ts` (proof checker verdict without Lean, pick, new). Fixture: `test/fixtures/import/answer/Answer.lean`.
- Verification: `bun run check` (tsc, bun test, validate) exit 0: 150 pass, 17 skip, 0 fail; `ok: 1479 problems, 0 attempts`.

## Deviations
- Tags are not re-sorted: the importer does not sort them today (folder tag, then `variant`), and sorting would reorder existing lines and break the "diff only adds the tag" requirement. `answer-required` is appended last.
- The 17 skipped tests are the Lean checker tests: `lean/` is not set up in this worktree (`.lake/packages/formal_conjectures` missing), so they did not run. This task changes nothing they exercise except an early return in `check()`, which is tested separately.

## Concerns
- Detection is per file: a theorem using a sorry def imported from another file is not tagged. The count (167) matches the ~167 expected.
- Statements using `answer(sorry)` inline are a different mechanism; none exist in the current problems, so not handled.
- Matching is deliberately conservative and could over-tag if a bound variable shares a sorry def's written name.

## Follow-ups
- The README/AGENTS paragraph hardcodes "167"; update it when the import commit changes.
