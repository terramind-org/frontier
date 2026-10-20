/**
 * The practice set: upstream `@[category textbook]` declarations imported so an agent can run the
 * whole loop (scaffold, prove, check, `verified`) on something provable. They are tagged `practice`,
 * carry `upstream_status: textbook` and `difficulty.level: practice`, and never count as open problems.
 *
 * How the list was chosen (formal-conjectures @ 197f7f8dcc457f556754f826389d2ec7a0d85b92):
 * 1. Every `category textbook` theorem/lemma (218 parsed) that is not `private`, whose upstream proof
 *    has no `sorry`, `admit` or `native_decide`, is at most 40 lines long, and whose statement does
 *    not use an upstream `sorry` definition: 99 candidates (54 ErdosProblems, 22 Wikipedia, 10 OEIS, 13 other).
 * 2. From those, by hand: `Erdos1.erdos_1.variants.weaker` (the warm-up named in the cycle-3 design),
 *    then a spread over sources (Erdős, Wikipedia, OEIS, Green, Hilbert, Millennium, Paper, Books),
 *    over subjects (number theory, graphs, combinatorics, analysis, complexity) and over effort
 *    (a few `decide`-sized finite checks, most a short argument), skipping declarations whose
 *    statement leans on file-level `variable`s, `private` declarations (the checker looks the name up),
 *    and near-duplicates of an entry already chosen.
 * 3. Removed on 21 Oct 2026: `ComplexityTheory.P_subset_coNP`. Its own proof has no `sorry`, but it calls
 *    `coP_eq_P` and `P_subset_NP`, which do (found by the site fact-check). Rule 1 only inspects the
 *    declaration's own proof, so check the lemmas a candidate's proof calls before adding one by hand.
 *
 * The importer re-checks rule 1 for each entry at import time and fails if one no longer holds.
 * Only statements are imported; upstream proofs are never copied into this repository.
 */
export interface PracticeEntry {
  /** File in the formal-conjectures checkout. */
  path: string;
  /** Full Lean name of the `textbook` declaration. */
  decl: string;
  /** One line for `show`/`pick`: what kind of exercise this is. Our own words. */
  note: string;
}

/** Upper bound on the upstream proof length, in lines, for a practice problem. */
export const PRACTICE_MAX_PROOF_LINES = 40;

/** Tokens that disqualify an upstream proof (checked with comments and strings masked). */
export const PRACTICE_BANNED = /\b(?:sorry|admit|native_decide)\b|\bdecide\s*\+\s*native\b|\bofReduceBool\b/;

export const PRACTICE: readonly PracticeEntry[] = [
  {
    path: 'FormalConjectures/ErdosProblems/1.lean',
    decl: 'Erdos1.erdos_1.variants.weaker',
    note: 'Practice: a counting bound for sum-distinct sets (pigeonhole on subset sums); upstream proves it in under 20 lines.',
  },
  {
    path: 'FormalConjectures/ErdosProblems/44.lean',
    decl: 'Erdos44.example_sidon_set',
    note: 'Practice: check that a five-element set is Sidon; a finite computation.',
  },
  {
    path: 'FormalConjectures/ErdosProblems/317.lean',
    decl: 'Erdos317.erdos_317.variants.counterexample',
    note: 'Practice: a claimed lower bound fails for n = 4; exhibit the signs that break it.',
  },
  {
    path: 'FormalConjectures/ErdosProblems/364.lean',
    decl: 'Erdos364.erdos_364.variants.weak',
    note: 'Practice: no four consecutive powerful numbers; an argument modulo 4.',
  },
  {
    path: 'FormalConjectures/ErdosProblems/470.lean',
    decl: 'Erdos470.erdos_470.variants.smallest_weird_eq_70',
    note: 'Practice: 70 is the smallest weird number; a bounded check over divisors.',
  },
  {
    path: 'FormalConjectures/ErdosProblems/595.lean',
    decl: 'Erdos595.erdos_595.variants.K4_not_cliqueFree',
    note: 'Practice: the complete graph on 4 vertices contains a 4-clique; unfold the definitions.',
  },
  {
    path: 'FormalConjectures/Wikipedia/AgohGiuga.lean',
    decl: 'AgohGiuga.squarefree_of_isCarmichael',
    note: 'Practice: Carmichael numbers are squarefree; a short Mathlib argument.',
  },
  {
    path: 'FormalConjectures/Wikipedia/Selfridge.lean',
    decl: 'Selfridge.selfridge_conjecture.variants.pseudo_counterexample',
    note: 'Practice: 6601 passes the test, is not prime and is 1 mod 5; a finite computation.',
  },
  {
    path: 'FormalConjectures/Wikipedia/Oppermann.lean',
    decl: 'Oppermann.oppermann_implies_legendre',
    note: "Practice: derive Legendre's conjecture from Oppermann's for one n; interval bookkeeping.",
  },
  {
    path: 'FormalConjectures/Wikipedia/CarmichaelTotient.lean',
    decl: 'CarmichaelTotient.carmichealTotientFor_odd',
    note: "Practice: Carmichael's totient conjecture holds for odd n (2n has the same totient).",
  },
  {
    path: 'FormalConjectures/OEIS/4290.lean',
    decl: 'OeisA4290.a_ten_pow',
    note: 'Practice: the least 0/1-digit multiple of 10^k is 10^k itself; an argument about an infimum.',
  },
  {
    path: 'FormalConjectures/OEIS/38771.lean',
    decl: 'OeisA38771.a_n_exists',
    note: 'Practice: the sequence is well defined (some composite c makes primorial(n) + c prime); uses infinitely many primes.',
  },
  {
    path: 'FormalConjectures/GreensOpenProblems/72.lean',
    decl: 'Green72.allowedSetSize_le',
    note: 'Practice: at most (k - 1) N grid points with no k on a line; pigeonhole over rows.',
  },
  {
    path: 'FormalConjectures/HilbertProblems/17.lean',
    decl: 'Hilbert17.f_nonneg',
    note: 'Practice: the Motzkin polynomial is nonnegative; an AM-GM style inequality.',
  },
  {
    path: 'FormalConjectures/Paper/Kurepa.lean',
    decl: 'Kurepa.kurepa_conjecture.prime_reduction',
    note: "Practice: Kurepa's conjecture reduces to primes; uses the file's local `!` notation.",
  },
  {
    path: 'FormalConjectures/Books/UniformDistributionOfSequences/Equidistribution.lean',
    decl: 'Equidistribution.isAccumulationPoint_exists_subsequence_tendsto',
    note: 'Practice: an accumulation point is the limit of a subsequence; a topology exercise.',
  },
];
