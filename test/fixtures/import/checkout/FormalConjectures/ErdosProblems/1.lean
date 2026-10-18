/-
Copyright 2025 The Formal Conjectures Authors.
-/
module

public import FormalConjecturesUtil

/-!
# Erdős Problem 1

*Reference:* [erdosproblems.com/1](https://www.erdosproblems.com/1)
See also [a paper](https://example.org/paper_(v2)) and the same link again
[duplicate](https://www.erdosproblems.com/1).
-/

@[expose] public section

open Filter

namespace Erdos1

/-- A helper -- not a problem. -/
abbrev Helper : Prop := True

/--
This one is solved: it must be skipped. See [x](https://example.org/solved).
-/
@[category research solved, AMS 5 11, formal_proof using lean4 at
  "https://github.com/example/erdos1/blob/0e39/Erdos1.lean#L2419"]
theorem erdos_1 : ¬ ∃ C > (0 : ℝ), C = 0 := by
  sorry

/--
The main open statement, with $x \le y$ in LaTeX.
Quote: "a := b" inside a docstring.
-/
@[category research open, AMS 5 11]
theorem erdos_1.open_main : ∃ C > (0 : ℝ), C * 2 = 3 := by
  sorry

/-- A weaker variant. -/
@[category research open, AMS 5 11, formal_proof using lean4 at
  "https://example.org/a[1]/proof"]
theorem erdos_1.variants.weaker : ∀ n : ℕ, n = n := by
  rfl

namespace Inner.Deeper

/-- Nested dotted namespace. -/
@[category research open, AMS 11 5]
lemma deep_lemma (n : ℕ) (h : n = (n : ℕ) := rfl) : n = n :=
  rfl

end Inner.Deeper

section Helpers

-- TODO: formalise the known cases
/--
Docstring separated from the attribute by a comment.
-/
-- a note: ignore me
@[category research open, AMS 11]
theorem after_section : True := trivial

end Helpers

end Erdos1
