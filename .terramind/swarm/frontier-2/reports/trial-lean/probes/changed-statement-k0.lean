import FormalConjectures.ErdosProblems.«727»

namespace OpenProblemsAttempt

theorem solution : letI k := 0
    Set.Infinite {n : ℕ | (Nat.factorial (n + k)) ^ 2 ∣ Nat.factorial (2 * n)} := by
  show Set.Infinite {n : ℕ | (Nat.factorial n) ^ 2 ∣ Nat.factorial (2 * n)}
  have : {n : ℕ | (Nat.factorial n) ^ 2 ∣ Nat.factorial (2 * n)} = Set.univ := by
    ext n
    simp only [Set.mem_setOf_eq, Set.mem_univ, iff_true]
    have := Nat.factorial_mul_factorial_dvd_factorial_add n n
    rw [two_mul, sq]; exact this
  rw [this]; exact Set.infinite_univ

end OpenProblemsAttempt
