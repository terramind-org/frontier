/** Shared types and strict-shape helpers for the witness verifiers. */

export type Params = Record<string, number | string | boolean>;
export interface VerifyResult {
  valid: boolean;
  value?: number;
  reason?: string;
  /** Only with `{ all: true }`: every violation found, at most MAX_VIOLATIONS of them. */
  violations?: string[];
  /** Only with `{ all: true }`: violations found beyond the ones listed in `violations`. */
  omitted?: number;
  /** Only with `{ all: true }`: the scan stopped at SCAN_LIMIT violations, so `omitted` is a lower bound. */
  truncated?: boolean;
}

/** Optional third argument of every verifier. `all` collects every violation instead of stopping at the first. */
export interface VerifyOptions {
  all?: boolean;
}

/** Violations listed in `violations`; the rest are only counted. */
export const MAX_VIOLATIONS = 200;
/** In all mode the scan stops after this many violations (the count of the rest is then a lower bound). */
export const SCAN_LIMIT = 100_000;

export const ok = (value: number): VerifyResult => ({ valid: true, value });
export const bad = (reason: string): VerifyResult => ({ valid: false, reason });

/** Thrown for malformed input; `guard` turns it into a rejection. */
export class Invalid extends Error {}
export function fail(reason: string): never {
  throw new Invalid(reason);
}

class ScanLimit extends Error {}

/**
 * Where a verifier reports semantic violations. Default mode throws at the first one, so the result and message are
 * the same as before; with `{ all: true }` they are collected, the first MAX_VIOLATIONS kept and the rest counted.
 * A message may be a function so that violations past the cap cost no string building.
 */
export class Violations {
  readonly list: string[] = [];
  total = 0;
  /** The value the witness has, set as soon as it is known so that it survives an early stop. */
  value: number | undefined;
  constructor(readonly all: boolean) {}

  add(message: string | (() => string)): void {
    if (!this.all) fail(typeof message === 'function' ? message() : message);
    this.total++;
    if (this.list.length < MAX_VIOLATIONS) this.list.push(typeof message === 'function' ? message() : message);
    if (this.total >= SCAN_LIMIT) throw new ScanLimit();
  }
}

/**
 * Run a verifier body. `body` reports violations through `v` and returns the value the witness would have. A shape
 * error (`fail`) still ends the run: in all mode it is reported as the only violation.
 */
export function run(opts: VerifyOptions | undefined, body: (v: Violations) => number): VerifyResult {
  const v = new Violations(opts?.all === true);
  let truncated = false;
  try {
    v.value = body(v);
  } catch (e) {
    if (e instanceof ScanLimit) truncated = true;
    else if (e instanceof Invalid) {
      return v.all ? { valid: false, reason: e.message, violations: [e.message], omitted: 0 } : bad(e.message);
    } else throw e;
  }
  if (!v.all) return ok(v.value!);
  const result: VerifyResult = { valid: v.total === 0, violations: v.list, omitted: v.total - v.list.length };
  if (v.value !== undefined) result.value = v.value;
  if (v.total > 0) result.reason = v.list[0];
  if (truncated) result.truncated = true;
  return result;
}

/** A positive-or-zero safe integer parameter; a bad problem file is a programming error, not a rejection. */
export function intParam(params: Params, name: string, min: number, max = Number.MAX_SAFE_INTEGER): number {
  const v = params[name];
  if (typeof v !== 'number' || !Number.isSafeInteger(v) || v < min || v > max) {
    throw new Error(`verifier parameter "${name}" must be an integer in [${min}, ${max}], got ${JSON.stringify(v)}`);
  }
  return v;
}

/** The witness must be a JSON object whose keys are all in `allowed` and include every key in `required`. */
export function objectWith(witness: unknown, required: string[], optional: string[] = []): Record<string, unknown> {
  if (witness === null || typeof witness !== 'object' || Array.isArray(witness)) {
    return fail('witness.json must be a JSON object');
  }
  const obj = witness as Record<string, unknown>;
  for (const k of required) if (!(k in obj)) fail(`witness.json is missing the key "${k}"`);
  for (const k of Object.keys(obj)) {
    if (!required.includes(k) && !optional.includes(k)) fail(`witness.json has the unexpected key "${k}"`);
  }
  return obj;
}

export function arrayOf(value: unknown, what: string): unknown[] {
  if (!Array.isArray(value)) return fail(`${what} must be an array`);
  return value;
}

export function safeInt(value: unknown, what: string): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value)) {
    return fail(`${what} must be an integer (got ${JSON.stringify(value)})`);
  }
  return value;
}
