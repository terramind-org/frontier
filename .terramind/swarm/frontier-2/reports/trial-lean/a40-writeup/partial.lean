import FormalConjectures.OEIS.«103662»

open Nat

namespace Scratch

/-- A zero digit (not the leading one) appears in base 10. -/
theorem zero_mem_digits_of {N k : ℕ} (hk : N / 10 ^ k % 10 = 0) (hN : 10 ^ (k + 1) ≤ N) :
    0 ∈ Nat.digits 10 N := by
  induction k generalizing N with
  | zero =>
    have hpos : 0 < N := by omega
    rw [Nat.digits_def' (by norm_num) hpos]
    simp at hk
    simp [hk]
  | succ k ih =>
    have hpos : 0 < N := lt_of_lt_of_le (by positivity) hN
    rw [Nat.digits_def' (by norm_num) hpos]
    apply List.mem_cons_of_mem
    apply ih
    · rw [Nat.div_div_eq_div_mul, ← pow_succ']; exact hk
    · rw [Nat.le_div_iff_mul_le (by norm_num), ← pow_succ]; exact hN

theorem pow40_mod16_of_odd {c : ℕ} (hc : c % 2 = 1) : c ^ 40 % 16 = 1 := by
  rw [Nat.pow_mod]
  have : c % 16 < 16 := Nat.mod_lt _ (by norm_num)
  have h2 : c % 16 % 2 = 1 := by omega
  generalize c % 16 = r at this h2
  interval_cases r <;> simp_all

theorem pow40_mod25 {c : ℕ} (hc : c % 5 ≠ 0) : c ^ 40 % 25 = 1 := by
  rw [Nat.pow_mod]
  have : c % 25 < 25 := Nat.mod_lt _ (by norm_num)
  have h2 : c % 25 % 5 ≠ 0 := by omega
  generalize c % 25 = r at this h2
  interval_cases r <;> simp_all

theorem big {b : ℕ} (hb : 1 < b) : 10 ^ 5 ≤ b ^ 40 :=
  calc 10 ^ 5 ≤ 2 ^ 40 := by norm_num
    _ ≤ b ^ 40 := Nat.pow_le_pow_left hb 40

/-- Every base `b > 1` that is odd or divisible by 5 has a zero digit in `b ^ 40`. -/
theorem zero_digit_unless_even_coprime_five (b : ℕ) (hb : 1 < b) (h : b % 2 = 1 ∨ b % 5 = 0) :
    0 ∈ Nat.digits 10 (b ^ 40) := by
  have hbig := big hb
  by_cases h5 : b % 5 = 0
  · by_cases h2 : b % 2 = 0
    · -- 10 ∣ b: the units digit is 0
      apply zero_mem_digits_of (k := 0) _ (by omega)
      have : 10 ∣ b := by omega
      have : 10 ∣ b ^ 40 := dvd_pow this (by norm_num)
      simpa using Nat.mod_eq_zero_of_dvd this
    · -- b odd, 5 ∣ b: b ^ 40 ≡ 625 (mod 10^4), so the thousands digit is 0
      obtain ⟨c, rfl⟩ : 5 ∣ b := Nat.dvd_of_mod_eq_zero h5
      have hc : c % 2 = 1 := by omega
      have h16 : (5 * c) ^ 40 % 16 = 1 := pow40_mod16_of_odd (by omega)
      have h625 : (5 * c) ^ 40 % 625 = 0 := by
        apply Nat.mod_eq_zero_of_dvd
        rw [mul_pow]; exact dvd_mul_of_dvd_left (by norm_num) _
      apply zero_mem_digits_of (k := 3) _ _
      · omega
      · -- need 10^4 ≤ N
        have : (2:ℕ) ^ 40 ≤ (5 * c) ^ 40 := Nat.pow_le_pow_left hb 40
        have : 10 ^ (3 + 1) ≤ (2:ℕ) ^ 40 := by norm_num
        omega
  · -- b odd, 5 ∤ b: b ^ 40 ≡ 1 (mod 100), so the tens digit is 0
    have h2 : b % 2 = 1 := by omega
    have h16 := pow40_mod16_of_odd h2
    have h25 := pow40_mod25 h5
    apply zero_mem_digits_of (k := 1) _ (by omega)
    omega

end Scratch
