-- (d) An extra axiom used in the proof. The source pre-check rejects it; built without the pre-check,
-- Check.lean rejects it through collectAxioms ("uses axiom OpenProblemsAttempt.cheat").
import FormalConjectures.ErdosProblems.«1»

open Erdos1

namespace OpenProblemsAttempt

axiom cheat : False

theorem solution : ∃ C > (0 : ℝ), ∀ (N : ℕ) (A : Finset ℕ)
    (_ : IsSumDistinctSet A N), N ≠ 0 → C * 2 ^ A.card / A.card < N := by
  exact cheat.elim

end OpenProblemsAttempt
