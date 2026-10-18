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

export const Problem = z
  .object({
    schema: z.literal(1),
    id: ProblemId,
    title: z.string().min(1),
    field: z.enum(['mathematics', 'computer-science', 'physics']),
    tier: z.enum(['proof', 'witness']),
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
    upstream_status: z.enum(['open']),
    lean: z
      .object({
        module: z.string(),
        decl: z.string(),
        statement: z.string(),
      })
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

export const ProblemStatus = z.enum(['open', 'proof-checked', 'disproof-checked', 'record-improved']);

export const Index = z.object({
  schema: z.literal(1),
  generated_at: z.iso.datetime(),
  repo_commit: z.string(),
  sources: z.array(z.object({ name: z.string(), repo: z.url(), commit: z.string(), licence: z.string() })),
  counts: z.object({
    problems: z.number(),
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
        }).extend({ verdict: VerdictResult.nullable() }),
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
export type Index = z.infer<typeof Index>;

export type AttemptKind = Attempt['kind'];

/** The file each attempt kind must ship. */
export const KIND_FILE: Record<AttemptKind, string> = {
  proof: 'solution.lean',
  disproof: 'solution.lean',
  witness: 'witness.json',
  writeup: 'writeup.md',
};

/** Problem tier each non-writeup kind may target; writeup is allowed on any tier. */
export const KIND_TIER: Record<Exclude<AttemptKind, 'writeup'>, Problem['tier']> = {
  proof: 'proof',
  disproof: 'proof',
  witness: 'witness',
};

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
  return issues;
}

/** Cross-field attempt rules against the problem it targets; returns readable messages. */
export function attemptIssues(a: Attempt, problem: Problem): string[] {
  const issues: string[] = [];
  if (a.problem !== problem.id) issues.push(`attempt targets "${a.problem}" but was checked against "${problem.id}"`);
  if (a.kind !== 'writeup' && KIND_TIER[a.kind] !== problem.tier) {
    issues.push(`kind "${a.kind}" is not allowed on a "${problem.tier}" problem (needs tier "${KIND_TIER[a.kind]}")`);
  }
  const expected = KIND_FILE[a.kind];
  if (!a.files.includes(expected)) issues.push(`kind "${a.kind}" needs "${expected}" in files`);
  for (const f of a.files) {
    if (!isSafeRelativePath(f)) issues.push(`file "${f}" must be a relative path without ".." or leading "/"`);
  }
  if (a.mode !== 'human_only' && a.models.length === 0) {
    issues.push(`mode "${a.mode}" requires at least one entry in models`);
  }
  return issues;
}
