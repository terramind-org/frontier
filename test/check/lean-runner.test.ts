// The Lean checker's source pre-check (lean/check-attempt.sh --precheck) and the message helpers in
// src/check/proof.ts. Needs bash, perl and grep, not Lean, so it runs in the fast `bun run check`.
import { describe, expect, test } from 'bun:test';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { mapSolutionPath, PROGRESS_LINE, RUNNER } from '../../src/check/proof.ts';

const dir = mkdtempSync(join(tmpdir(), 'frontier-precheck-'));
let n = 0;

/** The pre-check's reason for `src`, or '' when it passes. */
function precheck(src: string): string {
  const file = join(dir, `s${n++}.lean`);
  writeFileSync(file, src);
  const p = Bun.spawnSync(['bash', RUNNER, '--precheck', file], { stdout: 'pipe', stderr: 'pipe' });
  if (p.exitCode !== 0) throw new Error(`precheck failed (exit ${p.exitCode}): ${p.stderr.toString()}`);
  return p.stdout.toString().trim();
}

/** The scaffold `bun frontier new` writes (design: import, context lines, namespace, theorem, sorry). */
const scaffold = (context: string[] = []) =>
  [
    'import FormalConjectures.ErdosProblems.«1»',
    ...context,
    '',
    'namespace OpenProblemsAttempt',
    '',
    '-- Replace the placeholder below with your proof.',
    'theorem solution : ∃ C > (0 : ℝ), ∀ (N : ℕ) (A : Finset ℕ)',
    '    (_ : Erdos1.IsSumDistinctSet A N), N ≠ 0 → C * 2 ^ A.card / A.card < N := by',
    '  sorry',
    '',
    'end OpenProblemsAttempt',
    '',
  ].join('\n');

describe('pre-check passes', () => {
  test('the scaffold', () => {
    expect(precheck(scaffold())).toBe('');
  });

  test('a scaffold with upstream open and notation context lines', () => {
    const context = [
      'open Nat Finset',
      'open scoped Real',
      'local notation "!" n => Nat.factorial n',
      'notation "ℝ²" => EuclideanSpace ℝ (Fin 2)',
      `local notation3 "∑ᶠ' " => (1 : ℕ)`,
      `infixl:65 " +ᵥ' " => HAdd.hAdd`,
      `local infixr:30 " ⊓' " => Min.min`,
      'local prefix:max "√" => Nat.sqrt',
      'postfix:max "⁻¹ᶠ" => id',
      'scoped[Foo] notation "𝟙" => (1 : ℕ)',
    ];
    expect(precheck(scaffold(context))).toBe('');
  });

  test('comments that mention banned words', () => {
    const src = [
      'import Mathlib',
      '-- Old scaffold: `sorry`, `native_decide` and new `axiom`s are rejected; no #eval, macro or syntax.',
      '/- A block comment /- nested, with run_cmd -/ still a comment: unsafe, initialize, elab -/',
      'theorem t : True := trivial -- the meta-argument and @[implemented_by] in a trailing comment',
      '/-',
      '  set_option debug.skipKernelTC true',
      '-/',
    ].join('\n');
    expect(precheck(src)).toBe('');
  });

  test('a comment marker inside a string or char literal does not hide anything, and a comment after one is still ignored', () => {
    expect(precheck('import Mathlib\ndef c : Char := \'"\'\ndef s := "x" -- axiom in a comment\n')).toBe('');
  });

  test('an import commented out, and a trailing comment on an import line', () => {
    expect(precheck('import Mathlib -- everything\n/- import Evil.Module -/\n-- import Lean\n')).toBe('');
  });
});

