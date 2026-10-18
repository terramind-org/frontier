import { randomBytes } from 'node:crypto';

const PROBLEM_ID = /^[a-z0-9][a-z0-9.-]*[a-z0-9]$/;
const ATTEMPT_ID = /^\d{8}-[a-z0-9-]{1,39}-[0-9a-f]{6}$/;
export const MAX_PROBLEM_ID_LENGTH = 120;

export function isProblemId(id: unknown): id is string {
  return typeof id === 'string' && id.length <= MAX_PROBLEM_ID_LENGTH && PROBLEM_ID.test(id);
}

export function isAttemptId(id: unknown): id is string {
  return typeof id === 'string' && ATTEMPT_ID.test(id);
}

/**
 * Problem id from a Lean full declaration name: NFKD-normalise, drop non-ASCII and guillemets,
 * lowercase, turn `_` and anything outside [a-z0-9.] into `-`, collapse repeats, trim `-` and `.`.
 * Collisions are the caller's job (append -2, -3 in declaration order).
 */
export function problemIdFromLeanName(name: string): string {
  const id = name
    .normalize('NFKD')
    .replace(/[«»]/g, '')
    .replace(/[^\x00-\x7f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9.]/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^[-.]+|[-.]+$/g, '')
    .slice(0, MAX_PROBLEM_ID_LENGTH)
    .replace(/[-.]+$/, '');
  if (!isProblemId(id)) throw new Error(`cannot derive a problem id from Lean name ${JSON.stringify(name)}`);
  return id;
}

/** `<YYYYMMDD>-<github-login-lowercased>-<6 hex>`; the date is UTC. */
export function newAttemptId(login: string, date: Date = new Date()): string {
  const day = date.toISOString().slice(0, 10).replaceAll('-', '');
  const id = `${day}-${login.toLowerCase()}-${randomBytes(3).toString('hex')}`;
  if (!isAttemptId(id)) throw new Error(`invalid GitHub login for an attempt id: ${JSON.stringify(login)}`);
  return id;
}
