import FormalConjectures.Paper.Kurepa

/-
  Kurepa's conjecture (variant: gcd): a proof of `Kurepa.kurepa_conjecture.variants.gcd`.
  Replace `sorry` with your proof. The statement above `:= by` must not change; the checker
  compares it with the problem's statement. `sorry`, `native_decide` and new `axiom`s are rejected.
-/

namespace OpenProblemsAttempt

theorem solution (n : ℕ) : 2 < n → (n !).gcd (! n) = 2 := by
  sorry

end OpenProblemsAttempt
