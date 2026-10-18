#!/usr/bin/env bun
import { existsSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { UsageError } from './args.ts';

const commandsDir = join(dirname(fileURLToPath(import.meta.url)), 'commands');

interface Command {
  run(args: string[]): Promise<number>;
  help: string;
}

/** Commands are the .ts files in src/commands; a command added by another task shows up by existing. */
export function commandNames(): string[] {
  return readdirSync(commandsDir)
    .filter((f) => f.endsWith('.ts'))
    .map((f) => f.slice(0, -3))
    .sort();
}

async function loadCommand(name: string): Promise<Command> {
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
  if (!/^[a-z][a-z-]*$/.test(name) || !existsSync(join(commandsDir, `${name}.ts`))) {
    console.error(`Unknown command: ${name}\n`);
    console.error(await helpText());
    return 2;
  }
  const cmd = await loadCommand(name);
  if (rest.includes('--help') || rest.includes('-h')) {
    console.log(cmd.help);
    return 0;
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
