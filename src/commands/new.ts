import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { parse, UsageError } from '../args.ts';
import { newAttemptId } from '../ids.ts';
import { loadProblem, repoRoot, writeYaml } from '../repo.ts';
import { Attempt, attemptIssues, KIND_FILE } from '../schema.ts';
import type { Problem } from '../schema.ts';

export const help = `Scaffold an attempt directory for a problem.

Usage: bun frontier new <problem-id> --kind proof|disproof|witness|writeup --login <github-login>
                        [--model name:provider:role]... [--mode ai_only|human_ai|human_only]

  --model   repeatable; the AI model(s) used, e.g. --model "claude-fable-5-1:anthropic:author"
  --mode    default ai_only when models are given, else human_only
Prints the new directory. Add --json for {dir, files}.`;

const OPEN: Record<string, string> = { '(': ')', '[': ']', '{': '}', '⦃': '⦄', '⟨': '⟩' };
const CLOSE = new Set(Object.values(OPEN));

/** Split the text after a declaration name into its binders and its type (first depth-0 `:`). */
function splitBindersAndType(rest: string): { binders: string; type: string } {
  let depth = 0;
  let colon = -1;
  for (let i = 0; i < rest.length; i++) {
    const c = rest[i]!;
    if (c in OPEN) depth++;
    else if (CLOSE.has(c)) depth--;
    else if (c === ':' && depth === 0 && rest[i + 1] !== '=') {
      colon = i;
      break;
    }
  }
  if (colon < 0) throw new Error('could not find the type (a top-level ":") in the Lean statement');
  let type = rest.slice(colon + 1);
  depth = 0;
  for (let i = 0; i < type.length; i++) {
    const c = type[i]!;
    if (c in OPEN) depth++;
    else if (CLOSE.has(c)) depth--;
    else if (c === ':' && type[i + 1] === '=' && depth === 0) {
      type = type.slice(0, i);
      break;
    }
  }
  return { binders: rest.slice(0, colon).trim(), type: type.trim() };
}

/**
 * The declaration header of solution.lean: the problem's statement with its name replaced by `solution`.
 * For a disproof the type becomes `¬ (type)`; binders move inside as `∀ binders, type` so the negation
 * covers the whole statement.
 */
export function solutionDeclaration(statement: string, disproof: boolean): string {
  const m = /(?:^|\s)(theorem|lemma)\s+[^\s(){}\[\]⦃⦄:]+/.exec(statement);
  if (!m) throw new Error('lean.statement has no `theorem`/`lemma` declaration');
  const rest = statement.slice(m.index + m[0].length);
  const { binders, type } = splitBindersAndType(rest);
  if (!disproof) {
    return `theorem solution${binders ? ` ${binders}` : ''} : ${type}`;
  }
  return `theorem solution : ¬ (${binders ? `∀ ${binders}, ` : ''}${type})`;
}

export function leanTemplate(problem: Problem, kind: 'proof' | 'disproof'): string {
  if (!problem.lean) throw new Error(`problem ${problem.id} has no lean block`);
  const decl = solutionDeclaration(problem.lean.statement, kind === 'disproof');
  const goal = kind === 'proof' ? 'a proof of' : 'a disproof of (a proof of the negation of)';
  return `import ${problem.lean.module}

/-
  ${problem.title}: ${goal} \`${problem.lean.decl}\`.
  Replace \`sorry\` with your proof. The statement above \`:= by\` must not change; the checker
  compares it with the problem's statement. \`sorry\`, \`native_decide\` and new \`axiom\`s are rejected.
-/

namespace OpenProblemsAttempt

${decl} := by
  sorry

end OpenProblemsAttempt
`;
}

export interface ScaffoldOptions {
  root: string;
  problem: Problem;
  kind: Attempt['kind'];
  login: string;
  models?: Attempt['models'];
  mode?: Attempt['mode'];
  date?: Date;
}

