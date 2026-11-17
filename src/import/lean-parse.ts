/** Text-level parsing of formal-conjectures `.lean` files. No Lean needed. */

/** Upstream `category` values the parser can collect. */
export type Category = 'research open' | 'research solved' | 'textbook';

export interface OpenDecl {
  /** Full Lean name: enclosing namespaces + the declaration's own (possibly dotted) name, as written. */
  fullName: string;
  /** The declaration's own name as written after `theorem`/`lemma`. */
  ownName: string;
  keyword: 'theorem' | 'lemma';
  /** Upstream category from the attribute block. */
  category: Category;
  /** Declared `private` (its real name is mangled, so nothing outside the file can name it). */
  isPrivate: boolean;
  /** 1-based line of the `theorem`/`lemma` keyword. */
  line: number;
  /** Source from the keyword up to, excluding, the `:=` that starts the proof; trimmed. */
  statement: string;
  /** Dedented docstring directly before the attribute block, or null. */
  docstring: string | null;
  /** Numbers after `AMS` in the attribute block. */
  ams: number[];
  /** URL of `formal_proof using <tool> at "<url>"` in the attribute block, if any. */
  formalProof: string | null;
  /** Module doc blocks that start before this declaration, in file order. */
  moduleDocs: string[];
  /** Enclosing namespace segments at the declaration (what Lean resolves relative names against). */
  namespace: string[];
  /**
   * Lines a scaffold needs before the theorem, in this order: `open <ns>` for every namespace enclosing
   * the declaration (outermost first), every upstream `open …` in effect at it (including `open … in`
   * directly before it, without the `in`), and every `local notation`/`local infix…`/`local prefix`/
   * `local postfix` command in effect at it, verbatim.
   */
  context: string[];
  /** Number of source lines from the `:=` (or `where`) that starts the proof to the declaration's end. */
  proofLines: number;
  /** The proof with comments and string literals blanked, for token checks; never stored. */
  maskedProof: string;
}

export type DefKind = 'def' | 'abbrev' | 'structure' | 'inductive' | 'class';

export interface DefDecl {
  fullName: string;
  /** Name as written after the keyword. */
  ownName: string;
  kind: DefKind;
  /** Source text: the doc comment directly above (if any) through the end of the declaration. */
  text: string;
  /** 1-based line where `text` starts. */
  line: number;
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
  /** Every `def`/`abbrev`/`structure`/`inductive`/`class` declaration of the file, in file order. */
  defs: DefDecl[];
}

export interface SorryDef {
  fullName: string;
  ownName: string;
}

