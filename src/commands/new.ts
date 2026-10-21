import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { parse, UsageError } from '../args.ts';
import { newAttemptId } from '../ids.ts';
import { proofStart } from '../import/lean-parse.ts';
import { loadProblem, loadProblems, repoRoot, unknownIdMessage, writeYaml } from '../repo.ts';
import { Attempt, attemptIssues, KIND_FILE, PLACEHOLDER_CLAIM, PROSE_NOTE } from '../schema.ts';
import type { Problem } from '../schema.ts';

export const help = `Scaffold an attempt directory for a problem.

Usage: bun frontier new <problem-id> --kind proof|disproof|witness|writeup --login <github-login>
                        [--model name:provider:role]... [--tool name:role]... [--lean-file name.lean]...
                        [--mode ai_only|human_ai|human_only]

  --model       repeatable; the AI model(s) used, e.g. --model "claude-fable-5-1:anthropic:author"
  --tool        repeatable; a non-AI tool used, e.g. --tool "cp-sat:search", recorded in models with provider "tool"
  --lean-file   repeatable, writeups only: an extra .lean file (listed, shown, never compiled for a verdict)
  --mode        default ai_only when an AI model is given, else human_only
The scaffold's declarations are false until your human has seen them and you set them.
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
  // Drop a trailing proof (`:= …`), skipping the `:=` of `let`/`letI`/`have`/… binders in the type.
  const proof = proofStart(type);
  if (proof !== null) type = type.slice(0, proof);
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
  const context = problem.lean.context.length ? `${problem.lean.context.join('\n')}\n\n` : '';
  // The comment avoids every word the checker's source pre-check looks for.
  const what = kind === 'proof' ? 'proof' : 'proof of the negation';
  return `import ${problem.lean.module}

${context}namespace OpenProblemsAttempt

-- Replace the placeholder below with your ${what}.
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
  /** AI models (provider as given) and tools (provider "tool"), all recorded in `models`. */
  models?: Attempt['models'];
  /** Extra `.lean` files for a writeup (created with an `import` line, listed in `files`, never compiled for a verdict). */
  leanFiles?: string[];
  mode?: Attempt['mode'];
  date?: Date;
}

const KIND_TITLE: Record<Attempt['kind'], string> = { proof: 'Proof', disproof: 'Disproof', witness: 'Witness', writeup: 'Writeup' };

/** What `new` writes: an Attempt whose declarations are still false (the schema only accepts true). */
export type ScaffoldedAttempt = Omit<Attempt, 'declarations'> & { declarations: { rights: boolean; disclosure_complete: boolean } };

export async function scaffoldAttempt(o: ScaffoldOptions): Promise<{ dir: string; files: string[]; attempt: ScaffoldedAttempt }> {
  const date = o.date ?? new Date();
  const models = o.models ?? [];
  const leanFiles = o.leanFiles ?? [];
  if (leanFiles.length && o.kind !== 'writeup') throw new UsageError('--lean-file is only for --kind writeup');
  for (const f of leanFiles) {
    if (!/^[A-Za-z0-9_][A-Za-z0-9_.-]*\.lean$/.test(f) || f === KIND_FILE[o.kind]) {
      throw new UsageError(`--lean-file must be a plain file name ending in .lean, got "${f}"`);
    }
  }
  const attempt: ScaffoldedAttempt = {
    schema: 1,
    id: newAttemptId(o.login, date),
    problem: o.problem.id,
    kind: o.kind,
    title: `${KIND_TITLE[o.kind]} attempt on ${o.problem.title}`,
    claim: PLACEHOLDER_CLAIM,
    files: [KIND_FILE[o.kind], ...leanFiles],
    submitter: { github: o.login },
    people: [{ name: o.login, github: o.login, role: 'submitter' }],
    models,
    mode: o.mode ?? (models.some((m) => m.provider !== TOOL_PROVIDER) ? 'ai_only' : 'human_only'),
    created: date.toISOString().slice(0, 10),
    licence: 'CC-BY-4.0',
    // Unconfirmed on purpose: validate, check and submit fail until the human has seen and set them.
    declarations: { rights: false, disclosure_complete: false },
  };
  const asIfConfirmed = Attempt.parse({ ...attempt, declarations: { rights: true, disclosure_complete: true } });
  const issues = attemptIssues(asIfConfirmed, o.problem, { scaffold: true });
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
  const stub = o.problem.lean ? `import ${o.problem.lean.module}\n\n` : '';
  for (const f of leanFiles) await writeFile(join(dir, f), stub);
  return { dir, files: ['attempt.yaml', file, ...leanFiles], attempt };
}

/** Provider recorded for `--tool` entries. */
export const TOOL_PROVIDER = 'tool';

function parseModel(spec: string): Attempt['models'][number] {
  const parts = spec.split(':');
  if (parts.length !== 3 || parts.some((p) => p.trim() === '')) {
    throw new UsageError(`--model must look like "name:provider:role", got "${spec}"`);
  }
  return { name: parts[0]!.trim(), provider: parts[1]!.trim(), role: parts[2]!.trim() };
}

function parseTool(spec: string): Attempt['models'][number] {
  const parts = spec.split(':');
  if (parts.length !== 2 || parts.some((p) => p.trim() === '')) {
    throw new UsageError(`--tool must look like "name:role", got "${spec}"`);
  }
  return { name: parts[0]!.trim(), provider: TOOL_PROVIDER, role: parts[1]!.trim() };
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, {
    kind: { type: 'string' },
    login: { type: 'string' },
    model: { type: 'string', multiple: true },
    tool: { type: 'string', multiple: true },
    'lean-file': { type: 'string', multiple: true },
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
    console.error(unknownIdMessage(positionals[0]!, (await loadProblems(root)).map((p) => p.id)));
    return 1;
  }
  if (problem.tier === 'prose' && kind.data !== 'writeup') {
    throw new UsageError(`${problem.id} is a prose problem: only --kind writeup is accepted, and it is never machine-checked.`);
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
    models: [...(values.model ?? []).map(parseModel), ...(values.tool ?? []).map(parseTool)],
    leanFiles: values['lean-file'],
    mode: mode?.data,
  });
  if (values.json) console.log(JSON.stringify({ dir, files }, null, 2));
  else {
    console.log(dir);
    console.log(`Edit ${files.slice(1).join(', ')} and the claim in attempt.yaml, then run: bun frontier check ${dir}`);
    if (problem.tier === 'prose') console.log(PROSE_NOTE);
    console.log(
      'attempt.yaml declarations are false on purpose: before submitting, show them to your human and set them to true only after they agree.',
    );
  }
  return 0;
}
