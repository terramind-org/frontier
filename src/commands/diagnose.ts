import { existsSync, statSync } from 'node:fs';
import { readFile, stat } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { parse, UsageError } from '../args.ts';
import { loadVerifier } from '../check/witness.ts';
import { loadProblem, repoRoot } from '../repo.ts';

export const help = `List every violation of a witness, not only the first one.

Usage: bun frontier diagnose <attempt-dir|witness.json> --problem <id> [--json]

Runs the problem's verifier in its collect-everything mode and prints the value the witness has, whether it is valid,
and each violation (the first 200, then a count of the rest). --problem may be left out for an attempt directory: the
problem is then read from its attempt.yaml. The verdict of the real checker is unchanged; this only explains it.
Exit 0 whenever the witness could be read, valid or not.`;

export interface Diagnosis {
  problem: string;
  verifier: string;
  valid: boolean;
  /** The value the witness has; absent when the witness could not be read far enough to count anything. */
  value: number | null;
  objective: 'minimize' | 'maximize';
  best_known: number;
  beats_best_known: boolean;
  ties_best_known: boolean;
  violations: string[];
  /** Violations found beyond the ones listed. */
  omitted: number;
  /** The scan stopped early, so `omitted` is a lower bound. */
  truncated: boolean;
}

const MAX_WITNESS_BYTES = 5_000_000;

/** The witness file and, when the input is an attempt directory, the problem id from its attempt.yaml. */
async function locate(input: string): Promise<{ file: string; attemptProblem?: string }> {
  const abs = resolve(input);
  if (!existsSync(abs)) throw new Error(`${input} does not exist`);
  if (!statSync(abs).isDirectory()) return { file: abs };
  const file = join(abs, 'witness.json');
  if (!existsSync(file)) throw new Error(`${input} has no witness.json`);
  let attemptProblem: string | undefined;
  const yamlFile = join(abs, 'attempt.yaml');
  if (existsSync(yamlFile)) {
    const doc = parseYaml(await readFile(yamlFile, 'utf8')) as { problem?: unknown } | null;
    if (typeof doc?.problem === 'string') attemptProblem = doc.problem;
  }
  return { file, attemptProblem };
}

export async function diagnose(root: string, input: string, problemId: string | undefined): Promise<Diagnosis> {
  const { file, attemptProblem } = await locate(input);
  if (problemId !== undefined && attemptProblem !== undefined && problemId !== attemptProblem) {
    throw new Error(`--problem ${problemId} differs from the problem in attempt.yaml (${attemptProblem})`);
  }
  const id = problemId ?? attemptProblem;
  if (id === undefined) throw new UsageError('diagnose needs --problem <id>');
  const problem = await loadProblem(id, root);
  if (!problem) throw new Error(`no problem with id ${id}`);
  const spec = problem.witness;
  if (!spec) throw new Error(`${id} is not a witness problem; diagnose only explains witness problems`);
  const loaded = await loadVerifier(spec.verifier, id);
  if ('error' in loaded) throw new Error(loaded.error);

  const report = (violations: string[], extra: Partial<Diagnosis> = {}): Diagnosis => ({
    problem: id,
    verifier: spec.verifier,
    valid: false,
    value: null,
    objective: spec.objective,
    best_known: spec.best_known.value,
    beats_best_known: false,
    ties_best_known: false,
    violations,
    omitted: 0,
    truncated: false,
    ...extra,
  });

  if ((await stat(file)).size > MAX_WITNESS_BYTES) return report([`witness.json is larger than ${MAX_WITNESS_BYTES} bytes`]);
  let witness: unknown;
  try {
    witness = JSON.parse(await readFile(file, 'utf8'));
  } catch (e) {
    return report([`witness.json is not valid JSON (${(e as Error).message})`]);
  }

  const outcome = loaded.verify(witness, spec.params, { all: true });
  const violations = outcome.violations ?? (outcome.reason ? [outcome.reason] : []);
  const valid = outcome.valid && violations.length === 0;
  const value = outcome.value ?? null;
  const best = spec.best_known.value;
  const beats = valid && value !== null && (spec.objective === 'maximize' ? value > best : value < best);
  return report(violations, {
    valid,
    value,
    beats_best_known: beats,
    ties_best_known: valid && value === best,
    omitted: outcome.omitted ?? 0,
    truncated: outcome.truncated ?? false,
  });
}

export function formatDiagnosis(d: Diagnosis): string {
  const lines = [`problem:  ${d.problem} (verifier ${d.verifier})`];
  lines.push(`value:    ${d.value === null ? 'not available' : d.value} (best known ${d.best_known}, ${d.objective === 'maximize' ? 'higher' : 'lower'} is better)`);
  lines.push(`valid:    ${d.valid ? 'yes' : 'no'}`);
  if (d.valid) {
    lines.push(d.beats_best_known ? 'result:   beats the best known value' : d.ties_best_known ? 'result:   ties the best known value' : 'result:   does not reach the best known value');
  } else {
    const total = d.violations.length + d.omitted;
    lines.push(`violations (${d.truncated ? 'at least ' : ''}${total}):`);
    d.violations.forEach((v, i) => lines.push(`  ${i + 1}. ${v}`));
    if (d.omitted > 0) lines.push(`  ... and ${d.truncated ? 'at least ' : ''}${d.omitted} more not listed`);
  }
  return lines.join('\n');
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { json: { type: 'boolean' }, problem: { type: 'string' } });
  if (positionals.length !== 1) throw new UsageError('diagnose needs exactly one attempt directory or witness.json');
  const d = await diagnose(repoRoot(), positionals[0]!, values.problem);
  console.log(values.json ? JSON.stringify(d, null, 2) : formatDiagnosis(d));
  return 0;
}
