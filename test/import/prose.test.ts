import { describe, expect, test } from 'bun:test';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  catalogueKeyFromCode,
  catalogueKeyFromFcPath,
  collectReferences,
  formalConjecturesKeys,
  titleAndStatementMatch,
  wordSet,
} from '../../src/import/prose.ts';
import { importUnsolvedMath, readUnsolvedMath, rowLicence } from '../../src/import/unsolvedmath.ts';
import { compareHandles, importWeSolve, openStatus, statementBody, WeSolveRecord } from '../../src/import/we-solve.ts';
import { main } from '../../src/cli.ts';
import { loadProblems } from '../../src/repo.ts';
import { problemIssues } from '../../src/schema.ts';

// Real records, copied unchanged: 18 we-solve records (problem.yaml + statement.tex) with their handles,
// 19 UnsolvedMath rows, and four formal-conjectures problems for the dedupe against Frontier.
const FIX = join(import.meta.dir, '..', 'fixtures', 'import');
const REV = 'd371ee917ac9647fbb06cd6fc529deec6f3dda82';
const DATE = '2026-10-21';

function git(cwd: string, ...args: string[]): void {
  // Fixed dates, so every workspace's fixture commit has the same id.
  const env = { ...process.env, GIT_AUTHOR_DATE: '2026-10-20T00:00:00Z', GIT_COMMITTER_DATE: '2026-10-20T00:00:00Z' };
  const p = Bun.spawnSync(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.org', ...args], { cwd, env });
  if (p.exitCode !== 0) throw new Error(`git ${args.join(' ')}: ${p.stderr.toString()}`);
}

/** A git clone of the we-solve fixture, the UnsolvedMath fixture directory, and a repo root holding the FC problems. */
function workspace(): { checkout: string; um: string; root: string } {
  const base = mkdtempSync(join(tmpdir(), 'frontier-prose-'));
  const checkout = join(base, 'we-solve');
  cpSync(join(FIX, 'we-solve'), checkout, { recursive: true });
  git(checkout, 'init', '-q');
  git(checkout, 'add', '-A');
  git(checkout, 'commit', '-q', '-m', 'fixture');
  const root = join(base, 'repo');
  mkdirSync(join(root, 'problems'), { recursive: true });
  cpSync(join(FIX, 'prose-root'), join(root, 'problems'), { recursive: true });
  return { checkout, um: join(FIX, 'unsolvedmath'), root };
}

function snapshot(root: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const n of readdirSync(join(root, 'problems')).sort()) out[n] = readFileSync(join(root, 'problems', n), 'utf8');
  for (const n of readdirSync(join(root, 'sources')).sort()) out[`sources/${n}`] = readFileSync(join(root, 'sources', n), 'utf8');
  return out;
}

const steps = (s: { steps: { rule: string; before: number; after: number; reasons: Record<string, number> }[] }) =>
  s.steps.map((x) => [x.rule, x.before, x.after, x.reasons]);

