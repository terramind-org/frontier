import { REVIEW_DISCLAIMER, reviewAgreement } from '../schema.ts';
import type { ReviewOpinion, ReviewResult } from '../schema.ts';
import type { PanelConfig, ReviewerConfig } from './config.ts';
import { buildPrompt, ModelReply } from './prompt.ts';
import type { ReviewInput } from './prompt.ts';
import { callProvider, TransportError } from './providers.ts';
import type { FetchFn } from './providers.ts';

export interface ReviewerUsage {
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
}

export interface PanelOutcome {
  /** The review, or null when no reviewer is configured or no reviewer got any reply (then it is retried later). */
  review: Omit<ReviewResult, 'reviewed_at'> | null;
  /** Why there is no review, when there is none. */
  reason: string | null;
  skipped: { provider: string; model: string; reason: string }[];
  usage: ReviewerUsage[];
  /** Input tokens estimated before any call (4 characters per token), for a dry estimate. */
  estimatedInputTokens: number;
}

export interface PanelOptions {
  env?: Record<string, string | undefined>;
  fetch?: FetchFn;
  retryDelayMs?: number;
  timeoutMs?: number;
}

/** Reviewers whose key is set, and the ones skipped for a missing key. */
export function configuredReviewers(config: PanelConfig, env: Record<string, string | undefined>) {
  const active: { reviewer: ReviewerConfig; key: string }[] = [];
  const skipped: PanelOutcome['skipped'] = [];
  for (const reviewer of config.reviewers) {
    const key = env[reviewer.api_key_env]?.trim();
    if (key) active.push({ reviewer, key });
    else skipped.push({ provider: reviewer.provider, model: reviewer.model, reason: `${reviewer.api_key_env} is not set` });
  }
  return { active, skipped };
}

function cost(r: ReviewerConfig, input: number, output: number): number {
  return (input * r.price_usd_per_mtok.input + output * r.price_usd_per_mtok.output) / 1_000_000;
}

/** Turn a model's raw text into an opinion; anything that does not match the contract is `could-not-assess`. */
export function toOpinion(r: ReviewerConfig, text: string | null, problem: string | null): ReviewOpinion {
  const base = { model: r.model, provider: r.provider };
  if (text === null) return { ...base, assessment: 'could-not-assess', issues: [], summary: `No assessment: ${problem ?? 'no reply'}.` };
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    return { ...base, assessment: 'could-not-assess', issues: [], summary: 'No assessment: the reply was not valid JSON.' };
  }
  const parsed = ModelReply.safeParse(raw);
  if (!parsed.success) {
    const why = parsed.error.issues.slice(0, 3).map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ');
    return { ...base, assessment: 'could-not-assess', issues: [], summary: `No assessment: the reply did not match the review schema (${why}).` };
  }
  const reply = parsed.data;
  const issues = reply.issues.map((i) => ({
    severity: i.severity,
    ...(i.location.trim() ? { location: i.location.trim() } : {}),
    explanation: i.explanation,
  }));
  // A fatal or major issue means issues were found, whatever label the model put on it.
  const serious = issues.some((i) => i.severity !== 'minor');
  const assessment = reply.assessment === 'no-issues-found' && serious ? 'issues-found' : reply.assessment;
  return { ...base, assessment, issues, summary: reply.summary };
}

/** Run every configured reviewer on one writeup, in parallel. Never executes anything from the attempt. */
export async function runPanel(input: ReviewInput, config: PanelConfig, opts: PanelOptions = {}): Promise<PanelOutcome> {
  const env = opts.env ?? process.env;
  const fetchFn = opts.fetch ?? ((url, init) => fetch(url, init));
  const prompt = buildPrompt(input, { maxInputChars: config.max_input_chars, maxStatementChars: config.max_statement_chars });
  const { active, skipped } = configuredReviewers(config, env);
  const base = { skipped, estimatedInputTokens: prompt.estimatedInputTokens };
  if (!active.length) return { ...base, review: null, reason: 'no reviewers configured (no API key is set)', usage: [] };

  const results = await Promise.all(
    active.map(async ({ reviewer, key }) => {
      try {
        const reply = await callProvider(reviewer, key, prompt.system, prompt.user, config.max_output_tokens, {
          fetch: fetchFn,
          retryDelayMs: opts.retryDelayMs,
          timeoutMs: opts.timeoutMs,
        });
        return { reviewer, opinion: toOpinion(reviewer, reply.text, reply.problem), usage: reply.usage, transport: null };
      } catch (e) {
        if (!(e instanceof TransportError)) throw e;
        const opinion = toOpinion(reviewer, null, `the API call failed (${e.message})`);
        return { reviewer, opinion, usage: { input: 0, output: 0 }, transport: e.message };
      }
    }),
  );
  const usage = results.map(({ reviewer, usage: u }) => ({
    provider: reviewer.provider,
    model: reviewer.model,
    input_tokens: u.input,
    output_tokens: u.output,
    cost_usd: cost(reviewer, u.input, u.output),
  }));
  if (results.every((r) => r.transport !== null)) {
    return { ...base, review: null, reason: `no reviewer got a reply: ${results.map((r) => `${r.reviewer.provider}: ${r.transport}`).join('; ')}`, usage };
  }
  const panel = results.map((r) => r.opinion);
  const notes = [...skipped.map((s) => `${s.provider} ${s.model} did not take part: ${s.reason}.`), ...prompt.notes];
  return {
    ...base,
    review: { disclaimer: REVIEW_DISCLAIMER, panel, agreement: reviewAgreement(panel), notes },
    reason: null,
    usage,
  };
}
