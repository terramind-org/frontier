import FormalConjectures.ErdosProblems.«727»

/-!
Partial results towards `Erdos727.erdos_727.variants.k_2`. Not the problem's `solution`
theorem; compile with `lake env lean` against the pinned FormalConjectures.
-/

namespace Erdos727Partial

/-- `((n+2)!)^2 ∣ (2n)!` iff `((n+1)(n+2))^2 ∣ C(2n, n)`. -/
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

/-- Necessary condition: for every prime `p`, `2 · v_p((n+1)(n+2)) ≤ log_p (2n)`. -/
theorem two_mul_factorization_le_log (n p : ℕ)
    (h : (Nat.factorial (n + 2)) ^ 2 ∣ Nat.factorial (2 * n)) :
    2 * ((n + 1) * (n + 2)).factorization p ≤ Nat.log p (2 * n) := by
  rw [reduce] at h
  have hC : Nat.choose (2 * n) n ≠ 0 := (Nat.choose_pos (by omega)).ne'
  have hle := Nat.factorization_choose_le_log (p := p) (n := 2 * n) (k := n)
  have h3 := (Nat.factorization_le_iff_dvd (by positivity) hC).2 h p
  rw [Nat.factorization_pow] at h3
  simp only [Finsupp.smul_apply, smul_eq_mul] at h3
  omega

/-- In particular every prime factor `p` of `(n+1)(n+2)` has `p ^ 2 ≤ 2 n`. -/
theorem prime_sq_le (n p : ℕ) (hp : p.Prime)
    (hdiv : p ∣ (n + 1) * (n + 2))
    (h : (Nat.factorial (n + 2)) ^ 2 ∣ Nat.factorial (2 * n)) : p ^ 2 ≤ 2 * n := by
  have hn : n ≠ 0 := by rintro rfl; norm_num at h
  have hpos : (n + 1) * (n + 2) ≠ 0 := by positivity
  have h1 : 1 ≤ ((n + 1) * (n + 2)).factorization p :=
    (hp.dvd_iff_one_le_factorization hpos).1 hdiv
  have h2 := two_mul_factorization_le_log n p h
  have hlog : 2 ≤ Nat.log p (2 * n) := by omega
  calc p ^ 2 ≤ p ^ Nat.log p (2 * n) := Nat.pow_le_pow_right hp.pos hlog
    _ ≤ 2 * n := Nat.pow_log_le_self p (by omega)

end Erdos727Partial
