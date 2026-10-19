import { describe, expect, test } from 'bun:test';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { main } from '../../src/cli.ts';
import { recordVerdict } from '../../src/commands/record.ts';
import { Verdict } from '../../src/schema.ts';
import { copyFixture, sh } from '../core/helpers.ts';

const ATTEMPT = 'attempts/toy.open-one/20260104-carol-cccccc';

async function gitRepo() {
  const root = copyFixture('good');
  await sh(root, 'git', 'init', '-q');
  await sh(root, 'git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'init');
  const head = (await sh(root, 'git', 'rev-parse', 'HEAD')).trim();
  const result = join(root, 'result.json');
  writeFileSync(result, JSON.stringify({ checker: 'none', result: 'unchecked', summary: 'Writeups are not machine-checked.' }));
  return { root, head, result, dir: join(root, ATTEMPT) };
}

describe('frontier record', () => {
  test('writes a Verdict with attempt id, time, commit and run url', async () => {
    const { root, head, result, dir } = await gitRepo();
    const now = new Date('2026-10-19T12:00:00Z');
    const v = await recordVerdict(root, dir, { resultFile: result, runUrl: 'https://github.com/o/r/actions/runs/1', now });
    expect(v.attempt).toBe('20260104-carol-cccccc');
    expect(v.checked_at).toBe('2026-10-19T12:00:00.000Z');
    expect(v.checker_version).toBe(head);
    const onDisk = Verdict.parse(JSON.parse(readFileSync(join(dir, 'verdict.json'), 'utf8')));
    expect(onDisk.run_url).toBe('https://github.com/o/r/actions/runs/1');
    expect(onDisk.result).toBe('unchecked');
  });

  test('refuses to overwrite a verdict unless forced', async () => {
    const { root, result, dir } = await gitRepo();
    await recordVerdict(root, dir, { resultFile: result });
    await expect(recordVerdict(root, dir, { resultFile: result })).rejects.toThrow(/already exists/);
    writeFileSync(result, JSON.stringify({ checker: 'none', result: 'error', summary: 'second' }));
    const v = await recordVerdict(root, dir, { resultFile: result, force: true });
    expect(v.summary).toBe('second');
  });

  test('rejects a result file that is not a VerdictResult', async () => {
    const { root, result, dir } = await gitRepo();
    writeFileSync(result, JSON.stringify({ checker: 'lean', result: 'maybe', summary: 'x' }));
    await expect(recordVerdict(root, dir, { resultFile: result })).rejects.toThrow(/not a VerdictResult/);
    expect(existsSync(join(dir, 'verdict.json'))).toBe(false);
  });

  test('CLI: usage errors and success', async () => {
    const { root, result, dir } = await gitRepo();
    const prev = process.cwd();
    const log = console.log;
    const err = console.error;
    console.log = () => {};
    console.error = () => {};
    process.chdir(root);
    try {
      expect(await main(['record', dir])).toBe(2);
      expect(await main(['record', '--result-file', result])).toBe(2);
      expect(await main(['record', dir, '--result-file', result, '--run-url', 'https://example.com/run'])).toBe(0);
      expect(await main(['record', dir, '--result-file', result])).toBe(1);
    } finally {
      process.chdir(prev);
      console.log = log;
      console.error = err;
    }
  });
});
