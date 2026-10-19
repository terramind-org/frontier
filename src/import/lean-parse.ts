/** Text-level parsing of formal-conjectures `.lean` files. No Lean needed. */

export interface OpenDecl {
  /** Full Lean name: enclosing namespaces + the declaration's own (possibly dotted) name, as written. */
  fullName: string;
  /** The declaration's own name as written after `theorem`/`lemma`. */
  ownName: string;
  keyword: 'theorem' | 'lemma';
  /** 1-based line of the `theorem`/`lemma` keyword. */
  line: number;
  /** Source from the keyword up to, excluding, the `:=` that starts the proof; trimmed. */
  statement: string;
  /** Dedented docstring directly before the attribute block, or null. */
  docstring: string | null;
  /** Numbers after `AMS` in the attribute block. */
  ams: number[];
  /** Module doc blocks that start before this declaration, in file order. */
  moduleDocs: string[];
  /** Enclosing namespace segments at the declaration (what Lean resolves relative names against). */
  namespace: string[];
}

export interface ParsedFile {
  /** `# Title` heading of the file's first module doc, or null. */
  title: string | null;
  decls: OpenDecl[];
  /**
   * Full names of `def`/`abbrev` declarations (any modifiers) in this file whose body is exactly
   * `sorry`, with the name as written in the file.
   */
  sorryDefs: SorryDef[];
}

export interface SorryDef {
  fullName: string;
  ownName: string;
}

interface Comment {
  start: number;
  end: number;
  kind: 'doc' | 'mod' | 'plain' | 'line';
}

/**
 * Replace comments and string literals by spaces (newlines kept) so offsets and line numbers stay
 * valid, and collect the comment ranges.
 */
function mask(text: string): { masked: string; comments: Comment[] } {
  const out = text.split('');
  const comments: Comment[] = [];
  const blank = (from: number, to: number) => {
    for (let k = from; k < to; k++) if (out[k] !== '\n') out[k] = ' ';
  };
  let i = 0;
  while (i < text.length) {
    const c = text[i]!;
    if (c === '-' && text[i + 1] === '-') {
      let j = text.indexOf('\n', i);
      if (j < 0) j = text.length;
      comments.push({ start: i, end: j, kind: 'line' });
      blank(i, j);
      i = j;
    } else if (c === '/' && text[i + 1] === '-') {
      const kind = text[i + 2] === '-' ? 'doc' : text[i + 2] === '!' ? 'mod' : 'plain';
      let depth = 1;
      let j = i + 2;
      while (j < text.length && depth > 0) {
        if (text[j] === '/' && text[j + 1] === '-') { depth++; j += 2; }
        else if (text[j] === '-' && text[j + 1] === '/') { depth--; j += 2; }
        else j++;
      }
      comments.push({ start: i, end: j, kind });
      blank(i, j);
      i = j;
    } else if (c === '"') {
      let j = i + 1;
      while (j < text.length && text[j] !== '"') j += text[j] === '\\' ? 2 : 1;
      blank(i + 1, Math.min(j, text.length));
      i = j + 1;
    } else if (c === "'" && text[i + 2] === "'" && text[i + 1] === '"') {
      i += 3; // the character literal '"'
    } else {
      i++;
    }
  }
  return { masked: out.join(''), comments };
}

const OPEN = new Set(['(', '[', '{', '⟨', '⦃']);
const CLOSE = new Set([')', ']', '}', '⟩', '⦄']);

/** Index just past the `]` that closes the `[` at `open`. */
function matchBracket(masked: string, open: number): number {
  let depth = 0;
  for (let j = open; j < masked.length; j++) {
    const c = masked[j]!;
    if (c === '[') depth++;
    else if (c === ']' && --depth === 0) return j + 1;
  }
  throw new Error('unterminated attribute block');
}

const NAME = /(?:«[^»]*»|[^\s:(){}[\]⟨⟩⦃⦄«»])+/y;