export interface ParseOptions {
  /** Categories to collect; default `['research open']`. */
  categories?: Category[];
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

/**
 * Binder keywords whose own `:=` comes before the proof's: `let x := v; body`, `letI`, `have`, `haveI`,
 * `let_fun` and `set x := v`. `set` only counts before a name, so a variable called `set` does not.
 */
const BINDER = /^(?:let_fun|letI|haveI|let|have)(?![\w'.!?])|^set(?=[ \t]+[A-Za-z_À-˿Ͱ-Ͽ«])/;
/** `where` that starts a declaration body (`theorem t : T where field := …`). */
const WHERE = /^where(?![\w'.!?])/;

/**
 * End offset (exclusive) of the statement in comment-masked source: the first `:=` at bracket depth 0
 * that starts the proof, or a depth-0 `where` that starts a structure-instance body (whose field
 * `:=`s come after it). The `:=` of a depth-0 binder (`let`, `letI`, `have`, `haveI`, `let_fun`,
 * `set`) belongs to that binder and is skipped; a `:=` inside brackets (structure instances
 * `{ f := … }`, binder defaults `(h : p := rfl)`) is never at depth 0.
 */
export function statementEnd(masked: string, from: number): number {
  let depth = 0;
  let pending = 0; // binders at depth 0 still waiting for their own `:=`
  for (let j = from; j < masked.length; j++) {
    const c = masked[j]!;
    if (OPEN.has(c)) depth++;
    else if (CLOSE.has(c)) depth--;
    else if (depth === 0 && c === ':' && masked[j + 1] === '=') {
      if (pending > 0) { pending--; j++; continue; }
      return j;
    } else if (depth === 0 && /[a-z]/.test(c) && !/[\w'.!?«»]/.test(masked[j - 1] ?? ' ')) {
      const head = masked.slice(j, j + 12);
      if (BINDER.test(head)) pending++;
      else if (pending === 0 && WHERE.test(head)) return j;
    }
  }
  throw new Error('no `:=` found after the statement');
}

/**
 * Offset of the `:=` (or body `where`) that starts a proof in a Lean snippet, ignoring comments,
 * string literals and binder `:=`s (see `statementEnd`); null when the snippet has no proof.
 */
export function proofStart(text: string): number | null {
  try {
    return statementEnd(mask(text).masked, 0);
  } catch {
    return null;
  }
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

/** Split a possibly dotted name on dots outside `«»`. */
function splitName(name: string): string[] {
  return name.match(/(?:«[^»]*»|[^.«»])+/g) ?? [];
}

const MODIFIERS = '(?:(?:private|protected|noncomputable|nonrec|unsafe|partial|public|meta)[ \\t]+)*';
const DEF_START = new RegExp(`^[ \\t]*(?:@\\[[^\\]\\n]*\\][ \\t]*)?${MODIFIERS}(?:def|abbrev)[ \\t]+`, 'gm');
/** Definitions whose text `show` can print; attributes may sit on the line above. */
const DEF_DECL = new RegExp(
  `^[ \\t]*(?:@\\[[^\\]]*\\][ \\t\\n]*)?${MODIFIERS}(def|abbrev|structure|inductive|class(?:[ \\t]+inductive)?)[ \\t]+`,
  'gm',
);
/** The start of any later top-level command; a definition's text never runs past it. */
const NEXT_COMMAND = /\n(?=[ \t]*(?:@\[|(?:(?:private|protected|noncomputable|nonrec|unsafe|partial|public|meta)[ \t]+)*(?:theorem|lemma|def|abbrev|instance|structure|inductive|class|example|axiom|opaque|namespace|section|end|open|variable|universe|attribute|macro|syntax|notation|local|scoped|set_option|#[a-z]+)\b))/;
/** A non-blank character in column 0: the next command after an (indented) proof. */
const COLUMN_ZERO = /\n(?=[^\s])/;
const SCOPE_LINE = /^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:(?:public|private|protected|noncomputable|meta)[ \t]+)*(namespace|section|end)\b[ \t]*([^\n]*)$/gm;
const OPEN_LINE = /^[ \t]*open[ \t]+([^\n]*)$/gm;
const LOCAL_NOTATION = /^[ \t]*local[ \t]+(?:notation3?|infix[lr]?|prefix|postfix)(?![\w'])/gm;
// File-level `set_option` and `variable` commands are in scope for later declarations too: a statement can
// depend on them (e.g. `set_option quotPrecheck false` before a set-builder notation, or `variable [Field K]`).
// `… in` forms apply to one command only and are skipped; `debug.*` options are never copied (the pre-check bans them).
const SET_OPTION = /^[ \t]*set_option[ \t]+(?!debug\.)[\w.]+[ \t]+[^\s]+[ \t]*$/gm;
const VARIABLE = /^[ \t]*variable(?![\w'])/gm;

/** Offset just past the last non-whitespace character of masked[from, to). */
function trimEnd(masked: string, from: number, to: number): number {
  let e = to;
  while (e > from && /\s/.test(masked[e - 1]!)) e--;
  return e;
}

/** End of the command starting at `at`: the next command start (or EOF), trailing whitespace/comments dropped. */
function commandEnd(masked: string, at: number): number {
  const lineEnd = masked.indexOf('\n', at);
  const rest = lineEnd < 0 ? '' : masked.slice(lineEnd);
  const next = NEXT_COMMAND.exec(rest);
  const to = lineEnd < 0 ? masked.length : next ? lineEnd + next.index : masked.length;
  return trimEnd(masked, at, to);
}

type ScopeEvent =
  | { at: number; kind: 'namespace' | 'section' | 'end'; name: string }
  | { at: number; kind: 'open'; text: string }
  | { at: number; kind: 'notation'; text: string };
// 'notation' events cover every copied scope line (local notation, set_option, variable), kept in file order.

interface Frame {
  kind: 'namespace' | 'section' | 'root';
  names: string[];
  opens: string[];
  notations: string[];
}

function replay(events: ScopeEvent[], at: number): Frame[] {
  const stack: Frame[] = [{ kind: 'root', names: [], opens: [], notations: [] }];
  for (const e of events) {
    if (e.at >= at) break;
    const top = stack[stack.length - 1]!;
    if (e.kind === 'end') { if (stack.length > 1) stack.pop(); }
    else if (e.kind === 'open') top.opens.push(e.text);
    else if (e.kind === 'notation') top.notations.push(e.text);
    else stack.push({ kind: e.kind, names: e.kind === 'namespace' ? splitName(e.name) : [], opens: [], notations: [] });
  }
  return stack;
}

/** Namespace segments in scope at `at`. */
function namespaceAt(events: ScopeEvent[], at: number): string[] {
  return replay(events, at).flatMap((f) => f.names);
}

function findSorryDefs(masked: string, events: ScopeEvent[]): SorryDef[] {
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

function findDefs(text: string, masked: string, comments: Comment[], events: ScopeEvent[], lineOf: (o: number) => number): DefDecl[] {
  const out: DefDecl[] = [];
  for (const m of masked.matchAll(DEF_DECL)) {
    const nameStart = m.index! + m[0].length;
    NAME.lastIndex = nameStart;
    const nm = NAME.exec(masked);
    if (!nm) continue;
    let ownName = nm[0];
    if (ownName.endsWith('.')) ownName = ownName.slice(0, -1);
    const kind = (m[1]!.startsWith('class') ? 'class' : m[1]) as DefKind;
    let start = m.index! + /^\s*/.exec(m[0])![0].length;
    let p = start;
    while (p > 0 && /\s/.test(text[p - 1]!)) p--;
    const doc = comments.find((c) => c.kind === 'doc' && c.end === p);
    if (doc) start = doc.start;
    const end = commandEnd(masked, nameStart);
    let prefix = namespaceAt(events, m.index!);
    let local = ownName;
    if (local.startsWith('_root_.')) { prefix = []; local = local.slice('_root_.'.length); }
    out.push({ fullName: [...prefix, local].join('.'), ownName, kind, text: text.slice(start, end), line: lineOf(start) });
  }
  return out;
}

/** Scope events in file order: namespace/section/end, `open` (not `open … in`) and local notation. */
function scopeEvents(text: string, masked: string): { events: ScopeEvent[]; openIn: Map<number, string[]> } {
  const events: ScopeEvent[] = [];
  for (const m of masked.matchAll(SCOPE_LINE)) {
    events.push({ at: m.index!, kind: m[1] as 'namespace' | 'section' | 'end', name: (m[2] ?? '').trim().split(/\s+/)[0] ?? '' });
  }
  // `open X in` applies to the next command only: map that command's offset to the opens.
  const openIn = new Map<number, string[]>();
  const chains: { at: number; text: string; target: number }[] = [];
  for (const m of masked.matchAll(OPEN_LINE)) {
    const body = m[1]!.trim();
    const inForm = /^(.*?)\s+in(?:\s+(.*))?$/.exec(body);
    if (!inForm) {
      events.push({ at: m.index!, kind: 'open', text: `open ${body.replace(/\s+/g, ' ')}` });
      continue;
    }
    const after = m.index! + m[0].length - (inForm[2] ? inForm[2].length : 0);
    let target = inForm[2] ? after : m.index! + m[0].length;
    while (target < masked.length && /\s/.test(masked[target]!)) target++;
    chains.push({ at: m.index! + /^\s*/.exec(m[0])![0].length, text: `open ${inForm[1]!.replace(/\s+/g, ' ')}`, target });
  }
  // Resolve chains (`open A in open B in theorem …`): each open reaches the first non-open command.
  const byStart = new Map(chains.map((c) => [c.at, c]));
  for (const c of chains) {
    let t = c.target;
    for (let next = byStart.get(t); next; next = byStart.get(t)) t = next.target;
    const list = openIn.get(t) ?? [];
    list.push(c.text);
    openIn.set(t, list);
  }
  for (const m of masked.matchAll(LOCAL_NOTATION)) {
    const start = m.index! + /^\s*/.exec(m[0])![0].length;
    events.push({ at: start, kind: 'notation', text: text.slice(start, commandEnd(masked, start)) });
  }
  for (const m of masked.matchAll(SET_OPTION)) {
    const start = m.index! + /^\s*/.exec(m[0])![0].length;
    events.push({ at: start, kind: 'notation', text: text.slice(start, start + m[0].trim().length) });
  }
  for (const m of masked.matchAll(VARIABLE)) {
    const start = m.index! + /^\s*/.exec(m[0])![0].length;
    const cmd = text.slice(start, commandEnd(masked, start));
    if (/\sin\s*$/.test(masked.slice(start, commandEnd(masked, start)))) continue; // `variable … in` targets one command
    events.push({ at: start, kind: 'notation', text: cmd });
  }
  events.sort((a, b) => a.at - b.at);
  return { events, openIn };
}

/** `open` lines for every namespace enclosing a declaration, outermost first. */
function namespaceOpens(stack: Frame[], ownName: string): string[] {
  const out: string[] = [];
  const path: string[] = [];
  for (const f of stack) {
    for (const n of f.names) {
      path.push(n);
      out.push(`open ${path.join('.')}`);
    }
  }
  // `theorem a.b.c` is elaborated inside namespace `a.b` (Lean expands the dotted name), so those too.
  let segs = splitName(ownName);
  if (segs[0] === '_root_') { path.length = 0; out.length = 0; segs = segs.slice(1); }
  for (const n of segs.slice(0, -1)) {
    path.push(n);
    out.push(`open ${path.join('.')}`);
  }
  return out;
}

export function parseLeanFile(text: string, opts: ParseOptions = {}): ParsedFile {
  const categories = new Set<Category>(opts.categories ?? ['research open']);
  text = text.replace(/\r\n/g, '\n');
  const { masked, comments } = mask(text);
  const lineOf = (offset: number) => text.slice(0, offset).split('\n').length;
  const modDocs = comments.filter((c) => c.kind === 'mod');
  const titleMatch = modDocs.length ? /^#[ \t]+(.+?)[ \t]*$/m.exec(docBody(text, modDocs[0]!)) : null;

  const { events, openIn } = scopeEvents(text, masked);

  // Declarations of the requested categories.
  const found: { attrStart: number; attrEnd: number; category: Category }[] = [];
  for (let i = masked.indexOf('@['); i >= 0; i = masked.indexOf('@[', i + 2)) {
    const end = matchBracket(masked, i + 1);
    const cat = /\bcategory\s+(research\s+open|research\s+solved|textbook)\b/.exec(masked.slice(i, end));
    if (!cat) continue;
    const category = cat[1]!.replace(/\s+/g, ' ') as Category;
    if (categories.has(category)) found.push({ attrStart: i, attrEnd: end, category });
  }

  const decls: OpenDecl[] = [];
  for (const { attrStart, attrEnd, category } of found) {
    const stack = replay(events, attrStart);
    const after = /^\s*(?:(?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*(theorem|lemma)\s+/.exec(masked.slice(attrEnd));
    if (!after && category !== 'research open') continue; // e.g. a textbook or solved `example`: not a problem
    if (!after) throw new Error(`line ${lineOf(attrStart)}: ${category} attribute is not followed by theorem/lemma`);
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

    // The proof runs to the next character in column 0 (upstream proofs are indented).
    const tail = masked.slice(end);
    const stop = COLUMN_ZERO.exec(tail);
    const proofEnd = trimEnd(masked, end, stop ? end + stop.index : masked.length);
    const maskedProof = masked.slice(end, proofEnd);

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

    const context = [
      ...namespaceOpens(stack, ownName),
      ...stack.flatMap((f) => f.opens),
      ...(openIn.get(attrStart) ?? []),
      ...stack.flatMap((f) => f.notations),
    ];

    const ams = /\bAMS((?:\s+\d+)+)/.exec(masked.slice(attrStart, attrEnd));
    decls.push({
      fullName,
      ownName,
      keyword,
      category,
      isPrivate: /\bprivate\b/.test(masked.slice(attrEnd, kw)),
      line: lineOf(kw),
      statement,
      docstring: doc ? docBody(text, doc) : null,
      ams: ams ? ams[1]!.trim().split(/\s+/).map(Number) : [],
      formalProof: /\bformal_proof\s+using\s+\S+\s+at\s+"([^"]+)"/.exec(text.slice(attrStart, attrEnd))?.[1] ?? null,
      moduleDocs: modDocs.filter((c) => c.start < attrStart).map((c) => docBody(text, c)),
      namespace: prefix,
      context: [...new Set(context)],
      proofLines: maskedProof.split('\n').length,
      maskedProof,
    });
  }
  return {
    title: titleMatch ? titleMatch[1]! : null,
    decls,
    sorryDefs: findSorryDefs(masked, events),
    defs: findDefs(text, masked, comments, events, lineOf),
  };
}

/** Dotted identifier tokens of a Lean snippet (comments already irrelevant: statements are code). */
function identifierTokens(statement: string): string[] {
  return statement.match(/(?:«[^»]*»|[A-Za-z_À-˿Ͱ-Ͽἀ-῿℀-⅏])(?:«[^»]*»|[\w'!?.À-˿Ͱ-Ͽἀ-῿₀-ₜ℀-⅏])*/gu) ?? [];
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

/**
 * The local notation lines of `context` that `statement` appears to use: one of the notation's quoted
 * atoms (`"!"`, `"R("`) occurs in the statement text.
 */
export function usedNotation(context: string[], statement: string): string[] {
  return context.filter((line) => {
    if (!line.startsWith('local ')) return false;
    const atoms = [...line.matchAll(/"((?:[^"\\]|\\.)*)"/g)].map((m) => m[1]!.trim()).filter((a) => a !== '');
    return atoms.some((a) => statement.includes(a));
  });
}

/**
 * Definitions of the file whose name occurs in `texts` (the statement, plus the local notation it may
 * use), in file order. A token, or a dotted prefix of it, names a definition when it is the name as
 * written or resolves to the full name through a namespace opened by `context` (which lists the
 * enclosing namespaces too), or is the full name itself. Generalised field notation
 * (`n.left_factorial`) counts when a later segment equals the definition's last segment and no other
 * definition of the file shares that last segment (so the many `….answer` defs do not all match).
 */
export function referencedDefs(context: string[], texts: string[], defs: DefDecl[]): DefDecl[] {
  const opened = [''];
  for (const line of context) {
    const m = /^open\s+(.*)$/.exec(line);
    if (!m) continue;
    for (const w of m[1]!.split(/\s+/)) if (w !== 'scoped' && /^[^()]+$/.test(w)) opened.push(`${w}.`);
  }
  const tokens = texts.flatMap(identifierTokens).map(splitName);
  const last = (name: string) => splitName(name).pop()!;
  const shortCount = new Map<string, number>();
  for (const d of defs) shortCount.set(last(d.fullName), (shortCount.get(last(d.fullName)) ?? 0) + 1);
  return defs.filter((d) => {
    const short = last(d.fullName);
    for (const segs of tokens) {
      for (let n = 1; n <= segs.length; n++) {
        const name = segs.slice(0, n).join('.');
        if (name === d.ownName || opened.some((o) => `${o}${name}` === d.fullName)) return true;
      }
      if (shortCount.get(short) === 1 && segs.slice(1).includes(short)) return true;
    }
    return false;
  });
}
