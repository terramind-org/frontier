/**
 * Provider adapters over plain fetch (no SDKs). Each turns one review prompt into one HTTP request and reads the
 * reply text, the stop condition and the token usage back out. Request shapes, as documented in October 2026:
 *
 * - Anthropic Messages API: POST https://api.anthropic.com/v1/messages, headers x-api-key and
 *   anthropic-version: 2023-06-01; JSON output via output_config.format {type: json_schema}; depth via
 *   output_config.effort. Claude Opus 5.5 always thinks and rejects temperature (400), so it is sent only if configured.
 * - OpenAI Responses API: POST https://api.openai.com/v1/responses, Authorization: Bearer; JSON output via
 *   text.format {type: json_schema, strict: true}; depth via reasoning.effort; max_output_tokens includes reasoning.
 * - Gemini API: POST https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent, header
 *   x-goog-api-key; JSON output via generationConfig.responseMimeType + responseJsonSchema; depth via
 *   generationConfig.thinkingConfig.thinkingLevel; maxOutputTokens includes thinking.
 */
import type { ProviderName, ReviewerConfig } from './config.ts';
import { MODEL_REPLY_JSON_SCHEMA } from './prompt.ts';

export type FetchFn = (url: string, init: RequestInit) => Promise<Response>;

export interface ProviderRequest {
  url: string;
  headers: Record<string, string>;
  body: Record<string, unknown>;
}

export interface ProviderReply {
  /** The JSON text the model returned, or null when there is none. */
  text: string | null;
  /** Why there is no usable text (refusal, cut at the token limit, blocked), if that is the case. */
  problem: string | null;
  usage: { input: number; output: number };
}

interface Adapter {
  request(r: ReviewerConfig, key: string, system: string, user: string, maxOutputTokens: number): ProviderRequest;
  parse(json: any): ProviderReply;
}

const num = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? v : 0);

const anthropic: Adapter = {
  request(r, key, system, user, maxOutputTokens) {
    return {
      url: 'https://api.anthropic.com/v1/messages',
      headers: { 'content-type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01' },
      body: {
        model: r.model,
        max_tokens: maxOutputTokens,
        system,
        messages: [{ role: 'user', content: user }],
        output_config: { effort: r.effort, format: { type: 'json_schema', schema: MODEL_REPLY_JSON_SCHEMA } },
        ...(r.temperature !== undefined ? { temperature: r.temperature } : {}),
      },
    };
  },
  parse(json) {
    const usage = { input: num(json?.usage?.input_tokens), output: num(json?.usage?.output_tokens) };
    const stop = json?.stop_reason;
    const texts = (Array.isArray(json?.content) ? json.content : []).filter((b: any) => b?.type === 'text' && typeof b.text === 'string');
    if (stop === 'refusal') return { text: null, problem: `the model declined (refusal${json?.stop_details?.category ? `: ${json.stop_details.category}` : ''})`, usage };
    if (stop === 'max_tokens') return { text: null, problem: 'the reply was cut at the output token limit', usage };
    if (!texts.length) return { text: null, problem: `no text in the reply (stop_reason ${String(stop)})`, usage };
    return { text: texts.map((b: any) => b.text).join(''), problem: null, usage };
  },
};

