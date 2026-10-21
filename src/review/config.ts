import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { z } from 'zod';

export const PROVIDERS = ['anthropic', 'openai', 'google'] as const;
export type ProviderName = (typeof PROVIDERS)[number];

export const ReviewerConfig = z
  .object({
    provider: z.enum(PROVIDERS),
    model: z.string().min(1),
    // Name of the environment variable holding the key (in CI: a repository secret of the same name).
    api_key_env: z.string().regex(/^[A-Z][A-Z0-9_]*$/),
    // Reasoning depth; every default model reasons before it answers, and these tokens are billed as output.
    effort: z.enum(['low', 'medium', 'high']).default('medium'),
    // Sent only when set. The three default models reject or ignore sampling parameters (see review.config.json).
    temperature: z.number().min(0).max(2).optional(),
    // Standard list price, USD per million tokens, for the cost estimate `review` prints. Never sent anywhere.
    price_usd_per_mtok: z.object({ input: z.number().min(0), output: z.number().min(0) }).strict(),
  })
  .strict();

export const PanelConfig = z
  .object({
    schema: z.literal(1),
    // A writeup longer than this is cut at this many characters, and the review says so.
    max_input_chars: z.number().int().positive(),
    // The problem statement (and Lean statement) are cut at this many characters.
    max_statement_chars: z.number().int().positive(),
    // Cap on each reply, thinking included.
    max_output_tokens: z.number().int().positive(),
    // Default cap on writeups reviewed per CI run; the env var REVIEW_MAX_ATTEMPTS overrides it.
    max_attempts_per_run: z.number().int().positive(),
    reviewers: z.array(ReviewerConfig).min(1),
    sources: z.array(z.string()).optional(), // where the prices and API shapes were looked up
  })
  .strict();

export type ReviewerConfig = z.infer<typeof ReviewerConfig>;
export type PanelConfig = z.infer<typeof PanelConfig>;

export const CONFIG_FILE = 'review.config.json';

/** The checkout this code runs from, whose review.config.json applies when the data root has none (e.g. a fixture). */
const SOURCE_ROOT = join(import.meta.dir, '..', '..');

export async function loadPanelConfig(root: string): Promise<PanelConfig> {
  const file = [join(root, CONFIG_FILE), join(SOURCE_ROOT, CONFIG_FILE)].find((f) => existsSync(f)) ?? join(root, CONFIG_FILE);
  if (!existsSync(file)) throw new Error(`${CONFIG_FILE} not found at the repo root`);
  const parsed = PanelConfig.safeParse(JSON.parse(await readFile(file, 'utf8')));
  if (!parsed.success) {
    throw new Error(`${CONFIG_FILE} is invalid: ${parsed.error.issues.map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ')}`);
  }
  return parsed.data;
}

/** The per-run cap: REVIEW_MAX_ATTEMPTS if it is a positive integer, else the config default. */
export function maxAttemptsPerRun(config: PanelConfig, env: Record<string, string | undefined> = process.env): number {
  const raw = env.REVIEW_MAX_ATTEMPTS?.trim();
  if (raw && /^\d+$/.test(raw) && Number(raw) > 0) return Number(raw);
  return config.max_attempts_per_run;
}
