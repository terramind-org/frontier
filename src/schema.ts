import { z } from 'zod';
import { isAttemptId, isProblemId, MAX_PROBLEM_ID_LENGTH } from './ids.ts';

export const ProblemId = z
  .string()
  .max(MAX_PROBLEM_ID_LENGTH)
  .refine(isProblemId, { message: 'must match ^[a-z0-9][a-z0-9.-]*[a-z0-9]$' });
export const AttemptId = z
  .string()
  .refine(isAttemptId, { message: 'must look like 20261018-login-3f9a1c' });

export const Reference = z.object({ label: z.string().min(1), url: z.url() });

/** Tag of practice problems: upstream `textbook` results, provable, never counted as open problems. */
export const PRACTICE_TAG = 'practice';

/** The claim `new` writes; an attempt still carrying it has not said what it claims. */
export const PLACEHOLDER_CLAIM = 'Describe exactly what this attempt claims.';

/** Upstream definition a statement uses, shown so the statement can be read. */
export const LeanDefinition = z
  .object({
    name: z.string().min(1), // full Lean name
    kind: z.enum(['def', 'abbrev', 'structure', 'inductive', 'class']),
    text: z.string(), // source text, at most 4,000 characters (then `…`)
    url: z.url(), // permalink with #L<line>
  })
  .strict();

export const Difficulty = z
  .object({
    level: z.enum(['practice', 'approachable', 'hard', 'very-hard']),
    note: z.string().min(1),
  })
  .strict();

/** Tag of prose problems whose open status no source certifies (owner-supplied catalogues without a status). */
export const OPEN_STATUS_UNVERIFIED_TAG = 'open-status-unverified';
/** Tag of problems a source lists as partially solved (still open). */
export const PARTIALLY_SOLVED_TAG = 'partially-solved';

/** Every discipline a problem source uses; prose problems come from all of them. */
export const FIELDS = ['mathematics', 'computer-science', 'physics', 'economics', 'biology'] as const;

/**
 * `proof`: a Lean statement the checker judges. `witness`: an object a verifier judges against a record.
 * `prose`: an open problem stated in words (any discipline); only writeups, never machine-checked.
 */
export const TIERS = ['proof', 'witness', 'prose'] as const;

/** What `show`, `pick` and `new` say about a prose problem. */
export const PROSE_NOTE =
  'prose: an open problem stated in words. Only writeups are accepted; they are never machine-checked. A labelled AI review of a writeup is an opinion, not a verdict, and never changes the status.';

export const Problem = z
  .object({
    schema: z.literal(1),
    id: ProblemId,
    title: z.string().min(1),
    field: z.enum(FIELDS),
    tier: z.enum(TIERS),
    statement: z.string().min(1),
    ams: z.array(z.number().int().min(0).max(99)),
    tags: z.array(z.string()),
    references: z.array(Reference),
    source: z.object({
      name: z.string(),
      repo: z.url(),
      commit: z.string().regex(/^[0-9a-f]{40}$/).optional(),
      path: z.string().optional(),
      url: z.url(),
      licence: z.string(),
    }),
    upstream_status: z.enum(['open', 'partially-solved', 'textbook']),
    // Identifiers of the same problem in other catalogues, `scheme:identifier` (e.g. `unsolvedmath:2965`,
    // `erdosproblems:428`); used to deduplicate imports.
    external_ids: z.array(z.string().regex(/^[a-z0-9-]+:\S+$/)).optional(),
    difficulty: Difficulty.optional(),
    lean: z
      .object({
        module: z.string(),
        decl: z.string(),
        statement: z.string(),
        // Lines a scaffold needs before the theorem: `open` for enclosing namespaces, upstream opens,
        // local notation in effect at the declaration (verbatim).
        context: z.array(z.string()),
        definitions: z.array(LeanDefinition),
      })
      .strict()
      .optional(),
    witness: z
      .object({
        verifier: z.string(),
        params: z.record(z.string(), z.union([z.number(), z.string(), z.boolean()])),
        objective: z.enum(['maximize', 'minimize']),
        best_known: z.object({ value: z.number(), reference: Reference, note: z.string().optional() }),
        format: z.string(),
      })
      .optional(),
    added: z.iso.date(),
  })
  .strict();

