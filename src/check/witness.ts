/**
 * Tier checker for `witness` problems: reads witness.json from the attempt directory, runs the problem's verifier
 * (src/check/witness/<verifier>.ts) and compares the value with the best known one.
 */
import { existsSync } from 'node:fs';
import { readFile, stat } from 'node:fs/promises';
import { join } from 'node:path';
import type { Attempt, Problem, VerdictResult } from '../schema.ts';
import type { Params, VerifyOptions, VerifyResult } from './witness/common.ts';

export interface CheckInput {
  repoRoot: string;
  problem: Problem;
  attempt: Attempt;
  attemptDir: string;
}

const MAX_WITNESS_BYTES = 5_000_000;

export type VerifyFn = (witness: unknown, params: Params, opts?: VerifyOptions) => VerifyResult;

function rejected(problem: Problem, reason: string): VerdictResult {
  const best = problem.witness!.best_known.value;
  return {
    checker: 'witness',
    result: 'rejected',
    summary: `Invalid: ${reason}`,
    witness: { valid: false, best_known: best, beats_best_known: false, ties_best_known: false, reason },
  };
}

/** Load `src/check/witness/<name>.ts`'s `verify`, or say why not. */
export async function loadVerifier(name: string, problemId: string): Promise<{ verify: VerifyFn } | { error: string }> {
  if (!/^[a-z0-9-]+$/.test(name)) return { error: `invalid verifier name "${name}"` };
  const verifierFile = join(import.meta.dir, 'witness', `${name}.ts`);
  if (!existsSync(verifierFile)) return { error: `no verifier "${name}" for problem ${problemId}` };
  const mod = (await import(verifierFile)) as { verify?: VerifyFn };
  if (typeof mod.verify !== 'function') return { error: `verifier "${name}" exports no verify function` };
  return { verify: mod.verify };
}

export async function check(input: CheckInput): Promise<VerdictResult> {
  const { problem, attemptDir } = input;
  const spec = problem.witness;
  if (!spec) return { checker: 'witness', result: 'error', summary: `problem ${problem.id} has no witness block` };

  const file = join(attemptDir, 'witness.json');
  if (!existsSync(file)) return rejected(problem, 'witness.json is missing');
  if ((await stat(file)).size > MAX_WITNESS_BYTES) {
    return rejected(problem, `witness.json is larger than ${MAX_WITNESS_BYTES} bytes`);
  }
  let witness: unknown;
  try {
    witness = JSON.parse(await readFile(file, 'utf8'));
  } catch (e) {
    return rejected(problem, `witness.json is not valid JSON (${(e as Error).message})`);
  }

  const loaded = await loadVerifier(spec.verifier, problem.id);
  if ('error' in loaded) return { checker: 'witness', result: 'error', summary: loaded.error };

  let outcome: VerifyResult;
  try {
    outcome = loaded.verify(witness, spec.params);
  } catch (e) {
    return { checker: 'witness', result: 'error', summary: `verifier "${spec.verifier}" failed: ${(e as Error).message}` };
  }
  if (!outcome.valid || outcome.value === undefined) {
    return rejected(problem, outcome.reason ?? 'the verifier rejected the witness');
  }

  const best = spec.best_known.value;
  const value = outcome.value;
  const beats = spec.objective === 'maximize' ? value > best : value < best;
  const ties = value === best;
  const verdict = beats
    ? `beats the best known (${best}, ${spec.best_known.reference.label})`
    : ties
      ? `ties the best known (${spec.best_known.reference.label})`
      : `does not reach the best known ${best} (${spec.best_known.reference.label})`;
  return {
    checker: 'witness',
    result: 'verified',
    summary: `Valid witness for ${problem.id} with value ${value}; ${verdict}.`,
    witness: { valid: true, value, best_known: best, beats_best_known: beats, ties_best_known: ties },
  };
}
