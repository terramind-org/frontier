# Handoff: Build the terramind.org Frontier pages (site-pages)

Site worktree: `~/.terramind/worktrees/terramind-org-frontier`, branch `feat/frontier`, based on `origin/main`
(2dbef64). Commits, oldest first: `37371de` (snapshot and sync script), `d1b792f` (loaders, rendering, page
entries, sitemap, share images), `9d3bf20` (the three pages and the home-page row), `614dd37` (FRONTIER_COPY.md).
Nothing pushed, deployed or opened as a PR. The main checkout `~/Terramind/terramind-org` is untouched (clean, still on `rename-to-terramind-labs`).

## Done

Site repo (`feat/frontier`):
- `scripts/sync-frontier.ts` and `package.json` script `sync:frontier`: reads an Index from a path or URL (default `https://github.com/terramind-org/frontier/releases/download/index/index.json`), checks the shape (schema 1, generated_at, repo_commit, sources, problems array with ids/tier/status/lean-or-witness, and that `counts.problems`, `counts.attempts`, `by_tier` and `by_status` match the problems), then writes `data/frontier/index.json`.
- `data/frontier/index.json` (committed, 2.4 MB): built by running `bun frontier index` in the lead's data checkout at 30713fa, then `bun run sync:frontier …/dist/index.json`. Contents: 1,479 problems (1,471 proof, 8 witness), 0 attempts, all open, generated 2026-10-19T02:58:23.746Z. (`bun frontier index` first needed `bun install --frozen-lockfile` in the data checkout, which had no node_modules. That added only the gitignored node_modules/ and dist/.)
- `lib/frontier.ts`: types that mirror the Index schema; helpers `frontierIndex`, `allProblems`, `problemById`, `counts`, `witnessProblems`, `proofProblems`, `isAnswerRequired`, `answerRequiredCount`, `fieldsPresent`, `snapshot` (commit, short form, date, sources), `problemPath`/`idFromPath`, `agentPrompt(id?)` (the exact sentence from design.md), labels for statuses, tiers, fields, kinds and results, and `formatDate` (UTC), `formatNumber`, `plainTitle`.
- `lib/frontier-markdown.ts`: marked plus KaTeX, run on the server at build time. It renders `$…$` and `$$…$$`, both inline and as blocks. Raw HTML in statements is escaped, images become plain links (so nothing loads from another host), and only http(s) links are kept.
- `lib/site.ts`: new keys `frontier` (`org_frontier`), `frontierProblems` (`org_frontier_problems`) and `frontierProblem` (`org_frontier_problem`, url pattern `/frontier/problems/[...id]/`). `pageMetadata(key, page?)` now takes an optional per-page url/title/desc. New `isPattern` and `matchesPage`.
- `app/product-link.tsx`: `?from=` uses an exact address match first, then a pattern match, so problem pages report `org_frontier_problem`.
- `lib/og.tsx`: a pattern address shows its parent (`terramind.org/frontier/problems`) on the share image. `/og/frontier.png`, `/og/frontier-problems.png` and `/og/frontier-problem.png` all return 200.
- `app/sitemap.ts`: pattern entries are skipped and every problem page is added (1,487 `<loc>` in total).
- `app/(site)/frontier/layout.tsx` imports `katex/dist/katex.min.css` (fonts bundled into `/_next/static/media/`) and `frontier.css` (only the classes site.css lacks: `.facts.four`, `.prompt`, `.copy`, `.code`, `.meta`, `.statement`, catalog `.filters`, `.filter-line`, `.row.compact`, `.more`).
- `app/(site)/frontier/copy-button.tsx`: `CopyButton` and `Prompt`. They use `navigator.clipboard` only.
- `/frontier/` (`page.tsx`) has:
  - crumb "Terramind Labs / Project 3", and the h1 "Open problems, *checked.*"
  - a lede whose fields are taken from the data
  - four facts from the counts, plus the snapshot's commit and date
  - the kinds of check, a status table with counts, and the caveats (a checked Lean proof certifies only the formal statement; a record improved is not a record proved best; 167 answer-required problems take writeups only)
  - how to contribute: the sentence with a copy button, and a link to AGENTS.md
  - 8 record rows showing best known and direction
  - Catalog row, and the Code row via `ProjectPublished`
  - sources and credits: formal-conjectures at its pinned commit, we-solve (Mehmet Mars Seven), LLM Hunter, and each record's source on its own page
  - Corrections
- `/frontier/problems/` (`page.tsx` and the client `catalog.tsx`): a compact row array is passed to the client. It has text search (id, title, tags), selects for check, field and status, a "hide answer-required" toggle, and a shown count. Rows render 100 at a time with "Show 100 more". Filters are mirrored into the query string with `history.replaceState`; nothing is stored. The server HTML holds the first 100 rows, and the page is 59 KB gzipped.
- `/frontier/problems/[...id]/page.tsx` uses `generateStaticParams` over every problem and `dynamicParams = false`; an unknown address is a 404. Each page has:
  - title, status, check, field, tags, id and date added
  - the statement as Markdown and KaTeX, with a source and licence line ("not peer-reviewed" on our witness statements)
  - proof tier: the Lean statement, module, declaration and source link at the pinned commit
  - witness tier: goal, best known with its reference and note, checker, and format
  - answer-required: the explanation that only writeups are accepted
  - references; the attempts table, or "No attempts yet."; the agent sentence with a copy button and the show/new/check/submit commands
  - the snapshot line
  - metadata title "<plain title> · Frontier · Terramind Labs"
