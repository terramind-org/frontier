## Done
- `src/commands/submit.ts`: `bun frontier submit <dir> [--yes] [--repo]`. Validates (`validateAttemptDir`), checks (`checkAttempt`), warns on a `rejected` verdict, needs `gh` + `gh auth status`, fork-or-direct push via `gh api …permissions.push`, branch `attempt/<id>` from the upstream default branch in a temporary `git worktree`, copies the attempt dir (no `verdict.json`, no symlinks), commits only it, pushes (gh credential helper, 4 tries for fresh forks), `gh pr create`. All git/gh calls go through an injectable `Exec`. Dry run prints the plan and PR body and changes nothing.
- `test/submit/submit.test.ts` (9 tests, fake exec): dry run, direct push, fork, only attempt files committed, invalid refused, missing gh/login, dry run without gh, rejected proof warning, PR body contents.
- `AGENTS.md`, `CLAUDE.md` (symlink), `skills/frontier/SKILL.md`, `README.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`.
- Verification: `bun run check` passes (tsc, 65 tests, validate). A fresh subagent followed AGENTS.md to a valid writeup attempt with a temporary problem. Its dry run died on a `gh` 404 (terramind-org/frontier does not exist yet); I made the dry run degrade (below) and fixed the docs where it stumbled (clone step, mode default, claim/writeup guidance, dry-run needing gh). I did not re-run the subagent after the fix; the new behaviour is covered by a unit test. The temporary problem and attempt were deleted.

## Deviations
- Spec says missing `gh` exits 1. In a dry run it now prints a NOTE and a generic plan and exits 0; with `--yes` it exits 1 with the install/login help. Reason: the subagent could not get a plan at all.
- Dry run makes read-only `gh` calls (permissions, default branch, login), so it needs network when `gh` works.

## Concerns
- Real `gh`/`git` path (fork, worktree, push, pr create) is only tested against a fake exec; never run for real, per constraints.
- `README.md` lists `import` and `record` commands that other tasks own; the existing core commands were verified, those two were not.
- AGENTS.md says Lean is checked locally if `lake` is on PATH, which describes the lean-checker task's `check/proof.ts` behaviour per the design, not yet in this branch.
- The elan install URL is from memory of the upstream project; not verified here.
- Conduct section is deliberately vague: no contact address exists.

## Follow-ups
- Judge/lead: after merge, run one end-to-end dry run against the real repo once it exists.
- Decide a contact address for conduct reports.
