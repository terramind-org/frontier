import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join, relative, resolve, sep } from 'node:path';
import { parse as parseYamlText } from 'yaml';
import { parse, UsageError } from '../args.ts';
import { loadProblem, repoRoot, scanAttempts, writeJson } from '../repo.ts';
import { loadPanelConfig, maxAttemptsPerRun } from '../review/config.ts';
import type { PanelConfig } from '../review/config.ts';
import { runPanel } from '../review/panel.ts';
import type { PanelOptions, PanelOutcome } from '../review/panel.ts';
import { Attempt, KIND_FILE, Review, REVIEW_LABEL, ReviewResult } from '../schema.ts';
import { isSubmitOnlyIssue } from './check.ts';
import { validateAttemptDir } from './validate.ts';

export const help = `${REVIEW_LABEL} of a writeup by a panel of language models. An opinion, never a verdict or a check.

Usage: bun frontier review <attempt-dir> [--json] [--write [--run-url <url>] [--force] [--from <file>]]
       bun frontier review --pending [--json]

Each reviewer in review.config.json whose API key is set (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY by
default) reads the problem, the claim and writeup.md as quoted data and says whether the writeup supports exactly
what the claim says. Reviewers without a key are skipped; with no key at all there is no review. Each call costs
money on your own key; the command prints the tokens used and a cost estimate. Nothing in the attempt is run.

  --json             print {review, reason, skipped, usage} as JSON
  --write            write review.json into the attempt (CI on main only, like \`record\`; a PR adding one is rejected)
  --from <file>      with --write: write the review from an earlier \`review --json\` output instead of calling models
  --run-url <url>    the Actions run, stored in review.json
  --force            overwrite an existing review.json
  --pending          list writeup attempts without review.json, at most REVIEW_MAX_ATTEMPTS (default from the config)

A review never changes a problem's status.`;

async function gitHead(root: string): Promise<string> {
  const p = Bun.spawn(['git', 'rev-parse', 'HEAD'], { cwd: root, stdout: 'pipe', stderr: 'pipe' });
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  if (code !== 0) throw new Error(`git rev-parse HEAD failed: ${err.trim()}`);
  return out.trim();
}

/** Writeup attempts on disk that are valid and have no review.json yet, sorted, at most `max`. */
export async function pendingReviews(root: string, max: number): Promise<string[]> {
  return (await scanAttempts(undefined, root))
    .filter((a) => a.value?.kind === 'writeup' && !a.review && a.reviewErrors.length === 0 && !existsSync(join(a.dir, 'review.json')))
    .map((a) => a.relDir)
    .sort()
    .slice(0, max);
}

/** Load a writeup attempt for review. Local previews accept unconfirmed declarations; `strict` (for --write) does not. */
async function loadForReview(root: string, dir: string, strict: boolean) {
  const abs = resolve(dir);
  const issues = await validateAttemptDir(root, abs);
  const blocking = strict ? issues : issues.filter((i) => !isSubmitOnlyIssue(i.message));
  if (blocking.length) throw new Error(blocking.map((i) => `${i.path}: ${i.message}`).join('\n'));
  const raw = parseYamlText(await readFile(join(abs, 'attempt.yaml'), 'utf8')) as Record<string, unknown>;
  const attempt = Attempt.parse({ ...raw, declarations: { rights: true, disclosure_complete: true } });
  if (attempt.kind !== 'writeup') throw new Error(`only writeups get an AI review; this attempt is a ${attempt.kind} (its checker gives the verdict)`);
  const problem = (await loadProblem(attempt.problem, root))!;
  const writeup = await readFile(join(abs, KIND_FILE.writeup), 'utf8');
  return { abs, attempt, problem, writeup };
}

export interface ReviewRunOptions extends PanelOptions {
  config?: PanelConfig;
}

/** Run the panel on one attempt directory. */
export async function reviewAttempt(root: string, dir: string, opts: ReviewRunOptions & { strict?: boolean } = {}): Promise<PanelOutcome & { attemptId: string }> {
  const config = opts.config ?? (await loadPanelConfig(root));
  const { attempt, problem, writeup } = await loadForReview(root, dir, opts.strict ?? false);
  const outcome = await runPanel({ problem, attempt, writeup }, config, opts);
  return { ...outcome, attemptId: attempt.id };
}

