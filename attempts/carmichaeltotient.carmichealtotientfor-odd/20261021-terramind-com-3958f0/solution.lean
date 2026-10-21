import FormalConjectures.Wikipedia.CarmichaelTotient

open CarmichaelTotient
open Nat

namespace OpenProblemsAttempt

-- Replace the placeholder below with your proof.
theorem solution {n : ℕ} (hn : Odd n) : CarmichaelTotientFor n := by
  refine ⟨2 * n, ?_, ?_⟩
  · obtain ⟨k, hk⟩ := hn
    omega
  · have hc : Nat.Coprime 2 n := (Nat.coprime_two_left).mpr hn
    rw [Nat.totient_mul hc, Nat.totient_two, one_mul]

end OpenProblemsAttempt

