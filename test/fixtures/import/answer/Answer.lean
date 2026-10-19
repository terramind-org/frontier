import Mathlib

/-!
# Answer fixtures
-/

namespace AnswerFix

/-- A real definition: no tag. -/
def realBody : ℕ := 3

/-- An unreferenced sorry definition: no tag. -/
noncomputable def unused : ℕ := sorry

def erdos_9.parts.i.answer : Set ℕ := sorry

@[category research open, AMS 11]
theorem erdos_9.parts.i : ∀ n, n ∈ erdos_9.parts.i.answer ↔ n = 0 := by
  sorry

namespace Inner

abbrev guess : ℕ :=
  sorry -- upstream placeholder

@[category research open]
theorem uses_relative : guess = 4 := by
  sorry

@[category research open]
theorem uses_real : AnswerFix.realBody = 3 := by
  sorry

@[category research open]
theorem uses_via_outer : AnswerFix.Inner.guess = 5 := by
  sorry

end Inner

@[category research open]
theorem ignores_unused : (2 : ℕ) = 2 := by
  sorry

@[category research open]
theorem not_a_prefix : guess_other = 1 := by
  sorry

end AnswerFix