describe('import we-solve and unsolvedmath', async () => {
  const { checkout, um, root } = workspace();
  const data = await readUnsolvedMath(um, REV);
  const ws = await importWeSolve({ checkout, root, date: DATE, unsolvedmath: data });
  const us = await importUnsolvedMath({ dir: um, root, date: DATE, revision: REV });
  const problems = await loadProblems(root);
  const byId = new Map(problems.map((p) => [p.id, p]));

  test('we-solve: counts before and after every rule', () => {
    expect(ws.records).toBe(18);
    expect(steps(ws)).toEqual([
      ['rights: redistribution permitted under CC BY 4.0 or CC BY-SA 4.0', 18, 18, {}],
      ['status open, partially_solved, or uncertified catalogue', 18, 17, { 'status proved': 1 }],
      ['flagged duplicate or unrecoverable (c)', 17, 15, { 'statement marked unrecoverable': 1, 'title starts "Duplicate"': 1 }],
      ['UnsolvedMath archived the row (b/c)', 15, 14, { 'archived upstream as a duplicate or merged record': 1 }],
      ['UnsolvedMath now lists it as solved (b)', 14, 13, { 'we-solve open, UnsolvedMath solved': 1 }],
      ['same problem recorded twice (c)', 13, 10, { 'duplicate of ERDOS record': 2, 'duplicate of TOP record': 1 }],
      ['formal-conjectures has it (a)', 10, 9, { 'erdosproblems number matches a formal-conjectures problem': 1 }],
    ]);
    expect(ws.imported).toBe(9);
    expect(ws.byTag['open-status-unverified']).toBe(2);
  });

  test('unsolvedmath: counts before and after every rule', () => {
    expect(us.rows).toBe(19);
    expect(steps(us)).toEqual([
      ['published only (c: archived duplicates and non-problems)', 19, 17, { 'archived upstream as a duplicate or merged record': 2 }],
      ['status open or partially_solved', 17, 15, { 'status solved': 2 }],
      ['empty statement', 15, 15, {}],
      ['same title and statement as an earlier row (c)', 15, 15, {}],
      ['formal-conjectures has it (a)', 15, 12, {
        'erdosproblems number matches a formal-conjectures problem': 1,
        'kourovka number matches a formal-conjectures problem': 1,
        'millennium number matches a formal-conjectures problem': 1,
      }],
      ['we-solve has it (b)', 12, 5, { 'a we-solve problem lists this UnsolvedMath id': 7 }],
    ]);
    // Two sibling questions share the title of TOP-1500012 but are different problems: kept.
    expect(us.titleOnlyKept).toBe(2);
    expect(problems.filter((p) => p.source.name === 'unsolvedmath').map((p) => p.id).sort()).toEqual(
      ['um.1500013', 'um.1500014', 'um.20003237', 'um.30000173', 'um.800454'],
    );
  });

  test('every imported problem is a valid prose problem with no lean, witness or difficulty', () => {
    for (const p of problems.filter((x) => x.tier === 'prose')) {
      expect(problemIssues(p)).toEqual([]);
      expect(p.lean).toBeUndefined();
      expect(p.witness).toBeUndefined();
      expect(p.difficulty).toBeUndefined();
      expect(p.ams).toEqual([]);
      expect(p.added).toBe(DATE);
    }
  });

  test('a we-solve problem: id, statement without the preamble, source, licence, both sources referenced', () => {
    const p = byId.get('ws.top-2965')!;
    expect(p.title).toBe('Kirby Problem 4.89');
    expect(p.field).toBe('mathematics');
    expect(p.upstream_status).toBe('open');
    expect(p.tags).toEqual(['we-solve', 'top-open-problems']);
    expect(p.statement).toStartWith('\\section*{Kirby Problem 4.89}');
    expect(p.statement).not.toContain('\\documentclass');
    expect(p.statement).toContain('$a(uv,x)=a(u,a(v,x))$');
    expect(p.source.name).toBe('we-solve');
    expect(p.source.repo).toBe('https://github.com/We-Solve/research');
    expect(p.source.commit).toBe(ws.commit);
    expect(p.source.path).toBe('problems/00/prb_0007fc1635b9497fbfd2a64523550ac0/statement.tex');
    expect(p.source.url).toBe(`https://github.com/We-Solve/research/tree/${ws.commit}/problems/00/prb_0007fc1635b9497fbfd2a64523550ac0`);
    expect(p.source.licence).toBe('CC-BY-4.0');
    expect(p.references.slice(0, 2)).toEqual([
      { label: 'we-solve TOP-2965', url: p.source.url },
      { label: 'UnsolvedMath KP-4.89', url: 'https://www.unsolvedmath.com/problems/KP-4.89' },
    ]);
    expect(p.references.map((r) => r.url)).toContain('https://math.berkeley.edu/sites/default/files/surv-295-ruberman-watermarked-author-pdf.pdf');
    expect(p.external_ids).toEqual([
      'we-solve:prb_0007fc1635b9497fbfd2a64523550ac0',
      'top-open-problems:2965',
      'unsolvedmath-code:KP-4.89',
      'unsolvedmath:2965',
    ]);
  });

  test('partially solved, share-alike, physics, and the two uncertified catalogues', () => {
    expect(byId.get('ws.top-9400090')!.upstream_status).toBe('partially-solved');
    expect(byId.get('ws.top-9400090')!.tags).toContain('partially-solved');
    expect(byId.get('ws.top-30000030')!.source.licence).toBe('CC-BY-SA-4.0');
    expect(byId.get('ws.top-8200004')!.field).toBe('physics');
    const bio = byId.get('ws.biocat-107')!;
    expect([bio.field, bio.upstream_status, bio.tags]).toEqual(['biology', 'open', ['we-solve', 'biology-catalogue', 'open-status-unverified']]);
    const econ = byId.get('ws.econ-1')!;
    expect([econ.field, econ.tags]).toEqual(['economics', ['we-solve', 'economics-catalogue', 'open-status-unverified']]);
  });

  test('duplicates keep the canonical record, which inherits the other ids', () => {
    // ERDOS-111 (erdosproblems.com) beats TOP-1935 (UnsolvedMath EP-111); the related Pisot pair keeps TOP-4600053.
    expect(byId.has('ws.top-1935')).toBe(false);
    expect(byId.get('ws.erdos-111')!.external_ids).toContain('unsolvedmath:1935');
    expect(byId.get('ws.erdos-111')!.external_ids).toContain('we-solve:prb_' + readFileSync(join(checkout, 'browse', 'aliases.json'), 'utf8').match(/"TOP-1935": \{\s*"id": "prb_([0-9a-f]+)"/)![1]);
    expect(byId.has('ws.top-30006953')).toBe(false);
    expect(byId.has('ws.top-4600053')).toBe(true);
    // Erdős 101 is formalised in formal-conjectures: neither source imports it.
    expect([...byId.keys()].filter((id) => id === 'ws.erdos-101' || id === 'ws.top-1930' || id === 'um.1930')).toEqual([]);
  });

  test('an UnsolvedMath problem: id, statement as given, licence per row, page and links as references', () => {
    const p = byId.get('um.30000173')!;
    const row = data.rows.find((r) => r.id === 30000173)!;
    expect(p.statement).toBe(row.statement.trim());
    expect(p.source).toEqual({
      name: 'unsolvedmath',
      repo: 'https://huggingface.co/datasets/ulamai/UnsolvedMath',
      commit: REV,
      path: 'problems.json',
      url: `https://huggingface.co/datasets/ulamai/UnsolvedMath/blob/${REV}/problems.json`,
      licence: 'CC-BY-SA-4.0',
    });
    expect(p.references[0]).toEqual({ label: `UnsolvedMath ${row.problem_number}`, url: `https://www.unsolvedmath.com/problems/${row.problem_number}` });
    expect(p.tags).toEqual(['unsolvedmath', 'oberwolfach-reports-open-problems']);
    expect(byId.get('um.20003237')!.tags).toContain('partially-solved');
    expect(byId.get('um.20003237')!.source.licence).toBe('CC-BY-4.0');
    expect(byId.get('um.800454')!.field).toBe('computer-science');
  });

  test('sources/*.json pin the commit and the revision', () => {
    const w = JSON.parse(readFileSync(join(root, 'sources', 'we-solve.json'), 'utf8'));
    expect(w).toEqual({ repo: 'https://github.com/We-Solve/research', commit: ws.commit, licence: w.licence, imported_at: DATE });
    const u = JSON.parse(readFileSync(join(root, 'sources', 'unsolvedmath.json'), 'utf8'));
    expect(u.commit).toBe(REV);
    expect(u.licence).toContain('CC-BY-SA-4.0');
  });

  test('reruns are byte-identical, keep added dates, and leave the other source and formal-conjectures alone', async () => {
    const before = snapshot(root);
    await importWeSolve({ checkout, root, date: '2031-01-01', unsolvedmath: data });
    await importUnsolvedMath({ dir: um, root, date: '2031-01-01', revision: REV });
    expect(snapshot(root)).toEqual(before);
    expect(existsSync(join(root, 'problems', 'erdos101.erdos-101.yaml'))).toBe(true);
  });

  test('stale problems of the source are removed; dry runs write nothing', async () => {
    const { checkout: c, um: u, root: r } = workspace();
    await importUnsolvedMath({ dir: u, root: r, date: DATE, revision: REV });
    // Without we-solve problems in the repo, the rows we-solve covers are imported from UnsolvedMath.
    expect((await loadProblems(r)).filter((p) => p.source.name === 'unsolvedmath')).toHaveLength(12);
    const dry = await importWeSolve({ checkout: c, root: r, date: DATE, unsolvedmath: data, dryRun: true });
    expect(dry.imported).toBe(9);
    expect(existsSync(join(r, 'sources', 'we-solve.json'))).toBe(false);
    await importWeSolve({ checkout: c, root: r, date: DATE, unsolvedmath: data });
    const again = await importUnsolvedMath({ dir: u, root: r, date: DATE, revision: REV });
    expect(again.removed).toEqual(['um.1500012', 'um.2965', 'um.30000030', 'um.4600053', 'um.8200004', 'um.9400090', 'um.1935'].sort());
    expect(snapshot(r)).toEqual(snapshot(root));
  });

  test('without UnsolvedMath data the cross-source rules are skipped', async () => {
    const { checkout: c, root: r } = workspace();
    const s = await importWeSolve({ checkout: c, root: r, date: DATE, dryRun: true });
    expect(s.steps.map((x) => x.rule)).not.toContain('UnsolvedMath archived the row (b/c)');
    expect(s.imported).toBe(11);
  });
});

describe('bun frontier import we-solve | unsolvedmath', () => {
  async function cli(cwd: string, ...argv: string[]): Promise<{ code: number; out: string }> {
    const out: string[] = [];
    const [log, err, prev] = [console.log, console.error, process.cwd()];
    console.log = (...a) => void out.push(a.join(' '));
    console.error = (...a) => void out.push(a.join(' '));
    process.chdir(cwd);
    try {
      return { code: await main(argv), out: out.join('\n') };
    } finally {
      process.chdir(prev);
      console.log = log;
      console.error = err;
    }
  }

  test('prints the rule ledger and writes both sources', async () => {
    const { checkout, um, root } = workspace();
    writeFileSync(join(root, 'package.json'), '{}\n');
    const w = await cli(root, 'import', 'we-solve', '--path', checkout, '--unsolvedmath', um, '--revision', REV, '--date', DATE);
    expect(w.code).toBe(0);
    expect(w.out).toContain('18 records');
    expect(w.out).toContain('  same problem recorded twice (c): 13 -> 10 (-3)');
    expect(w.out).toContain('9 problems written, 0 removed');
    const u = await cli(root, 'import', 'unsolvedmath', '--path', um, '--revision', REV, '--date', DATE, '--dry-run');
    expect(u.code).toBe(0);
    expect(u.out).toContain('  we-solve has it (b): 12 -> 5 (-7)');
    expect(u.out).toContain('5 problems would be written');
    expect(existsSync(join(root, 'sources', 'unsolvedmath.json'))).toBe(false);
    expect((await cli(root, 'import', 'unsolvedmath', '--path', um)).out).toContain('pass --revision');
    expect((await cli(root, 'import', 'unsolvedmath', '--path', um, '--unsolvedmath', um)).code).toBe(2);
    expect((await cli(root, 'import', 'nowhere', '--path', um)).code).toBe(2);
  });
});

describe('prose import helpers', () => {
  test('openStatus: open beats partially solved, settled skips, uncertified catalogues are unverified', () => {
    const base = WeSolveRecord.parse({
      problem_id: 'prb_0007fc1635b9497fbfd2a64523550ac0', title: 't', kind: 'catalogued',
      disciplines: [{ discipline: 'mathematics', role: 'primary' }], statement_artifact: { path: 'statement.tex' },
      rights: { licence: 'CC-BY-4.0', redistribution: 'permitted' },
    });
    const src = (s: string) => ({ authority: 'a', normalised_status: s });
    expect(openStatus({ ...base, sources: [src('open'), src('partially_solved')] })).toBe('open');
    expect(openStatus({ ...base, sources: [src('partially_solved')] })).toBe('partially-solved');
    expect(openStatus({ ...base, sources: [src('open'), src('solved')] })).toEqual({ skip: 'status solved' });
    expect(openStatus({ ...base, sources: [] })).toBe('unverified');
    expect(openStatus({ ...base, sources: [src('unknown')] })).toEqual({ skip: 'status unknown' });
    expect(openStatus({ ...base, sources: [src('unknown')], extensions: { 'org.x': { open_status_certified: false } } })).toBe('unverified');
    for (const s of ['proved', 'disproved', 'other', 'independent']) expect(typeof openStatus({ ...base, sources: [src(s)] })).toBe('object');
  });

  test('catalogue keys from UnsolvedMath codes and formal-conjectures paths agree; Green numbers are not matched', () => {
    expect(catalogueKeyFromCode('EP-0428')).toBe('erdosproblems:428');
    expect(catalogueKeyFromCode('KOU-1.35')).toBe('kourovka:1.35');
    expect(catalogueKeyFromCode('HIL-012')).toBe('hilbert:12');
    expect(catalogueKeyFromCode('MPP-002')).toBe('millennium:RiemannHypothesis');
    expect(catalogueKeyFromCode('GREEN-061')).toBeNull();
    expect(catalogueKeyFromCode('OWR-698-004')).toBeNull();
    expect(catalogueKeyFromFcPath('FormalConjectures/ErdosProblems/428.lean')).toBe('erdosproblems:428');
    expect(catalogueKeyFromFcPath('FormalConjectures/Kourovka/1_35c.lean')).toBe('kourovka:1.35');
    expect(catalogueKeyFromFcPath('FormalConjectures/Millennium/RiemannHypothesis.lean')).toBe('millennium:RiemannHypothesis');
    expect(catalogueKeyFromFcPath('FormalConjectures/GreensOpenProblems/61.lean')).toBeNull();
  });

  test('practice problems never count as formal-conjectures having a problem', async () => {
    expect(formalConjecturesKeys([]).size).toBe(0);
    // The fixture root also holds erdos1.erdos-1.variants.weaker, a practice problem: no erdosproblems:1 key.
    const { root } = workspace();
    const keys = formalConjecturesKeys(await loadProblems(root));
    expect([...keys.keys()].sort()).toEqual(['erdosproblems:101', 'kourovka:1.40', 'millennium:RiemannHypothesis']);
  });

  test('title-and-statement matches need a title unique on both sides', () => {
    const w = wordSet('Does every smooth homotopy 4-sphere admit a diffeomorphism to the standard sphere');
    const u = wordSet('Is every smooth homotopy 4-sphere diffeomorphism standard sphere');
    expect(titleAndStatementMatch({ titleCountUnsolvedMath: 1, titleCountWeSolve: 1, unsolvedMathWords: u, weSolveWords: w })).toBe(true);
    expect(titleAndStatementMatch({ titleCountUnsolvedMath: 3, titleCountWeSolve: 1, unsolvedMathWords: u, weSolveWords: w })).toBe(false);
    expect(titleAndStatementMatch({ titleCountUnsolvedMath: 1, titleCountWeSolve: 1, unsolvedMathWords: wordSet('Lefschetz algebras'), weSolveWords: w })).toBe(false);
  });

  test('statement body, handle order, licences and references', () => {
    expect(statementBody('% c\n\\documentclass{article}\n\\begin{document}\nHello $x$.\n\\end{document}\n')).toBe('Hello $x$.');
    expect(statementBody('Plain $x$ text.\n')).toBe('Plain $x$ text.');
    expect(['TOP-100', 'ERDOS-2', 'TOP-12', 'TOP-2'].sort(compareHandles)).toEqual(['ERDOS-2', 'TOP-2', 'TOP-12', 'TOP-100']);
    expect(rowLicence({ problem_number: 'OWR-698-004', set: null })).toBe('CC-BY-SA-4.0');
    expect(rowLicence({ problem_number: 'AIM-X-1', set: { name: 'aim_workshop_problem_lists' } })).toBe('CC-BY-4.0');
    const refs = collectReferences(
      [{ label: 'page', url: 'https://example.org/a' }],
      ['See [paper](https://example.org/p_(v2)), \\href{https://example.org/q}{\\emph{Q}} and \\url{https://example.org/a} or https://example.org/r.'],
    );
    expect(refs).toEqual([
      { label: 'page', url: 'https://example.org/a' },
      { label: 'paper', url: 'https://example.org/p_(v2)' },
      { label: 'Q', url: 'https://example.org/q' },
      { label: 'https://example.org/r', url: 'https://example.org/r' },
    ]);
  });

  test('readUnsolvedMath needs a revision unless the directory pins one', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'frontier-um-'));
    writeFileSync(join(dir, 'problems.json'), '[]');
    await expect(readUnsolvedMath(dir)).rejects.toThrow('pass --revision');
    const snap = join(dir, 'snapshots', REV);
    mkdirSync(snap, { recursive: true });
    writeFileSync(join(snap, 'problems.json'), '[]');
    expect((await readUnsolvedMath(snap)).revision).toBe(REV);
  });
});