export const Attempt = z
  .object({
    schema: z.literal(1),
    id: AttemptId,
    problem: ProblemId,
    kind: z.enum(['proof', 'disproof', 'witness', 'writeup']),
    title: z.string().min(1).max(200),
    claim: z.string().min(1).max(4000),
    files: z.array(z.string()).min(1),
    submitter: z.object({ github: z.string().regex(/^[A-Za-z0-9-]{1,39}$/) }),
    people: z.array(z.object({ name: z.string(), github: z.string().optional(), role: z.string() })),
    models: z.array(z.object({ name: z.string(), provider: z.string(), role: z.string() })),
    mode: z.enum(['ai_only', 'human_ai', 'human_only']),
    created: z.iso.date(),
    licence: z.literal('CC-BY-4.0'),
    declarations: z.object({ rights: z.literal(true), disclosure_complete: z.literal(true) }),
  })
  .strict();

export const VerdictResult = z.object({
  checker: z.enum(['lean', 'witness', 'none']),
  result: z.enum(['verified', 'rejected', 'unchecked', 'error']),
  summary: z.string(),
  lean: z
    .object({
      toolchain: z.string(),
      fc_commit: z.string(),
      target: z.enum(['statement', 'negation']),
      axioms: z.array(z.string()),
      reason: z.string().optional(),
    })
    .optional(),
  witness: z
    .object({
      valid: z.boolean(),
      value: z.number().optional(),
      best_known: z.number(),
      beats_best_known: z.boolean(),
      ties_best_known: z.boolean(),
      reason: z.string().optional(),
    })
    .optional(),
});

export const Verdict = VerdictResult.extend({
  schema: z.literal(1),
  attempt: AttemptId,
  checked_at: z.iso.datetime(),
  checker_version: z.string(),
  run_url: z.url().optional(),
}).strict();

/**
 * The label every AI review carries, verbatim, wherever it is shown. A review is an opinion of language
 * models about a writeup: never a verdict, never a check, never an input to a problem's status.
 */
export const REVIEW_LABEL = 'AI review (opinion)';
export const REVIEW_DISCLAIMER =
  'AI review (opinion): language models read this writeup and said whether, in their opinion, it supports its claim. ' +
  'This is not a verdict and not a check. The models can be wrong in either direction, "no issues found" does not mean ' +
  'the writeup is correct, and a review never changes a problem\'s status.';

export const REVIEW_ASSESSMENTS = ['no-issues-found', 'issues-found', 'could-not-assess'] as const;
export const REVIEW_SEVERITIES = ['fatal', 'major', 'minor'] as const;

export const ReviewIssue = z
  .object({
    severity: z.enum(REVIEW_SEVERITIES),
    location: z.string().min(1).optional(),
    explanation: z.string().min(1),
  })
  .strict();

/** One panel member's opinion. */
export const ReviewOpinion = z
  .object({
    model: z.string().min(1),
    provider: z.string().min(1),
    assessment: z.enum(REVIEW_ASSESSMENTS),
    issues: z.array(ReviewIssue),
    summary: z.string().min(1),
  })
  .strict();

/** `unanimous` when every panel member gave the same assessment, else `split`. */
export function reviewAgreement(panel: readonly { assessment: string }[]): 'unanimous' | 'split' {
  return panel.every((p) => p.assessment === panel[0]?.assessment) ? 'unanimous' : 'split';
}

