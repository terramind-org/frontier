#!/usr/bin/env bun
import { existsSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { UsageError } from './args.ts';
import { cloneRequiredMessage, findCloneRoot } from './index-source.ts';

const commandsDir = join(dirname(fileURLToPath(import.meta.url)), 'commands');

interface Command {
  run(args: string[]): Promise<number>;
  help: string;
}

/**
 * Static command table, so a bundle (dist-cli/frontier.mjs) contains every command. From source the
 * commands directory is read instead, so a new command file shows up by existing; a test keeps this table complete.
 */
export const COMMAND_MODULES: Record<string, () => Promise<Command>> = {
  check: () => import('./commands/check.ts'),
  diagnose: () => import('./commands/diagnose.ts'),
  import: () => import('./commands/import.ts'),
  index: () => import('./commands/index.ts'),
  list: () => import('./commands/list.ts'),
  new: () => import('./commands/new.ts'),
  pick: () => import('./commands/pick.ts'),
  record: () => import('./commands/record.ts'),
  review: () => import('./commands/review.ts'),
  show: () => import('./commands/show.ts'),
  submit: () => import('./commands/submit.ts'),
  validate: () => import('./commands/validate.ts'),
};

/** Commands that also work outside a clone, reading the published index. */
export const READ_ONLY_COMMANDS = new Set(['list', 'show', 'pick']);

export function commandNames(): string[] {
  if (!existsSync(commandsDir)) return Object.keys(COMMAND_MODULES).sort();
  return readdirSync(commandsDir)
    .filter((f) => f.endsWith('.ts'))
    .map((f) => f.slice(0, -3))
    .sort();
}

async function loadCommand(name: string): Promise<Command> {
  const load = COMMAND_MODULES[name];
  if (load && !existsSync(commandsDir)) return load();
  return (await import(join(commandsDir, `${name}.ts`))) as Command;
}

async function helpText(): Promise<string> {
  const lines = ['frontier: open problems, attempts, checks anyone can rerun', '', 'Usage: bun frontier <command> [options]', '', 'Commands:'];
  for (const name of commandNames()) {
    const cmd = await loadCommand(name);
    const summary = cmd.help.split('\n').find((l) => l.trim() !== '') ?? '';
    lines.push(`  ${name.padEnd(10)} ${summary.replace(/^Usage:\s*/, '')}`);
  }
  lines.push('', 'Run `bun frontier <command> --help` for a command\'s options.');
  return lines.join('\n');
}

export async function main(argv: string[]): Promise<number> {
  const [name, ...rest] = argv;
  if (name === undefined || name === '--help' || name === '-h' || name === 'help') {
    console.log(await helpText());
    return 0;
  }
  if (!/^[a-z][a-z-]*$/.test(name) || !commandNames().includes(name)) {
    console.error(`Unknown command: ${name}\n`);
    console.error(await helpText());
    return 2;
  }
  const cmd = await loadCommand(name);
  if (rest.includes('--help') || rest.includes('-h')) {
    console.log(cmd.help);
    return 0;
  }
  if (!READ_ONLY_COMMANDS.has(name)) {
    if (!findCloneRoot()) {
      console.error(cloneRequiredMessage(name));
      return 2;
    }
    if (typeof Bun === 'undefined') {
      console.error(`frontier ${name} needs bun. Run it from the clone: bun frontier ${name}`);
      return 2;
    }
  }
  try {
    return await cmd.run(rest);
  } catch (e) {
    if (e instanceof UsageError) {
      console.error(`${e.message}\n\n${cmd.help}`);
      return 2;
    }
    console.error(`frontier ${name}: ${(e as Error).message}`);
    return 1;
  }
}

if (import.meta.main) {
  process.exit(await main(process.argv.slice(2)));
}
