/** Shared types and strict-shape helpers for the witness verifiers. */

export type Params = Record<string, number | string | boolean>;
export interface VerifyResult {
  valid: boolean;
  value?: number;
  reason?: string;
}

export const ok = (value: number): VerifyResult => ({ valid: true, value });
export const bad = (reason: string): VerifyResult => ({ valid: false, reason });

/** Thrown for malformed input; `guard` turns it into a rejection. */
export class Invalid extends Error {}
export function fail(reason: string): never {
  throw new Invalid(reason);
}

/** Run a verifier body; an `Invalid` throw becomes a rejected result, anything else propagates. */
export function guard(body: () => VerifyResult): VerifyResult {
  try {
    return body();
  } catch (e) {
    if (e instanceof Invalid) return bad(e.message);
    throw e;
  }
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
