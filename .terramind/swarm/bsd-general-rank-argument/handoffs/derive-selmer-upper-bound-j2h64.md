Outcome: done
## Done
- Read the prior swarm notes `iwasawa.md` and `higher-rank.md`; recorded how this analysis sharpens their limitation in `upper.md`.
- Wrote the unconditional Kummer/Selmer corank inequality and audited the conditional cyclotomic Iwasawa route, including the main-conjecture, control/descent, p-adic versus complex vanishing order, and exceptional-zero gaps.
- Checked primary references for Kato, Skinner–Urban, Mazur–Tate–Teitelbaum, and Gross–Zagier/Kolyvagin. Corrected the MTT DOI to `10.1007/BF01388731`.
- No repository test was run: this is a research-note-only change. Committed the note and handoff on the assigned branch.

## Deviations
- The requested new swarm directory contained no prior notes; relevant prior notes existed under `.terramind/swarm/bsd-research-and-formal-attempt/` and were used.
- Did not derive the universal inequality: the source audit isolates the p-adic-to-complex order comparison and universal hypotheses/descent as unproved, which is consistent with the task's required honest treatment of open hypotheses.

## Concerns
- `upper.md` identifies the universal bridge as unproved; it must not be treated as a proof of weak BSD.
- Primary-source applicability depends on exact local conditions and residual-image assumptions; the note avoids claiming a blanket theorem from them.

## Follow-ups
- Audit whether any recent general converse theorem can supply the stated comparison lemma without assuming a rank bound or p-adic BSD input.
- For any concrete application, instantiate the Selmer structure, control maps, local correction factors, and exceptional-zero normalization from the exact theorem used.
