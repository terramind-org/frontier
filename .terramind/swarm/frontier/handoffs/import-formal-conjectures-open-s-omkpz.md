## Done
- `src/import/lean-parse.ts`: text-level Lean parser. Masks comments and strings, bracket-matches attribute blocks, tracks `namespace`/`section`/`end` (dotted and nested, `_root_`), finds the first depth-0 `:=` that starts the proof (a `let`/`have` binder's own `:=` is skipped), docstring before the attribute (skipping `--` and plain comments in between), `AMS` numbers, module docs, title.
- `src/import/formal-conjectures.ts`: builds `Problem`s (ids via `problemIdFromLeanName`, `-2`/`-3` collisions in file-then-declaration order, titles, tags, references, source permalink with `#L<theorem line>`), writes `problems/<id>.yaml` via `writeYaml`, deletes stale `source.name: formal-conjectures` files (never `witness.*`), writes `sources/formal-conjectures.json` (repo, commit, lean_toolchain, licence, imported_at). An existing problem keeps `added`; `imported_at` is kept when commit and toolchain are unchanged, so a rerun on another date is still diff-free.
- `src/commands/import.ts`: `bun frontier import formal-conjectures --path <checkout> [--date YYYY-MM-DD]`; prints counts, no-docstring count, collisions, counts per tag. Aborts (exit 1, nothing written) if any file fails to parse.
- Committed `problems/*.yaml` (1,471 files) and `sources/formal-conjectures.json` from 197f7f8 (toolchain `leanprover/lean4:v4.33.1`).
- Tests: `test/import/{parse,import}.test.ts`, `helpers.ts`, fixtures `test/fixtures/import/checkout/**` (nested dotted namespaces, dotted variant names, `«»` names, multi-line attribute with `]` in a string, `:=` in a binder default / `let` / structure instance, docstring-less decl, `category research solved` skipped, `lemma`, comment between docstring and attribute, id collision across files, same-title clash).
- Verification: `bun run check` passes (tsc clean, 78 tests pass, `validate`: ok 1471 problems, 0 attempts). `bun frontier index`: 1471 problems, 0 attempts, 0 verified; by status open 1471. Rerun with the same `--date`, and with a different date, gives zero `git status` diff (tested on the real data and in the test suite).
- Count reconciliation: `grep -rho '@\[category research open'` gives 1,472, but one hit is `FormalConjectures/OEIS/README.md:96`, a documentation example, not a `.lean` declaration. The `.lean` files hold 1,471 (1,465 `theorem`, 6 `lemma`) in 886 files; all 1,471 imported, 0 skipped. (The 889 files from `grep -rl` = 886 `.lean` + that README + the 2 `Subsets/FC100*Set1.lean` files that only mention the tag in prose.)
- Collisions: 0. Declarations without an upstream docstring: 0 (7 had a `--` comment between docstring and attribute; the parser now looks through such comments). No module-doc title fallback needed (0 files).
- Counts per tag: erdos-problems 711, variant 274, wikipedia 268, oeis 189, greens-open-problems 90, paper 85, arxiv 33, open-quantum-problems 28, other 17, books 11, millennium 11, mathoverflow 9, kourovka 6, written-on-the-wall-ii 6, optimization-constants 3, hilbert-problems 2, litt-problems 2. 55 problems have no references (none in the module doc or docstring).
- Spot check by eye against upstream (name, module, statement cut at the right `:=`): euclidnumbers.euclid-numbers-are-square-free, erdos855.erdos-855, pollocksconjecture.pollock-tetrahedral.salzer-levine, koethe.kotherconjecture.variants.matrixover-kotherradical, moserworm.convex-mosers-worm-problem, irrational.irrational-pi-to-pi, erdos859.erdos-859, erdos114.erdos-114, buchi.buchi-problem-m5, erdos241.erdos-241. All correct. Also checked the 37 statements that contain `:=` (let / `(n := …)` named args): they end at the proof `:=`.

## Deviations
- Total is 1,471, not 1,472 (see reconciliation: the 1,472nd match is a README example).
- Titles: when several open theorems in a file share the same title (including a main theorem alongside others), every one of them gets ` (<short name>)`, even if only one is "the" main one; this follows the spec's uniqueness rule literally. A second tier appends the full name if short names still clash (did not occur).
- `sources/formal-conjectures.json` is written with `JSON.stringify` in the documented key order, not `writeJson` (which sorts unknown keys alphabetically).
- Docstring lookup skips `--` and plain `/- -/` comments between the docstring and the attribute (spec says "directly before").

## Concerns
- Parsing is text-level: a `'"'` char literal or a raw string would confuse the masker (none in this corpus; 0 parse failures). A newer upstream commit could break it; the importer fails loudly (exit 1, nothing written) rather than skipping.
- `lean.statement` keeps source comments if any sit inside the statement (8 statements contain `--` or `/-`, all real upstream text).
- Titles of 22 problems contain `/` etc. as written upstream; harmless.

## Follow-ups
- The judge should check README's `import` line matches `bun frontier import formal-conjectures --path <checkout> [--date]`.
- The lean-checker task relies on `lean.module` / `lean.decl` for all 1,471; `decl` is the exact name as written (including `«»`) with namespaces prefixed.
