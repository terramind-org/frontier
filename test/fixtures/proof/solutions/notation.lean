-- (h) The proof of good.lean with local notation and comments that mention banned words (an axiom,
-- #eval, macro, run_cmd, unsafe): comments are ignored and notation commands are allowed.
import FormalConjectures.ErdosProblems.«1»

open Erdos1

/- A block comment /- nested -/ that says: set_option debug.skipKernelTC true -/
local notation "𝟚" => (2 : ℝ)
local infixl:70 " ⨳ " => fun (a b : ℝ) => a * b

namespace OpenProblemsAttempt

-- Replace the placeholder below with your proof.
theorem solution : ∃ C > (0 : ℝ), ∀ (N : ℕ) (A : Finset ℕ)
    (_ : IsSumDistinctSet A N), N ≠ 0 → C * 2 ^ A.card / A.card < N := by
  refine ⟨1/3, by norm_num, fun N A ⟨hA1, hA2⟩ hN => ?_⟩
  have key : 2 ^ A.card ≤ A.card * N + 1 := by
    rw [← Finset.card_powerset]
    exact (Finset.card_le_card_of_injOn (Finset.sum · id)
      (fun S hS => Finset.mem_range.mpr <| Nat.lt_add_one_of_le <|
        (Finset.sum_le_card_nsmul S id N fun i hi =>
          (Finset.mem_Icc.mp (hA1 (Finset.mem_powerset.mp hS hi))).2).trans
          (Nat.mul_le_mul_right N (Finset.card_le_card (Finset.mem_powerset.mp hS))))
      (fun a ha b hb hab => by
        have := @hA2 ⟨a, ha⟩ ⟨b, hb⟩ hab; simp at this; exact this)).trans_eq
      (Finset.card_range _)
  rcases eq_or_ne A.card 0 with hc | hc
  · simp [hc]; positivity
  · rw [div_lt_iff₀ (Nat.cast_pos.mpr (Nat.pos_of_ne_zero hc))]
    have two : 𝟚 ^ A.card ≤ (1 : ℝ) ⨳ (↑A.card * ↑N + 1) := by
      simp only [one_mul]; exact_mod_cast key
    nlinarith [two,
      show (1 : ℝ) ≤ ↑A.card from by exact_mod_cast Nat.pos_of_ne_zero hc,
      show (1 : ℝ) ≤ (N : ℝ) from by exact_mod_cast Nat.pos_of_ne_zero hN]

end OpenProblemsAttempt
