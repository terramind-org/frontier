/-!
# Statements once cut at a binder's `:=` (upstream formal-conjectures @ 197f7f8, Apache-2.0)
-/

namespace Truncated

-- brocard.brocard-conjecture
@[category research open, AMS 11]
theorem brocard_conjecture (n : ℕ) (hn : 1 ≤ n) :
    letI prev := n.nth Nat.Prime;
    letI next := (n+1).nth Nat.Prime;
    4 ≤ ((Ioo (prev^2) (next^2)).filter Nat.Prime).card := by
  sorry

-- erdos1002.erdos-1002
@[category research open, question, AMS 11]
theorem erdos_1002 :
    ∃ g : ℝ → ℝ, Monotone g ∧
    Tendsto g atBot (𝓝 0) ∧
    Tendsto g atTop (𝓝 1) ∧
    letI f :=  fun (α : ℝ) (n : ℕ) ↦
      (1 / log n) * ∑ k ∈ Icc (1 : ℕ) n, (1 / 2 - Int.fract (α * k))
    ∀ c : ℝ, Tendsto (fun (n : ℕ) ↦ (volume { α | α ∈ Ioo (0 : ℝ) 1 ∧ f α n ≤ c }).toReal)
      atTop (𝓝 (g c)) := by
  sorry

-- erdos1139.erdos-1139
@[category research open, question, AMS 11]
theorem erdos_1139 :
    letI u := Nat.nth (fun n ↦ 0 < n ∧ Ω n ≤ 2)
    atTop.limsup (fun k : ℕ ↦ (((u (k + 1) : ℝ) - (u k : ℝ)) / Real.log (↑k + 1) : EReal)) = ⊤ := by
  sorry

-- erdos137.erdos-137.variants.multiple-powerful-factors
@[category research open, AMS 11]
theorem erdos_137.variants.multiple_powerful_factors (k : ℕ) : ∀ᶠ n in Filter.atTop,
    ∀ (m : ℕ) (hm : 0 < m),
    letI N := ∏ x ∈ Finset.Ioc m (m + n), x
    ∃ P : Finset ℕ, P.card = k ∧ ∀ p ∈ P, p.Prime ∧
    p ∣ N ∧ ¬ p ^ 2 ∣ N := by
  sorry

-- erdos317.erdos-317
@[category research open, question, AMS 11]
theorem erdos_317 :
    ∃ c > 0, ∀ n ≥ 1, ∃ δ : Fin n → ℚ,
      Set.range δ ⊆ {-1, 0, 1} ∧
      letI lhs : ℝ := |∑ k, (δ k) / (k + 1)|
      0 < lhs ∧ lhs < c / 2^n := by
  sorry

-- erdos317.erdos-317.variants.claim2
@[category research open, question, AMS 11]
theorem erdos_317.variants.claim2 :
    ∀ᶠ n in atTop, ∀ δ : (Fin n) → ℚ, δ '' Set.univ ⊆ {-1,0,1} →
    letI lhs := |∑ k, ((δ k : ℚ) / (k + 1))|
    lhs ≠ 0 → lhs > 1 / (Icc 1 n).lcm id := by
  sorry

-- erdos477.erdos-477.variants.x-pow-three
@[category research open, AMS 12]
theorem erdos_477.variants.X_pow_three :
    letI f := X ^ 3
    ∀ A : Set ℤ, ∃ z, ¬ ∃! a ∈ A ×ˢ (Set.range f.eval), z = a.1 + a.2 := by
  sorry

-- erdos488.erdos-488
@[category research open, question, AMS 5 11]
theorem erdos_488 : ∀ (A : Finset ℕ), A.Nonempty →
    -- These are needed for the reasons outlined here: https://github.com/google-deepmind/formal-conjectures/pull/256
    0 ∉ A → 1 ∉ A →
    letI B := {n ≥ 1 | ∃ a ∈ A, a ∣ n}
    ∀ᵉ (n : ℕ) (m > n), A.max ≤ n →
      ((Finset.Icc 1 m).filter (· ∈ B)).card / (m : ℚ) <
        2 * ((Finset.Icc 1 n).filter (· ∈ B)).card / n := by
  sorry

-- erdos727.erdos-727.variants.k-2
@[category research open, question, AMS 11]
theorem erdos_727.variants.k_2 :
    letI k := 2
    Set.Infinite {n : ℕ | (Nat.factorial (n + k)) ^ 2 ∣ Nat.factorial (2 * n)} := by
  sorry

-- erdos835.erdos-835.variants.johnson
@[category research open, question, AMS 5]
theorem erdos_835.variants.johnson : ∃ l,
    -- making sure k > 2
    letI k := l + 3
    J(2 * k, k).chromaticNumber = k + 1 := by
  sorry

-- oeisa179537.conjecture4
@[category research open, AMS 11]
theorem conjecture4 (p : ℕ) [Fact p.Prime] (_hp7 : p ≠ 7) :
    letI : Fact (Nat.Prime 7) := ⟨by decide⟩
    (∑ k ∈ Finset.range p, ((42 * (k : ℤ) + 37) * (-1 : ℤ) ^ k * a k)) ≡
      (p : ℤ) * (21 * legendreSym 7 p + 16) [ZMOD (p : ℤ) ^ 2] := by
  sorry

end Truncated