const openai: Adapter = {
  request(r, key, system, user, maxOutputTokens) {
    return {
      url: 'https://api.openai.com/v1/responses',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${key}` },
      body: {
        model: r.model,
        instructions: system,
        input: user,
        max_output_tokens: maxOutputTokens,
        reasoning: { effort: r.effort },
        text: { format: { type: 'json_schema', name: 'writeup_review', schema: MODEL_REPLY_JSON_SCHEMA, strict: true } },
        store: false,
        ...(r.temperature !== undefined ? { temperature: r.temperature } : {}),
      },
    };
  },
  parse(json) {
    const usage = { input: num(json?.usage?.input_tokens), output: num(json?.usage?.output_tokens) };
    if (json?.status === 'incomplete') {
      return { text: null, problem: `the reply is incomplete (${json?.incomplete_details?.reason ?? 'unknown reason'})`, usage };
    }
    const parts = (Array.isArray(json?.output) ? json.output : [])
      .filter((o: any) => o?.type === 'message')
      .flatMap((o: any) => (Array.isArray(o.content) ? o.content : []));
    const refusal = parts.find((c: any) => c?.type === 'refusal');
    if (refusal) return { text: null, problem: `the model declined: ${String(refusal.refusal ?? '').slice(0, 300)}`, usage };
    const texts = parts.filter((c: any) => c?.type === 'output_text' && typeof c.text === 'string');
    if (!texts.length) return { text: null, problem: `no text in the reply (status ${String(json?.status)})`, usage };
    return { text: texts.map((c: any) => c.text).join(''), problem: null, usage };
  },
};

const google: Adapter = {
  request(r, key, system, user, maxOutputTokens) {
    return {
      url: `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(r.model)}:generateContent`,
      headers: { 'content-type': 'application/json', 'x-goog-api-key': key },
      body: {
        systemInstruction: { parts: [{ text: system }] },
        contents: [{ role: 'user', parts: [{ text: user }] }],
        generationConfig: {
          maxOutputTokens,
          responseMimeType: 'application/json',
          responseJsonSchema: MODEL_REPLY_JSON_SCHEMA,
          thinkingConfig: { thinkingLevel: r.effort },
          ...(r.temperature !== undefined ? { temperature: r.temperature } : {}),
        },
      },
    };
  },
  parse(json) {
    const m = json?.usageMetadata ?? {};
    const usage = { input: num(m.promptTokenCount), output: num(m.candidatesTokenCount) + num(m.thoughtsTokenCount) };
    if (json?.promptFeedback?.blockReason) return { text: null, problem: `the prompt was blocked (${json.promptFeedback.blockReason})`, usage };
    const cand = Array.isArray(json?.candidates) ? json.candidates[0] : undefined;
    if (!cand) return { text: null, problem: 'no candidate in the reply', usage };
    if (cand.finishReason === 'MAX_TOKENS') return { text: null, problem: 'the reply was cut at the output token limit', usage };
    const parts = (Array.isArray(cand.content?.parts) ? cand.content.parts : []).filter((p: any) => !p?.thought && typeof p?.text === 'string');
    if (!parts.length) return { text: null, problem: `no text in the reply (finishReason ${String(cand.finishReason)})`, usage };
    return { text: parts.map((p: any) => p.text).join(''), problem: null, usage };
  },
};

export const ADAPTERS: Record<ProviderName, Adapter> = { anthropic, openai, google };

/** A failure to get any reply (network, HTTP status): the review is not about the writeup, so it may be retried. */
export class TransportError extends Error {}

/** Call one provider once (one retry on 429, 5xx or a network error). Never logs the key. */
export async function callProvider(
  r: ReviewerConfig,
  key: string,
  system: string,
  user: string,
  maxOutputTokens: number,
  opts: { fetch: FetchFn; timeoutMs?: number; retryDelayMs?: number },
): Promise<ProviderReply> {
  const adapter = ADAPTERS[r.provider];
  const req = adapter.request(r, key, system, user, maxOutputTokens);
  let last = '';
  for (let attempt = 0; attempt < 2; attempt++) {
    if (attempt > 0) await new Promise((res) => setTimeout(res, opts.retryDelayMs ?? 5000));
    let res: Response;
    try {
      res = await opts.fetch(req.url, {
        method: 'POST',
        headers: req.headers,
        body: JSON.stringify(req.body),
        signal: AbortSignal.timeout(opts.timeoutMs ?? 10 * 60 * 1000),
      });
    } catch (e) {
      last = `request failed: ${(e as Error).message}`;
      continue;
    }
    const body = await res.text();
    if (!res.ok) {
      last = `HTTP ${res.status}: ${body.replace(/\s+/g, ' ').slice(0, 300)}`;
      if (res.status === 429 || res.status >= 500) continue;
      throw new TransportError(last);
    }
    let json: unknown;
    try {
      json = JSON.parse(body);
    } catch {
      throw new TransportError(`the API answered with something that is not JSON: ${body.slice(0, 200)}`);
    }
    return adapter.parse(json);
  }
  throw new TransportError(last);
}