/** The part of a review the Index carries. */
export const ReviewResult = z
  .object({
    reviewed_at: z.iso.datetime(),
    disclaimer: z.literal(REVIEW_DISCLAIMER),
    panel: z.array(ReviewOpinion).min(1),
    agreement: z.enum(['unanimous', 'split']),
    // What the reader should know about how the review was made: reviewers skipped (no key), truncated input.
    notes: z.array(z.string()),
  })
  .strict();

/** `review.json` in a writeup attempt directory, written only by CI on main (like verdict.json). */
export const Review = z
  .object({
    schema: z.literal(1),
    attempt: AttemptId,
    reviewed_at: z.iso.datetime(),
    reviewer_version: z.string().min(1), // git commit of the reviewing code and review.config.json
    run_url: z.url().optional(),
    disclaimer: z.literal(REVIEW_DISCLAIMER),
    panel: z.array(ReviewOpinion).min(1),
    agreement: z.enum(['unanimous', 'split']),
    notes: z.array(z.string()),
  })
  .strict()
  .refine((r) => r.agreement === reviewAgreement(r.panel), {
    message: 'agreement must be "unanimous" exactly when every panel member gave the same assessment',
    path: ['agreement'],
  });

export const ProblemStatus = z.enum(['open', 'proof-checked', 'disproof-checked', 'record-improved', 'practice']);

export const Index = z.object({
  schema: z.literal(1),
  generated_at: z.iso.datetime(),
  repo_commit: z.string(),
  sources: z.array(z.object({ name: z.string(), repo: z.url(), commit: z.string(), licence: z.string() })),
  counts: z.object({
    problems: z.number(), // every problem except practice ones
    practice: z.number(),
    attempts: z.number(),
    verified: z.number(),
    by_tier: z.record(z.string(), z.number()),
    by_status: z.record(z.string(), z.number()),
  }),
  problems: z.array(
    Problem.extend({
      status: ProblemStatus,
      attempts: z.array(
        Attempt.pick({
          id: true,
          kind: true,
          title: true,
          claim: true,
          submitter: true,
          models: true,
          mode: true,
          created: true,
        }).extend({
          verdict: VerdictResult.nullable(),
          // An opinion, shown as "AI review (opinion)"; never used for status. Absent in indexes built before reviews.
          review: ReviewResult.nullable().default(null),
        }),
      ),
    }),
  ),
});

export type Reference = z.infer<typeof Reference>;
export type Problem = z.infer<typeof Problem>;
export type Attempt = z.infer<typeof Attempt>;
export type VerdictResult = z.infer<typeof VerdictResult>;
export type Verdict = z.infer<typeof Verdict>;
export type ProblemStatus = z.infer<typeof ProblemStatus>;
export type ReviewIssue = z.infer<typeof ReviewIssue>;
export type ReviewOpinion = z.infer<typeof ReviewOpinion>;
export type ReviewResult = z.infer<typeof ReviewResult>;
export type Review = z.infer<typeof Review>;
export type LeanDefinition = z.infer<typeof LeanDefinition>;
export type Difficulty = z.infer<typeof Difficulty>;
export type Index = z.infer<typeof Index>;

export type AttemptKind = Attempt['kind'];

/** The file each attempt kind must ship. */
export const KIND_FILE: Record<AttemptKind, string> = {
  proof: 'solution.lean',
  disproof: 'solution.lean',
  witness: 'witness.json',
  writeup: 'writeup.md',
};

/** Problem tier each non-writeup kind may target; writeup is allowed on any tier and is the only kind on `prose`. */
export const KIND_TIER: Record<Exclude<AttemptKind, 'writeup'>, Problem['tier']> = {
  proof: 'proof',
  disproof: 'proof',
  witness: 'witness',
};

/**
 * Extra `.lean` files of a writeup (e.g. partial lemmas): listed in `files`, shown with the writeup,
 * never compiled for a verdict. Other kinds have none.
 */
export function writeupLeanFiles(a: Pick<Attempt, 'kind' | 'files'>): string[] {
  return a.kind === 'writeup' ? a.files.filter((f) => f.endsWith('.lean')) : [];
}

