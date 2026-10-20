import { cpSync, lstatSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { parse, UsageError } from '../args.ts';
import { repoRoot } from '../repo.ts';
import type { Attempt, Problem, VerdictResult } from '../schema.ts';
import { checkAttempt } from './check.ts';
import { plainSummary } from './check.ts';
import type { CheckOutcome } from './check.ts';
import { validateAttemptDir } from './validate.ts';

export const help = `Open a pull request for an attempt (dry run unless --yes).

Usage: bun frontier submit <attempt-dir> [--yes] [--json] [--repo terramind-org/frontier]

Validates and checks the attempt, then with the GitHub CLI: forks the repo if you cannot push to it,
creates branch attempt/<attempt-id> from the upstream default branch in a temporary git worktree, commits
only the attempt directory, pushes, and runs \`gh pr create\`.
Without --yes it prints that plan and the PR body, changes nothing and exits 0. Show it to your human first.
Refuses until the attempt validates: the claim must be replaced and both declarations confirmed by your human.
--json prints one JSON object (plan, body, verdict, tooling) instead of text; with --yes it adds the PR URL.`;

export const DEFAULT_REPO = 'terramind-org/frontier';

export interface ExecResult {
  code: number;
  stdout: string;
  stderr: string;
}

/** Every git/gh call goes through this, so tests can record commands instead of running them. */
export type Exec = (cmd: string, args: string[], opts?: { cwd?: string }) => Promise<ExecResult>;

export const realExec: Exec = async (cmd, args, opts) => {
  try {
    const p = Bun.spawn([cmd, ...args], { cwd: opts?.cwd, stdout: 'pipe', stderr: 'pipe', stdin: 'ignore' });
    const [stdout, stderr, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
    return { code, stdout, stderr };
  } catch (e) {
    return { code: 127, stdout: '', stderr: (e as Error).message };
  }
};

export interface SubmitOptions {
  root: string;
  dir: string;
  yes: boolean;
  /** Print one JSON object instead of text. */
  json?: boolean;
  repo: string;
  exec?: Exec;
  /** Defaults to a pause between push retries; tests pass a no-op. */
  sleep?: (ms: number) => Promise<void>;
  /** Defaults to the same check `bun frontier check` runs. */
  check?: (root: string, dir: string) => Promise<CheckOutcome>;
  log?: (line: string) => void;
}

const REPO_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

function verdictLine(r: VerdictResult): string {
  const summary = plainSummary(r);
  if (r.result === 'rejected') return `rejected: ${summary}`;
  if (r.result === 'verified') return `verified locally: ${summary}`;
  if (r.result === 'unchecked') return `unchecked: ${summary}`;
  return `no local verdict (${summary}); CI will check this attempt`;
}

const list = (items: string[]) => (items.length ? items.map((i) => `- ${i}`).join('\n') : '- none');

/** The PR body. `.github/PULL_REQUEST_TEMPLATE.md` mirrors this structure for hand-made PRs. */
export function prBody(attempt: Attempt, problem: Problem, result: VerdictResult, repo: string): string {
  const people = attempt.people.map((p) => `${p.name}${p.github ? ` (@${p.github})` : ''}: ${p.role}`);
  const models = attempt.models.map((m) => `${m.name} (${m.provider}): ${m.role}`);
  return `## Attempt: ${problem.title}

- **Problem:** \`${problem.id}\` ([problem file](https://github.com/${repo}/blob/HEAD/problems/${problem.id}.yaml))
- **Attempt:** \`${attempt.id}\`
- **Kind:** ${attempt.kind}
- **Mode:** ${attempt.mode}
- **Local verdict:** ${verdictLine(result).replace(/\.$/, "")}. CI re-checks every attempt; the verdict recorded on \`main\` is the one that counts.

### Claim

${attempt.claim}

### Models and tools

${list(models)}

### People

${list(people)}

### Declarations

- [x] I have the right to submit this work, and I submit it under CC BY 4.0.
- [x] The models, tools and people listed above are the complete disclosure of how this was produced.
`;
}

export interface Plan {
  repo: string;
  defaultBranch: string;
  login: string;
  canPush: boolean;
  branch: string;
  head: string;
  pushUrl: string;
  attemptRel: string;
  title: string;
  body: string;
  commitMessage: string;
  steps: string[];
}

class Fail extends Error {}
class GhFail extends Error {
  constructor(readonly problem: GhProblem) {
    super(problem.message);
  }
}

/** Why the GitHub side is unavailable; each kind has its own note. */
export type GhProblemKind = 'gh-missing' | 'not-logged-in' | 'repo-not-found' | 'no-network' | 'other';

export interface GhProblem {
  kind: GhProblemKind;
  message: string;
}

const GH_HELP = `The GitHub CLI (gh) is not installed.
  Install: https://cli.github.com  (macOS: brew install gh; Debian/Ubuntu: sudo apt install gh)
  Then log in: gh auth login
Run this command again afterwards. Your attempt is untouched and can also be submitted by hand: see CONTRIBUTING.md.`;

const NETWORK_RE = /could not resolve host|no such host|dial tcp|connection (refused|reset|timed out)|network is unreachable|timed? ?out|error connecting to|tls handshake|i\/o timeout|temporary failure in name resolution|offline|EAI_AGAIN|ENOTFOUND|ECONNREFUSED/i;
const AUTH_RE = /HTTP 401|bad credentials|not logged in|gh auth login|authentication|requires authentication|no oauth token|token .*(invalid|expired)/i;
const NOT_FOUND_RE = /HTTP 404|not found|could not resolve to a repository|HTTP 403|forbidden|resource not accessible/i;

/** Sort a failed `gh` call into the note the human needs. */
export function classifyGhFailure(stderr: string, what: string, repo: string): GhProblem {
  const detail = stderr.trim().split('\n')[0] ?? '';
  if (NETWORK_RE.test(stderr)) {
    return {
      kind: 'no-network',
      message: `Cannot reach github.com (${detail || 'no response'}).\n  Check your network connection, proxy or VPN, then run this command again. Nothing was changed.`,
    };
  }
  if (AUTH_RE.test(stderr)) {
    return {
      kind: 'not-logged-in',
      message: `You are not logged in to the GitHub CLI, or your login has expired (${detail || 'gh auth failed'}).\n  Log in: gh auth login\nThen run this command again.`,
    };
  }
  if (NOT_FOUND_RE.test(stderr)) {
    return {
      kind: 'repo-not-found',
      message: `The repository ${repo} was not found, or your GitHub account cannot see it (while trying to ${what}: ${detail}).\n  Check the name (the default is ${DEFAULT_REPO}), that the repository is public or your account has access, and which account \`gh auth status\` shows.`,
    };
  }
  return { kind: 'other', message: `could not ${what}: ${detail || 'gh failed'}` };
}

/** Returns the process exit code. */
export async function submit(o: SubmitOptions): Promise<number> {
  const exec = o.exec ?? realExec;
  const out = o.log ?? ((l: string) => console.log(l));
  const err = (l: string) => (o.log ? o.log(l) : console.error(l));
  const sleep = o.sleep ?? ((ms: number) => new Promise<void>((r) => setTimeout(r, ms)));
  const dir = resolve(o.dir);

  if (!REPO_RE.test(o.repo)) throw new UsageError(`--repo must look like owner/name, got "${o.repo}"`);

  const emit = (obj: unknown) => out(JSON.stringify(obj, null, 2));
  const say = (l: string) => {
    if (!o.json) out(l);
  };
  const warn = (l: string) => {
    if (!o.json) err(l);
  };

  const issues = await validateAttemptDir(o.root, dir);
  if (issues.length) {
    if (o.json) emit({ ok: false, error: 'invalid', issues: issues.map((i) => `${i.path}: ${i.message}`) });
    else {
      err('This attempt is not valid, so it will not be submitted:');
      for (const i of issues) err(`  ${i.path}: ${i.message}`);
    }
    return 1;
  }
  const outcome = await (o.check ?? checkAttempt)(o.root, dir);
  if ('invalid' in outcome) {
    if (o.json) emit({ ok: false, error: 'invalid', issues: outcome.invalid });
    else {
      err('This attempt is not valid, so it will not be submitted:');
      for (const l of outcome.invalid) err(`  ${l}`);
    }
    return 1;
  }
  const { attempt, problem, result } = outcome;
  if (result.result === 'rejected') {
    warn(`WARNING: the local check REJECTED this attempt: ${plainSummary(result)}`);
    warn('It can still be submitted (failures are recorded as data), but the PR will say so. Do not describe it as a proof.');
  } else if (result.result === 'error') {
    warn(`Note: no local verdict (${plainSummary(result)}). CI will check the attempt.`);
  }

  // Tooling: gh installed and logged in; the repo readable. A dry run degrades to a generic plan so the
  // human can still review the PR body; a real submit stops.
  const [owner, name] = o.repo.split('/') as [string, string];
  let canPush = false;
  let defaultBranch = 'main';
  let login = '<your-login>';
  let unavailable: GhProblem | null = null;
  if ((await exec('gh', ['--version'])).code !== 0) {
    unavailable = { kind: 'gh-missing', message: GH_HELP };
  } else {
    const auth = await exec('gh', ['auth', 'status']);
    if (auth.code !== 0) {
      const text = `${auth.stderr}\n${auth.stdout}`;
      unavailable = NETWORK_RE.test(text)
        ? classifyGhFailure(text, 'check your GitHub login', o.repo)
        : { kind: 'not-logged-in', message: 'You are not logged in to the GitHub CLI.\n  Log in: gh auth login\nThen run this command again.' };
    }
  }
  if (unavailable === null) {
    const ghValue = async (args: string[], what: string): Promise<string> => {
      const r = await exec('gh', args);
      if (r.code !== 0) throw new GhFail(classifyGhFailure(`${r.stderr}\n${r.stdout}`, what, o.repo));
      return r.stdout.trim();
    };
    try {
      canPush = (await ghValue(['api', `repos/${o.repo}`, '--jq', '.permissions.push'], `read ${o.repo}`)) === 'true';
      defaultBranch = await ghValue(['api', `repos/${o.repo}`, '--jq', '.default_branch'], `read the default branch of ${o.repo}`);
      login = await ghValue(['api', 'user', '--jq', '.login'], 'read your GitHub login');
    } catch (e) {
      if (!(e instanceof GhFail)) throw e;
      unavailable = e.problem;
    }
  }
  if (unavailable !== null) {
    if (o.yes) {
      if (o.json) emit({ ok: false, error: unavailable.kind, tooling: unavailable });
      else err(unavailable.message);
      return 1;
    }
    warn(`NOTE: ${unavailable.message}\nShowing a generic plan; a real submit needs this fixed first.`);
  }

  const branch = `attempt/${attempt.id}`;
  const headOwner = canPush ? owner : login;
  const pushUrl = `https://github.com/${headOwner}/${name}.git`;
  const attemptRel = `attempts/${attempt.problem}/${attempt.id}`;
  const plan: Plan = {
    repo: o.repo,
    defaultBranch,
    login,
    canPush,
    branch,
    head: `${headOwner}:${branch}`,
    pushUrl,
    attemptRel,
    title: `Attempt: ${problem.id} — ${attempt.title}`,
    body: prBody(attempt, problem, result, o.repo),
    commitMessage: `Attempt ${attempt.id} on ${problem.id}`,
    steps: [],
  };
  plan.steps = [
    ...(unavailable !== null ? ['if you cannot push to the repo: gh repo fork (no remote) and push to your fork; otherwise push to the repo directly'] : canPush ? [`push access to ${o.repo}: yes, pushing to it directly`] : [`gh repo fork ${o.repo} --remote=false   (no push access; pushing to ${login}/${name})`]),
    `fetch ${o.repo} ${defaultBranch} and create a temporary git worktree from it (your working tree and other changes are not touched)`,
    `create branch ${branch}, copy ${attemptRel}/ into the worktree and commit only that directory: "${plan.commitMessage}"`,
    `git push ${pushUrl} ${branch}`,
    `gh pr create --repo ${o.repo} --head ${plan.head} --title "${plan.title}"`,
    'remove the temporary worktree',
  ];

  const report = { plan, body: plan.body, verdict: result, tooling: unavailable ?? { kind: 'ok', message: 'gh is installed, logged in and can read the repo' } };
  say(`Plan for ${attempt.id} (${attempt.kind}) on ${problem.id}:`);
  plan.steps.forEach((s, i) => say(`  ${i + 1}. ${s}`));
  say('\nPR title:\n  ' + plan.title);
  say('\nPR body:\n' + plan.body.split('\n').map((l) => `  ${l}`).join('\n'));
  if (!o.yes) {
    if (o.json) emit({ ok: true, dry_run: true, ...report });
    else out('\nDry run: nothing was changed. Show this plan to your human, then re-run with --yes to submit.');
    return 0;
  }

  const tmp = mkdtempSync(join(tmpdir(), 'frontier-submit-'));
  const wt = join(tmp, 'wt');
  let worktreeAdded = false;
  try {
    const step = async (cmd: string, args: string[], cwd: string | undefined, what: string): Promise<ExecResult> => {
      const r = await exec(cmd, args, { cwd });
      if (r.code !== 0) throw new Fail(`${what} failed: ${(r.stderr || r.stdout).trim()}`);
      return r;
    };
    if (!canPush) {
      say(`Forking ${o.repo} ...`);
      await step('gh', ['repo', 'fork', o.repo, '--remote=false'], undefined, 'gh repo fork');
    }
    await step('git', ['fetch', '--no-tags', `https://github.com/${o.repo}.git`, defaultBranch], o.root, 'git fetch');
    await step('git', ['worktree', 'add', '--detach', wt, 'FETCH_HEAD'], o.root, 'git worktree add');
    worktreeAdded = true;
    await step('git', ['checkout', '-b', branch], wt, 'git checkout');
    // Copy the attempt directory in; a submitter never ships a verdict.json and symlinks never leave the dir.
    const dest = join(wt, attemptRel);
    cpSync(dir, dest, {
      recursive: true,
      filter: (src) => !lstatSync(src).isSymbolicLink() && !(src.endsWith('/verdict.json') || src.endsWith('\\verdict.json')),
    });
    await step('git', ['add', '--', attemptRel], wt, 'git add');
    await step('git', ['commit', '-m', plan.commitMessage], wt, 'git commit');
    const credential = ['-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential'];
    let pushed: ExecResult = { code: 1, stdout: '', stderr: '' };
    for (let attemptNo = 0; attemptNo < 4 && pushed.code !== 0; attemptNo++) {
      if (attemptNo > 0) await sleep(3000); // a fresh fork can take a few seconds to accept pushes
      pushed = await exec('git', [...credential, 'push', pushUrl, branch], { cwd: wt });
    }
    if (pushed.code !== 0) throw new Fail(`git push failed: ${(pushed.stderr || pushed.stdout).trim()}`);
    const pr = await step(
      'gh',
      ['pr', 'create', '--repo', o.repo, '--head', plan.head, '--title', plan.title, '--body', plan.body],
      undefined,
      'gh pr create',
    );
    if (o.json) emit({ ok: true, dry_run: false, ...report, pr_url: pr.stdout.trim() });
    else out(`Opened: ${pr.stdout.trim()}`);
    return 0;
  } catch (e) {
    if (!(e instanceof Fail)) throw e;
    if (o.json) emit({ ok: false, error: 'submit-failed', message: e.message });
    else err(`submit: ${e.message}`);
    return 1;
  } finally {
    if (worktreeAdded) await exec('git', ['worktree', 'remove', '--force', wt], { cwd: o.root });
    rmSync(tmp, { recursive: true, force: true });
  }
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { yes: { type: 'boolean' }, json: { type: 'boolean' }, repo: { type: 'string' } });
  if (positionals.length !== 1) throw new UsageError('submit needs exactly one attempt directory');
  return submit({ root: repoRoot(), dir: positionals[0]!, yes: values.yes === true, json: values.json === true, repo: values.repo ?? DEFAULT_REPO });
}