/** End offset (exclusive) of the statement: the first `:=` at bracket depth 0 that starts the proof. */
function statementEnd(masked: string, from: number): number {
  let depth = 0;
  let pending = 0; // `let`/`have` binders at depth 0 still waiting for their own `:=`
  for (let j = from; j < masked.length; j++) {
    const c = masked[j]!;
    if (OPEN.has(c)) depth++;
    else if (CLOSE.has(c)) depth--;
    else if (depth === 0 && c === ':' && masked[j + 1] === '=') {
      if (pending > 0) { pending--; j++; continue; }
      return j;
    } else if (depth === 0 && /[a-z]/.test(c) && !/[\w'.!?«»]/.test(masked[j - 1] ?? ' ')) {
      const m = /^(let|have)(?![\w'.!?])/.exec(masked.slice(j, j + 5));
      if (m) pending++;
    }
  }
  throw new Error('no `:=` found after the statement');
}

function dedent(s: string): string {
  const lines = s.replace(/\r\n/g, '\n').split('\n');
  const indents = lines.filter((l) => l.trim() !== '').map((l) => /^[ \t]*/.exec(l)![0].length);
  const min = indents.length ? Math.min(...indents) : 0;
  return lines.map((l) => l.slice(min).trimEnd()).join('\n').trim();
}

function docBody(text: string, c: Comment): string {
  return dedent(text.slice(c.start + 3, c.end - 2));
}

interface Frame {
  kind: 'namespace' | 'section';
  names: string[];
}

const SCOPE_LINE = /^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:(?:public|private|protected|noncomputable|meta)[ \t]+)*(namespace|section|end)\b[ \t]*([^\n]*)$/gm;

/** Split a possibly dotted name on dots outside `«»`. */
function splitName(name: string): string[] {
  return name.match(/(?:«[^»]*»|[^.«»])+/g) ?? [];
}

const DEF_START = /^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:(?:private|protected|noncomputable|nonrec|unsafe|partial|public|meta)[ \t]+)*(?:def|abbrev)[ \t]+/gm;
/** The start of any later top-level command; a definition's text never runs past it. */
const NEXT_COMMAND = /\n(?=[ \t]*(?:@\[|(?:(?:private|protected|noncomputable|nonrec|unsafe|partial|public|meta)[ \t]+)*(?:theorem|lemma|def|abbrev|instance|structure|inductive|class|example|axiom|opaque|namespace|section|end|open|variable|universe|attribute|macro|syntax|notation|local|scoped)\b))/;

/** Replay namespace/section events up to `at`, returning the namespace segments in scope. */
function namespaceAt(events: { at: number; kind: string; name: string }[], at: number): string[] {
  const stack: Frame[] = [];
  for (const e of events) {
    if (e.at >= at) break;
    if (e.kind === 'end') stack.pop();
    else stack.push({ kind: e.kind as Frame['kind'], names: e.kind === 'namespace' ? splitName(e.name) : [] });
  }
  return stack.flatMap((f) => f.names);
}

function findSorryDefs(masked: string, events: { at: number; kind: string; name: string }[]): SorryDef[] {
  const out: SorryDef[] = [];
  for (const m of masked.matchAll(DEF_START)) {
    const nameStart = m.index! + m[0].length;
    NAME.lastIndex = nameStart;
    const nm = NAME.exec(masked);
    if (!nm) continue;
    let ownName = nm[0];
    if (ownName.endsWith('.')) ownName = ownName.slice(0, -1);
    const rest = masked.slice(nameStart);
    const limit = NEXT_COMMAND.exec(rest);
    const region = limit ? rest.slice(0, limit.index) : rest;
    let end: number;
    try {
      end = statementEnd(region, 0);
    } catch {
      continue; // no `:=` (pattern-matching or structure-like definition): not a bare `sorry`
    }
    if (!/^:=\s*sorry\s*$/.test(region.slice(end))) continue;
    let prefix = namespaceAt(events, m.index!);
    let local = ownName;
    if (local.startsWith('_root_.')) { prefix = []; local = local.slice('_root_.'.length); }
    out.push({ fullName: [...prefix, local].join('.'), ownName });
  }
  return out;
}

export function parseLeanFile(text: string): ParsedFile {
  text = text.replace(/\r\n/g, '\n');
  const { masked, comments } = mask(text);
  const lineOf = (offset: number) => text.slice(0, offset).split('\n').length;
  const modDocs = comments.filter((c) => c.kind === 'mod');
  const titleMatch = modDocs.length ? /^#[ \t]+(.+?)[ \t]*$/m.exec(docBody(text, modDocs[0]!)) : null;

  // Scope events in file order.
  const events: { at: number; kind: string; name: string }[] = [];
  for (const m of masked.matchAll(SCOPE_LINE)) {
    events.push({ at: m.index!, kind: m[1]!, name: (m[2] ?? '').trim().split(/\s+/)[0] ?? '' });
  }

  // Open declarations.
  const found: { attrStart: number; attrEnd: number }[] = [];
  for (let i = masked.indexOf('@['); i >= 0; i = masked.indexOf('@[', i + 2)) {
    const end = matchBracket(masked, i + 1);
    if (/\bcategory\s+research\s+open\b/.test(masked.slice(i, end))) found.push({ attrStart: i, attrEnd: end });
  }

  const decls: OpenDecl[] = [];
  let ev = 0;
  let stack: Frame[] = [];
  for (const { attrStart, attrEnd } of found) {
    while (ev < events.length && events[ev]!.at < attrStart) {
      const e = events[ev++]!;
      if (e.kind === 'end') stack.pop();
      else stack.push({ kind: e.kind as Frame['kind'], names: e.kind === 'namespace' ? splitName(e.name) : [] });
    }
    const after = /^\s*(?:(?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*(theorem|lemma)\s+/.exec(masked.slice(attrEnd));
    if (!after) throw new Error(`line ${lineOf(attrStart)}: open attribute is not followed by theorem/lemma`);
    const keyword = after[1] as 'theorem' | 'lemma';
    const kw = attrEnd + after[0].length - after[1]!.length - /\s+$/.exec(after[0])![0].length;
    const nameStart = attrEnd + after[0].length;
    NAME.lastIndex = nameStart;
    const nm = NAME.exec(masked);
    if (!nm) throw new Error(`line ${lineOf(kw)}: no declaration name`);
    let ownName = nm[0];
    if (ownName.endsWith('.')) ownName = ownName.slice(0, -1); // `foo.{u}`
    const end = statementEnd(masked, nameStart);
    const statement = text.slice(kw, end).trim();

    let prefix = stack.flatMap((f) => f.names);
    let local = ownName;
    if (local.startsWith('_root_.')) { prefix = []; local = local.slice('_root_.'.length); }
    const fullName = [...prefix, local].join('.');

    // Docstring: the `/-- … -/` comment that ends right before the attribute block, ignoring
    // whitespace and plain `--` / `/- -/` comments in between (e.g. upstream `-- TODO` notes).
    let p = attrStart;
    for (;;) {
      while (p > 0 && /\s/.test(text[p - 1]!)) p--;
      const plain = comments.find((c) => (c.kind === 'line' || c.kind === 'plain') && c.end === p);
      if (!plain) break;
      p = plain.start;
    }
    const doc = comments.find((c) => c.kind === 'doc' && c.end === p);

    const ams = /\bAMS((?:\s+\d+)+)/.exec(masked.slice(attrStart, attrEnd));
    decls.push({
      fullName,
      ownName,
      keyword,
      line: lineOf(kw),
      statement,
      docstring: doc ? docBody(text, doc) : null,
      ams: ams ? ams[1]!.trim().split(/\s+/).map(Number) : [],
      moduleDocs: modDocs.filter((c) => c.start < attrStart).map((c) => docBody(text, c)),
      namespace: prefix,
    });
  }
  return { title: titleMatch ? titleMatch[1]! : null, decls, sorryDefs: findSorryDefs(masked, events) };
}

/** Dotted identifier tokens of a Lean snippet (comments already irrelevant: statements are code). */
function identifierTokens(statement: string): string[] {
  return statement.match(/(?:«[^»]*»|[A-Za-z_\u00C0-\u02FF\u0370-\u03FF\u1F00-\u1FFF\u2100-\u214F])(?:«[^»]*»|[\w'!?.\u00C0-\u02FF\u0370-\u03FF\u1F00-\u1FFF\u2080-\u209C\u2100-\u214F])*/gu) ?? [];
}

/**
 * True when the statement mentions one of the `sorry` definitions: by full name, by the name as
 * written in the file, or by any name Lean would resolve to it from the declaration's namespace
 * (or a field-style continuation of such a name). Deliberately conservative.
 */
export function referencesSorryDef(decl: Pick<OpenDecl, 'statement' | 'namespace'>, defs: SorryDef[]): boolean {
  if (defs.length === 0) return false;
  const full = new Set(defs.map((d) => d.fullName));
  const written = new Set(defs.map((d) => d.ownName));
  for (const token of identifierTokens(decl.statement)) {
    const segs = splitName(token);
    for (let n = 1; n <= segs.length; n++) {
      const name = segs.slice(0, n).join('.');
      if (written.has(name)) return true;
      for (let k = 0; k <= decl.namespace.length; k++) {
        if (full.has([...decl.namespace.slice(0, k), name].join('.'))) return true;
      }
    }
  }
  return false;
}
