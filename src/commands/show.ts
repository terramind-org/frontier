import { parse, UsageError } from '../args.ts';
import { loadAll, unknownIdMessage } from '../repo.ts';
import { PRACTICE_TAG } from '../schema.ts';
import type { VerdictResult } from '../schema.ts';

export const help = `Show one problem: statement, Lean statement with its context and definitions, or witness format,
best known, difficulty, attempts and verdicts.

Usage: bun frontier show <problem-id> [--json]`;

function verdictLine(v: VerdictResult | null): string {
  return v ? `${v.result} (${v.checker}): ${v.summary}` : 'pending';
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { json: { type: 'boolean' } });
  if (positionals.length !== 1) throw new UsageError('show needs exactly one problem id');
  const id = positionals[0]!;
  const entry = (await loadAll()).find((r) => r.problem.id === id);
  if (!entry) {
    console.error(unknownIdMessage(id, (await loadAll()).map((r) => r.problem.id)));
    return 1;
  }
  const { problem: p, status, attempts } = entry;
  if (values.json) {
    console.log(
      JSON.stringify(
        {
          problem: p,
          status,
          attempts: attempts.map((a) => ({
            id: a.attempt.id,
            kind: a.attempt.kind,
            title: a.attempt.title,
            submitter: a.attempt.submitter.github,
            created: a.attempt.created,
            verdict: a.verdict,
          })),
        },
        null,
        2,
      ),
    );
    return 0;
  }
  const out: string[] = [`${p.title}  [${p.id}]`, `tier: ${p.tier}   field: ${p.field}   status: ${status}`];
  if (p.tags.length) out.push(`tags: ${p.tags.join(', ')}`);
  if (p.tags.includes(PRACTICE_TAG)) {
    out.push('practice: a textbook exercise with a known proof; a checked proof here never counts as an open-problem result');
  }
  if (p.difficulty) out.push(`difficulty: ${p.difficulty.level}. ${p.difficulty.note}`);
  out.push(`source: ${p.source.url} (${p.source.licence})`, '', p.statement.trim(), '');
  if (p.lean) {
    out.push(`Lean module: ${p.lean.module}`, `Lean declaration: ${p.lean.decl}`, '');
    if (p.lean.context.length) {
      out.push('Lean context (the scaffold puts these lines before the theorem):', ...p.lean.context.map((l) => `  ${l}`), '');
    }
    out.push(p.lean.statement.trim(), '');
    if (p.lean.definitions.length) {
      out.push('Definitions the statement uses:');
      for (const d of p.lean.definitions) {
        out.push(`  ${d.kind} ${d.name}  (${d.url})`, ...d.text.split('\n').map((l) => `    ${l}`), '');
      }
    }
  }
  if (p.witness) {
    const b = p.witness.best_known;
    out.push(
      `Witness: verifier ${p.witness.verifier}, ${p.witness.objective} the value`,
      `Params: ${JSON.stringify(p.witness.params)}`,
      `Format: ${p.witness.format}`,
      `Best known: ${b.value} (${b.reference.label}, ${b.reference.url})${b.note ? ` ${b.note}` : ''}`,
      '',
    );
  }
  if (p.references.length) {
    out.push('References:', ...p.references.map((r) => `  ${r.label}: ${r.url}`), '');
  }
  out.push(`Attempts (${attempts.length}):`);
  if (!attempts.length) out.push('  none yet');
  for (const a of attempts) {
    out.push(`  ${a.attempt.id}  ${a.attempt.kind}  ${verdictLine(a.verdict)}`, `    ${a.attempt.title}`);
  }
  console.log(out.join('\n'));
  return 0;
}
