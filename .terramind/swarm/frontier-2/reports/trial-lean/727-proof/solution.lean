import FormalConjectures.ErdosProblems.«727»

namespace OpenProblemsAttempt

theorem reduce (n : ℕ) :
    (Nat.factorial (n + 2)) ^ 2 ∣ Nat.factorial (2 * n) ↔
      ((n + 1) * (n + 2)) ^ 2 ∣ Nat.choose (2 * n) n := by
  have h1 : Nat.factorial (2 * n) = Nat.choose (2 * n) n * (Nat.factorial n) ^ 2 := by
    have := Nat.choose_mul_factorial_mul_factorial (show n ≤ 2 * n by omega)
    rw [show 2 * n - n = n by omega] at this
    rw [← this]; ring
  have h2 : (Nat.factorial (n + 2)) ^ 2 = ((n + 1) * (n + 2)) ^ 2 * (Nat.factorial n) ^ 2 := by
    rw [Nat.factorial_succ, Nat.factorial_succ]; ring
  rw [h1, h2]
  exact Nat.mul_dvd_mul_iff_right (by positivity)

/-- A necessary condition: every prime factor `p` of `(n+1)(n+2)` has `p ^ 2 ≤ 2 n`. -/
theorem prime_sq_le (n p : ℕ) (hp : p.Prime)
    (hdiv : p ∣ (n + 1) * (n + 2))
    (h : (Nat.factorial (n + 2)) ^ 2 ∣ Nat.factorial (2 * n)) : p ^ 2 ≤ 2 * n := by
  rw [reduce] at h
  have hn : n ≠ 0 := by rintro rfl; norm_num at h
  by_contra hlt
  push Not at hlt
  have hC : Nat.choose (2 * n) n ≠ 0 := (Nat.choose_pos (by omega)).ne'
  -- v_p (choose) ≤ log_p (2n) ≤ 1
  have hlog : Nat.log p (2 * n) < 2 := Nat.log_lt_of_lt_pow (by omega) hlt
  have hle := Nat.factorization_choose_le_log (p := p) (n := 2 * n) (k := n)
  -- v_p (((n+1)(n+2))^2) ≥ 2
  have hpos : (n + 1) * (n + 2) ≠ 0 := by positivity
  have h2 : 2 ≤ (((n + 1) * (n + 2)) ^ 2).factorization p := by
    rw [Nat.factorization_pow]
    simp only [Finsupp.smul_apply, smul_eq_mul]
    have : 1 ≤ ((n + 1) * (n + 2)).factorization p :=
      (hp.dvd_iff_one_le_factorization hpos).1 hdiv
    omega
  have h3 := (Nat.factorization_le_iff_dvd (by positivity) hC).2 h p
  omega
theorem solution : letI k := 2
    Set.Infinite {n : ℕ | (Nat.factorial (n + k)) ^ 2 ∣ Nat.factorial (2 * n)} := by
  show Set.Infinite {n : ℕ | (Nat.factorial (n + 2)) ^ 2 ∣ Nat.factorial (2 * n)}
  simp only [reduce]
  sorry

end OpenProblemsAttempt
