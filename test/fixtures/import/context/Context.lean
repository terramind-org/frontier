import Mathlib

/-!
# Context fixture
-/

open Filter

namespace Ctx

open scoped Nat

/-- Left factorial (a stand-in). -/
def lf (n : ℕ) : ℕ := n

local notation "!" n => lf n

notation "GLOBAL" => 1
scoped notation "SCOPED" => 2

section Closed
open Real
local notation "gone" => 3
end Closed

/-- A point. -/
structure Pt where
  x : ℕ
  y : ℕ

inductive Col
  | red
  | blue

class Shape (α : Type) where
  area : α → ℕ

@[reducible]
abbrev Big : ℕ := 5

def erdos_9.answer : ℕ := sorry

def erdos_10.answer : ℕ := sorry

def Nat.twice (n : ℕ) : ℕ := 2 * n

open scoped Classical in
/-- Uses an `open … in`, local notation, a structure, field notation and an abbrev. -/
@[category research open]
theorem uses_all (n : ℕ) : (! n) = lf n ∧ (⟨1, 2⟩ : Pt).x = 1 ∧ n.twice = 2 * n ∧ Big = 5 := by
  sorry

open Finset in
@[category research open]
theorem not_this_one : True := by
  sorry

@[category research open]
theorem erdos_9.variants.short : erdos_9.answer = 0 := by
  sorry

namespace Inner.Deep

open Topology

@[category research open]
theorem deep : Col.red ≠ Col.blue := by
  sorry

end Inner.Deep

end Ctx