/** Write review.json from a panel result. Throws if one exists and `force` is not set. */
export async function writeReview(
  root: string,
  dir: string,
  result: Omit<ReviewResult, 'reviewed_at'>,
  opts: { runUrl?: string; force?: boolean; now?: Date } = {},
): Promise<Review> {
  const { abs, attempt } = await loadForReview(root, dir, true);
  const target = join(abs, 'review.json');
  if (existsSync(target) && !opts.force) throw new Error(`${target} already exists (use --force to overwrite)`);
  const review = Review.parse({
    schema: 1,
    attempt: attempt.id,
    reviewed_at: (opts.now ?? new Date()).toISOString(),
    reviewer_version: await gitHead(root),
    ...(opts.runUrl ? { run_url: opts.runUrl } : {}),
    disclaimer: result.disclaimer,
    panel: result.panel,
    agreement: result.agreement,
    notes: result.notes,
  });
  await writeJson(target, review, Review);
  return review;
}

function money(n: number): string {
  return `$${n.toFixed(n < 0.01 ? 4 : 3)}`;
}

function printText(rel: string, o: PanelOutcome): void {
  const out: string[] = [];
  for (const s of o.skipped) out.push(`skipped ${s.provider} ${s.model}: ${s.reason}`);
  if (!o.review) {
    out.push(`no review: ${o.reason}`);
  } else {
    const r = o.review;
    out.push('', `${REVIEW_LABEL} of ${rel}`, r.disclaimer, '');
    for (const p of r.panel) {
      out.push(`${p.provider} ${p.model}: ${p.assessment}`, `  ${p.summary}`);
      for (const i of p.issues) out.push(`  [${i.severity}]${i.location ? ` ${i.location}:` : ''} ${i.explanation}`);
      out.push('');
    }
    out.push(`agreement: ${r.agreement}`);
    for (const n of r.notes) out.push(`note: ${n}`);
  }
  if (o.usage.length) {
    out.push('', 'usage (estimate from list prices in review.config.json):');
    for (const u of o.usage) out.push(`  ${u.provider} ${u.model}: ${u.input_tokens} in, ${u.output_tokens} out, about ${money(u.cost_usd)}`);
    out.push(`  total about ${money(o.usage.reduce((s, u) => s + u.cost_usd, 0))}`);
  }
  console.log(out.join('\n'));
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, {
    json: { type: 'boolean' },
    write: { type: 'boolean' },
    from: { type: 'string' },
    'run-url': { type: 'string' },
    force: { type: 'boolean' },
    pending: { type: 'boolean' },
  });
  const root = repoRoot();
  if (values.pending) {
    if (positionals.length) throw new UsageError('--pending takes no attempt directory');
    const dirs = await pendingReviews(root, maxAttemptsPerRun(await loadPanelConfig(root)));
    console.log(values.json ? JSON.stringify(dirs) : dirs.join('\n'));
    return 0;
  }
  if (positionals.length !== 1) throw new UsageError('review needs exactly one attempt directory');
  if (values.from !== undefined && !values.write) throw new UsageError('--from is only used with --write');
  const dir = positionals[0]!;
  const rel = relative(root, resolve(dir)).split(sep).join('/');

  let outcome: PanelOutcome;
  if (values.from !== undefined) {
    // A review computed earlier (in CI: by the job that holds the API keys but no write token).
    const raw = JSON.parse(await readFile(resolve(values.from), 'utf8')) as { review?: unknown; attempt?: unknown };
    const parsed = ReviewResult.omit({ reviewed_at: true }).safeParse(raw.review);
    if (!parsed.success) throw new Error(`${values.from} holds no valid review: ${parsed.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`).join('; ')}`);
    const { attempt } = await loadForReview(root, dir, true);
    if (raw.attempt !== attempt.id) throw new Error(`${values.from} is a review of "${String(raw.attempt)}", not "${attempt.id}"`);
    outcome = { review: parsed.data, reason: null, skipped: [], usage: [], estimatedInputTokens: 0 };
  } else {
    const r = await reviewAttempt(root, dir, { strict: values.write === true });
    outcome = r;
    if (values.json) {
      console.log(JSON.stringify({ attempt: r.attemptId, review: r.review, reason: r.reason, skipped: r.skipped, usage: r.usage, estimated_input_tokens: r.estimatedInputTokens }, null, 2));
    } else {
      printText(rel, r);
    }
  }
  if (!outcome.review) {
    // No key at all is not a failure (CI without secrets); no reply from any reviewer is, and is retried later.
    return outcome.usage.length ? 1 : 0;
  }
  if (values.write) {
    const review = await writeReview(root, dir, outcome.review, { runUrl: values['run-url'] as string | undefined, force: values.force === true });
    console.error(`wrote ${rel}/review.json (${REVIEW_LABEL}; agreement ${review.agreement})`);
  }
  return 0;
}