/** Whether a relative path stays inside its directory: no `..`, no absolute path, no empty segments. */
export function isSafeRelativePath(p: string): boolean {
  if (p === '' || p.startsWith('/') || p.startsWith('\\') || /^[A-Za-z]:/.test(p)) return false;
  return p.split(/[\\/]/).every((seg) => seg !== '' && seg !== '.' && seg !== '..');
}

/** Cross-field problem rules; returns readable messages, empty when fine. */
export function problemIssues(p: Problem): string[] {
  const issues: string[] = [];
  if (p.tier === 'proof' && !p.lean) issues.push('tier "proof" requires a `lean` block');
  if (p.tier === 'witness' && !p.witness) issues.push('tier "witness" requires a `witness` block');
  if (p.tier === 'proof' && p.witness) issues.push('tier "proof" must not have a `witness` block');
  if (p.tier === 'witness' && p.lean) issues.push('tier "witness" must not have a `lean` block');
  if (p.tier === 'prose' && (p.lean || p.witness)) issues.push('tier "prose" must have neither a `lean` nor a `witness` block');
  if (p.tier === 'prose' && p.difficulty) issues.push('tier "prose" has no difficulty rating');
  if (p.tier === 'prose' && p.tags.includes(PRACTICE_TAG)) issues.push('a `practice` problem cannot be tier "prose"');
  if ((p.upstream_status === 'partially-solved') !== p.tags.includes(PARTIALLY_SOLVED_TAG)) {
    issues.push(`upstream_status "partially-solved" and the \`${PARTIALLY_SOLVED_TAG}\` tag go together`);
  }
  const practice = p.tags.includes(PRACTICE_TAG);
  if (practice && p.upstream_status !== 'textbook') issues.push('a `practice` problem must have upstream_status "textbook"');
  if (!practice && p.upstream_status === 'textbook') issues.push('upstream_status "textbook" is only for problems tagged `practice`');
  if (practice && p.difficulty?.level !== 'practice') issues.push('a `practice` problem needs difficulty.level "practice"');
  if (!practice && p.difficulty?.level === 'practice') issues.push('difficulty.level "practice" is only for problems tagged `practice`');
  return issues;
}

/**
 * Cross-field attempt rules against the problem it targets; returns readable messages. `scaffold`
 * skips the placeholder-claim rule, for `new`, which writes the placeholder on purpose.
 */
export function attemptIssues(a: Attempt, problem: Problem, opts: { scaffold?: boolean } = {}): string[] {
  const issues: string[] = [];
  if (a.problem !== problem.id) issues.push(`attempt targets "${a.problem}" but was checked against "${problem.id}"`);
  if (problem.tier === 'prose' && a.kind !== 'writeup') {
    issues.push(`kind "${a.kind}" is not allowed on a "prose" problem: prose problems take only writeups, which are never machine-checked`);
  } else if (a.kind !== 'writeup' && KIND_TIER[a.kind] !== problem.tier) {
    issues.push(`kind "${a.kind}" is not allowed on a "${problem.tier}" problem (needs tier "${KIND_TIER[a.kind]}")`);
  }
  const expected = KIND_FILE[a.kind];
  if (!a.files.includes(expected)) issues.push(`kind "${a.kind}" needs "${expected}" in files`);
  for (const f of a.files) {
    if (!isSafeRelativePath(f)) issues.push(`file "${f}" must be a relative path without ".." or leading "/"`);
  }
  if (!opts.scaffold && a.claim.trim() === PLACEHOLDER_CLAIM) {
    issues.push('claim is still the scaffold placeholder; replace it with exactly what this attempt claims');
  }
  if (a.mode !== 'human_only' && a.models.length === 0) {
    issues.push(`mode "${a.mode}" requires at least one entry in models`);
  }
  return issues;
}