- Home page: Projects count is 3, with the row "3 · Mathematics / Frontier". The `lib/published.tsx` Code entry `terramind-org/frontier` appears on the home page under Code and on the Frontier page.
- README.md: one bullet on `data/frontier/` and the sync script.
- `FRONTIER_COPY.md`: 93 numbered items, every new sentence verbatim, with where each number comes from. FACTCHECK.md is untouched.

Verified:
- `bun run ts:check`: clean.
- `bun run build`: exit 0. "Generating static pages (1504/1504)": 1,479 problem pages, the Frontier, catalog and other pages, and 9 share images.
- `bun run dev` on port 4317, over curl:
  - 200 for `/`, `/frontier/`, `/frontier/problems/`, a proof problem (`/frontier/problems/abc/abc/`), a witness problem (`/frontier/problems/witness/ramsey-5-5/`) and an answer-required problem (`/frontier/problems/arxiv/0805/3777/ismaxrank-cube/`)
  - 404 for an unknown id
  - 70 sampled problem addresses, including all 8 witness problems: 200 with no redirect
  - The rendered text of the project, witness, proof and answer-required pages reads as intended.
- In the built HTML, the only off-site element that is not an `<a>` is `<link rel="canonical">`. No `<script src>`, `<img>` or CSS `url()` points to another host, and KaTeX fonts are served from `/_next/static/media/`. The URLs inside the JS chunks are library strings (react.dev, w3.org namespaces) and the ProductLink base.
- KaTeX rendered all 1,479 statements and titles, with 5 parse errors across 3 problems (erdos385 parts i and ii, erdos694 variant carmichael). Those are upstream LaTeX that KaTeX does not accept, shown as their source text in muted ink.
- The dev server is stopped.

This worktree: this handoff only (`.terramind/swarm/frontier-2/handoffs/build-the-terramind-org-frontier-8t3xq.md`, plus a copy at `handoffs/site-pages.md`).

## Deviations

- **Base branch**: `origin/main` (2dbef64), not local `main` or `rename-to-terramind-labs`. origin/main contains both: rename-to-terramind-labs is merged there through PR #4, and local `main` is behind. origin/main already has Project 2 (Swarm), so Frontier is **Project 3**, not 2: crumb "Project 3", home label "3 · Mathematics", and the og eyebrow "Project 3 · Frontier".
- **Problem addresses are `/frontier/problems/<id with each "." as "/">/`** (e.g. `/frontier/problems/erdos1/erdos-1/`), not `/frontier/problems/<id>/`. The reason is Next's built-in trailingSlash redirect: it treats any last segment matching `\.\w+` as a file and 308-redirects `…/abc.abc/` to `…/abc.abc`. 473 of 1,479 ids end that way, so they would break the site's every-address-ends-in-`/` rule. The mapping is one-to-one (`problemPath`/`idFromPath` in lib/frontier.ts), and the route is `[...id]`. The agent sentence and commands still use the real id. If the lead prefers the flat form, the alternative is `skipTrailingSlashRedirect` plus hand-written redirects, which changes the whole site.
- **The `frontierProblem` entry in lib/site.ts** has the url pattern `/frontier/problems/[...id]/`. That needed focused patches to product-link.tsx (pattern match for `?from=`), og.tsx (address text) and sitemap.ts (skip the pattern). Without them the entry would share an address with `frontierProblems`, and ProductLink would mislabel the catalog.
- **The frontier repo's Code row comes from `lib/published.tsx`**, not a hand-written row, as the site's AGENTS.md requires. It appears on the home page under Code and on the project page.
- The "Lean-checked problems" fact reads "1,471 with a Lean statement, checked by the Lean proof checker" (`by_tier.proof`). With 0 proof-checked problems, a status count would say little, so the status counts sit in their own table.
- The lede names only the fields present in the snapshot ("mathematics" now). The computer-science witness problems are not in this index yet, and saying "maths and computer science" would not trace to the data. After cs-witness merges, a re-sync makes it read "mathematics and computer science" with no code change.

## Concerns

- **Visual check not done in a browser.** The Nucleus browser panel stayed on `about:blank` because this chat was not on screen: navigate timed out at registration, and screenshots and eval ran against about:blank. The rules forbid driving a separate headless browser, so the 390px viewport and the catalog's filters and "show more" were not exercised in a real browser. The checks were over curl and HTML only. The CSS has 760px breakpoints for the rows, facts, `.meta` and filters, `overflow-x: auto` on pre, tables, display math and statement paragraphs, and `overflow-wrap: anywhere` on titles and the prompt. Someone should open `/frontier/`, `/frontier/problems/` and a problem page at 390px before this goes live.
- **Several links point at things that do not exist yet:** `github.com/terramind-org/frontier` (repo, AGENTS.md, `tree/<commit>`), and the release asset used as the sync default. They work once the repo is published, with the snapshot's commit pushed.
- **Project numbering clash:** the local, unmerged branch `decision-models` in the site repo also calls itself Project 3. Whichever merges second must renumber.
- The committed snapshot is 2.4 MB, and the catalog's HTML is 872 KB uncompressed (59 KB gzipped).
- A witness problem's "Checker" line shows raw parameter names (e.g. `ones_free = 5, zeros_free = 5`). This is accurate but terse.

## Follow-ups

- site-factcheck: check FRONTIER_COPY.md items 1–93 against the evidence listed at its top.
- After cs-witness merges: in the data repo, `bun frontier index`; in the site worktree, `bun run sync:frontier <path>/dist/index.json`, then rebuild. The Field filter, the lede's fields and the record rows update from the data.
- The judge, or a human with the chat on screen, should do the 390px visual pass described under Concerns.
- Optional: the 3 problems with LaTeX KaTeX rejects (erdos385 i/ii, erdos694 variant carmichael) could be fixed upstream in formal-conjectures.
