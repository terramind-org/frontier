import { parseArgs } from 'node:util';

/** A command-line usage mistake; the CLI prints the command's help and exits 2. */
export class UsageError extends Error {}

type Options = NonNullable<Parameters<typeof parseArgs>[0]>['options'];

/** Strict `node:util` parseArgs that reports mistakes as UsageError. */
export function parse<O extends NonNullable<Options>>(args: string[], options: O) {
  try {
    return parseArgs({ args, options, allowPositionals: true, strict: true });
  } catch (e) {
    throw new UsageError((e as Error).message);
  }
}
