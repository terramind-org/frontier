Outcome: done

## Done

- Recovered c4 intact: fixture, baseline JSON/metadata, encoder, eight lane JSON/log pairs, smoke result, and original handoff. Its Python cache survived; its PySAT environment did not.
- Read `AGENTS.md`, the catalogue entry, local PR-36 merge `64e896b5`, and fixed-core audit `b89c422f`. The hosted PR thread remains unread because `gh` is unavailable. Fixture: Exoo `r4.6.35`, SHA-256 `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`.
- Revalidated the baseline using Frontier diagnose (valid, 35, tied best known) and a disposable unsubmitted witness scaffold with Frontier check (valid, 35); the scaffold's declarations remained false and it was removed.
- Restored the delete-four/five-reinsert encoder and fixed timeout/checkpoint behavior: per-case Glucose4 interruption, `UNKNOWN` on timeout, atomic JSON checkpoint after every tuple. The asymmetric K4/K6 constraints and controls passed: the 14-variable direct-scanner control covers 16,384 assignments, and planted reconstruction exactly recovers Exoo's graph with no forbidden clique.
- Ran one core for 1,740.021 seconds from cursor 512. `c5-resume-512.json` (SHA-256 `3cd910cce9f7ba303a7ae6f7ab6e632991c6c4853921252fc18d4ce9d0a5b2a6`) records 2,457 tuples, indices 512–2968: UNSAT=2,457, SAT=0, UNKNOWN/timeouts=0, decisions=7,077,094. Raw stdout: `c5-resume-512.log`; first unvisited cursor: 2969; unresolved indices: none.
- No candidate was produced, so candidate diagnose/check was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

- Used the requested one existing cloud checkout and one core. The terminal-pane service failed (`ipcMain.removeListener is not a function`), so the bounded foreground process was waited on directly; no second search process started.
- PySAT was missing from this fresh checkout, so a task-local ignored virtual environment restored `python-sat` 1.9.dev23; it is not staged.
- The c4 handoff's 32,768 assignment control count was stale: 14 variables gives 16,384 assignments; the new emitted control is authoritative.

## Concerns

- Together with c4, only tuples 0–2968 of this one labelled Exoo replacement neighbourhood are excluded. `[2969, 52860)` and other 35-vertex colourings remain.
- No candidate exists to verify. A later SAT model must immediately be put in a disposable scaffold and checked/diagnosed with declarations false.

## Follow-ups

1. Resume exactly at `--start 2969`, retaining fixture hash, lexicographic order, asymmetric clauses and controls.
2. Partition `[2969, 52860)` among the remaining workers without overlap, preserving their JSON/log files and timeout indices.
3. Use `gh` in a future environment to inspect PR-36's hosted discussion before changing neighbourhoods.
