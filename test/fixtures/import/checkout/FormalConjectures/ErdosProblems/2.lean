/-!
# Erdős Problem 2
-/

namespace Erdos2

@[category research open, AMS 11]
theorem erdos_2 : let N := 5
    N = 5 ∧ ({ val := 1 } : Fin 2) = 1 := by
  decide

/-- Quoted names. -/
@[category research open]
theorem «weird name».«inner» (f : ℕ → ℕ := id) : f = f := by
  rfl

end Erdos2