describe('pre-check rejects, naming the token and the line', () => {
  const cases: [string, string, RegExp][] = [
    ['an axiom declaration', 'import Mathlib\n\naxiom cheat : False\n', /^source uses an axiom declaration: `axiom` on line 3 \(comments are ignored\)/],
    ['an axiom right after a block comment', 'import Mathlib\n/- c -/axiom cheat : False\n', /`axiom` on line 2/],
    ['an axiom after a multi-line block comment', 'import Mathlib\n/- a\nb\n-/ axiom cheat : False\n', /`axiom` on line 4/],
    ['#eval', 'import Mathlib.Tactic\n#eval 1\n', /^source uses #eval: `#eval` on line 2 \(comments are ignored\)/],
    ['run_cmd', 'import Mathlib\nrun_cmd pure ()\n', /source uses run_cmd: `run_cmd` on line 2/],
    ['macro', 'import Mathlib\nmacro "x" : term => `(1)\n', /source uses macro: `macro` on line 2/],
    ['macro_rules', 'import Mathlib\nmacro_rules | `(x) => `(1)\n', /source uses macro: `macro_rules` on line 2/],
    ['syntax', 'import Mathlib\nsyntax "x" : term\n', /source uses syntax: `syntax` on line 2/],
    ['elab', 'import Mathlib\nelab "x" : term => pure (Lean.mkNatLit 1)\n', /source uses elab: `elab` on line 2/],
    ['initialize', 'import Mathlib\ninitialize pure ()\n', /source uses initialize: `initialize` on line 2/],
    ['implemented_by', 'import Mathlib.Tactic\n@[implemented_by id] def f (n : Nat) : Nat := n\n', /source uses @\[implemented_by\]: `implemented_by` on line 2/],
    ['extern', 'import Mathlib\n@[extern "f"] def f (n : Nat) : Nat := n\n', /source uses @\[extern\]: `extern` on line 2/],
    ['unsafe', 'import Mathlib\nunsafe def f : Nat := 1\n', /source uses unsafe code: `unsafe` on line 2/],
    ['debug.skipKernelTC', 'import Mathlib.Tactic\nset_option debug.skipKernelTC true\n', /source uses set_option debug\.skipKernelTC: `skipKernelTC` on line 2/],
    ['an elaborator attribute', 'import Mathlib.Tactic\n@[tactic Lean.Parser.Tactic.done] def t : Nat := 0\n', /attribute that registers compile-time code: `@\[tactic` on line 2/],
    ['a Lean meta import', 'import Lean\nimport Mathlib.Tactic\n', /imports Lean, which is not on the allow-list/],
    ['an import outside the allow-list', 'import Evil.Module\n', /imports Evil\.Module, which is not on the allow-list/],
    ['an import after a comment on the same line', 'import Mathlib\n/- x -/ import Evil.Module\n', /imports Evil\.Module/],
    ['#eval after a string that contains --', 'import Mathlib\ndef s := "-- not a comment"\n#eval 1\n', /#eval: `#eval` on line 3/],
    ['#eval after a «name» that contains --', 'import Mathlib\ndef x := «a -- b» #eval 1\n', /#eval: `#eval` on line 2/],
    ['#eval in a doc comment (Lean may elaborate docstrings)', 'import Mathlib\n/-- doc with #eval 1 -/\ntheorem t : True := trivial\n', /#eval: `#eval` on line 2/],
  ];
  for (const [name, src, reason] of cases) {
    test(name, () => {
      expect(precheck(src)).toMatch(reason);
    });
  }

  test('a notation token containing -- makes comments count: nothing hides after it', () => {
    const src = 'import Mathlib\nnotation "x <-- " y => y\ntheorem t : True := x <-- (by run_tac pure ()) -- trivial\n';
    const reason = precheck(src);
    expect(reason).toMatch(/run_tac: `run_tac` on line 3/);
    expect(reason).toContain('comments were scanned too');
  });

  test('a char literal after a symbol is not guessed at: comments count', () => {
    const src = "import Mathlib\ndef f := ∘'/'-1 #eval 1 -/\n";
    expect(precheck(src)).toMatch(/#eval: `#eval` on line 2 \(comments were scanned too/);
  });
});

describe('verdict messages', () => {
  test('Attempt/Solution.lean is mapped back to the attempt’s own path', () => {
    const reason = 'does not compile: error: Attempt/Solution.lean:14:14: unknown identifier';
    const v = mapSolutionPath(
      {
        checker: 'lean',
        result: 'rejected',
        summary: `rejected: ${reason}`,
        lean: { toolchain: 't', fc_commit: 'c', target: 'statement', axioms: [], reason },
      },
      'attempts/p/a/solution.lean',
    );
    expect(v.summary).toBe('rejected: does not compile: error: attempts/p/a/solution.lean:14:14: unknown identifier');
    expect(v.lean?.reason).toBe('does not compile: error: attempts/p/a/solution.lean:14:14: unknown identifier');
  });

  test('the progress pattern matches the runner’s three lines and nothing else', () => {
    for (const l of ['[1/3] building attempt…', '[2/3] kernel replay and statement check…', '[3/3] integrity check…']) {
      expect(PROGRESS_LINE.test(l)).toBe(true);
    }
    expect(PROGRESS_LINE.test('check-attempt: WARNING: files changed')).toBe(false);
  });
});