const KIND_TITLE: Record<Attempt['kind'], string> = { proof: 'Proof', disproof: 'Disproof', witness: 'Witness', writeup: 'Writeup' };

export async function scaffoldAttempt(o: ScaffoldOptions): Promise<{ dir: string; files: string[]; attempt: Attempt }> {
  const date = o.date ?? new Date();
  const models = o.models ?? [];
  const attempt: Attempt = {
    schema: 1,
    id: newAttemptId(o.login, date),
    problem: o.problem.id,
    kind: o.kind,
    title: `${KIND_TITLE[o.kind]} attempt on ${o.problem.title}`,
    claim: 'Describe exactly what this attempt claims.',
    files: [KIND_FILE[o.kind]],
    submitter: { github: o.login },
    people: [{ name: o.login, github: o.login, role: 'submitter' }],
    models,
    mode: o.mode ?? (models.length ? 'ai_only' : 'human_only'),
    created: date.toISOString().slice(0, 10),
    licence: 'CC-BY-4.0',
    declarations: { rights: true, disclosure_complete: true },
  };
  Attempt.parse(attempt);
  const issues = attemptIssues(attempt, o.problem);
  if (issues.length) throw new UsageError(issues.join('; '));

  const dir = join(o.root, 'attempts', o.problem.id, attempt.id);
  if (existsSync(dir)) throw new Error(`${dir} already exists`);
  await mkdir(dir, { recursive: true });
  await writeYaml(join(dir, 'attempt.yaml'), attempt);
  const file = KIND_FILE[o.kind];
  const body =
    o.kind === 'proof' || o.kind === 'disproof'
      ? leanTemplate(o.problem, o.kind)
      : o.kind === 'witness'
        ? '{}\n'
        : `# ${attempt.title}\n\n`;
  await writeFile(join(dir, file), body);
  return { dir, files: ['attempt.yaml', file], attempt };
}

function parseModel(spec: string): Attempt['models'][number] {
  const parts = spec.split(':');
  if (parts.length !== 3 || parts.some((p) => p.trim() === '')) {
    throw new UsageError(`--model must look like "name:provider:role", got "${spec}"`);
  }
  return { name: parts[0]!.trim(), provider: parts[1]!.trim(), role: parts[2]!.trim() };
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, {
    kind: { type: 'string' },
    login: { type: 'string' },
    model: { type: 'string', multiple: true },
    mode: { type: 'string' },
    json: { type: 'boolean' },
  });
  if (positionals.length !== 1) throw new UsageError('new needs exactly one problem id');
  if (!values.login) throw new UsageError('--login <github-login> is required');
  const kind = Attempt.shape.kind.safeParse(values.kind);
  if (!kind.success) throw new UsageError('--kind must be one of proof, disproof, witness, writeup');
  const mode = values.mode === undefined ? undefined : Attempt.shape.mode.safeParse(values.mode);
  if (mode && !mode.success) throw new UsageError('--mode must be one of ai_only, human_ai, human_only');

  const root = repoRoot();
  const problem = await loadProblem(positionals[0]!, root);
  if (!problem) {
    console.error(`No problem "${positionals[0]}". Try \`bun frontier list\`.`);
    return 1;
  }
  if ((kind.data === 'proof' || kind.data === 'disproof') && problem.tags.includes('answer-required')) {
    throw new UsageError(
      `${problem.id} is tagged answer-required: upstream leaves the answer as sorry, so a Lean ${kind.data} cannot be checked. Use --kind writeup.`,
    );
  }
  const { dir, files } = await scaffoldAttempt({
    root,
    problem,
    kind: kind.data,
    login: values.login,
    models: (values.model ?? []).map(parseModel),
    mode: mode?.data,
  });
  if (values.json) console.log(JSON.stringify({ dir, files }, null, 2));
  else {
    console.log(dir);
    console.log(`Edit ${files.slice(1).join(', ')} and the claim in attempt.yaml, then run: bun frontier check ${dir}`);
  }
  return 0;
}
