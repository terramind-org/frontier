# a(40) of A103662: three of the four residue classes of the base are ruled out

## What is shown

The problem asks for a proof that no base `b > 1` makes `b^40` free of the decimal digit 0
(`¬ ∃ b, IsValidZerolessPower 40 b`). This writeup proves the statement for every base `b > 1`
that is odd or divisible by 5. It does **not** settle bases that are even and not divisible by 5,
so the problem stays open. A computer search found no counterexample there for `b ≤ 200000`.

## Argument

Let `b > 1` and `N = b^40`. Then `N ≥ 2^40 > 10^12`, so `N` has more than five digits and any
of its last five digits that is 0 is a non-leading zero.

1. **`10 ∣ b`.** Then `10 ∣ N` and the units digit is 0.
2. **`b` odd, `5 ∤ b`.** Since `b` is odd, `b^2 ≡ 1 (mod 8)`, so `N ≡ 1 (mod 16)`. Since
   `φ(25) = 20 ∣ 40` and `gcd(b, 25) = 1`, `N ≡ 1 (mod 25)`. Hence `N ≡ 1 (mod 100)`, the last
   two digits are `01`, and the tens digit is 0.
3. **`b` odd, `5 ∣ b`.** As above, `N ≡ 1 (mod 16)`, and `5^40 ∣ N`, so `N ≡ 0 (mod 625)`.
   Since `625 ≡ 1 (mod 16)`, the Chinese remainder theorem gives `N ≡ 625 (mod 10^4)`: the last
   four digits are `0625` and the thousands digit is 0.

## What is not shown: `b` even and `5 ∤ b`

Here `N ≡ 0 (mod 2^40)`, so for `k ≤ 40` the last `k` digits of `N` are fixed by `N mod 5^k`.
The 40th powers form a subgroup of size `5^(k-2)` in `(ℤ/5^k)^×` (for `k ≥ 2`), so the number of
possible last-`k`-digit blocks grows like `5^k` and congruences alone cannot force a zero: for
`k = 3` the possible endings are `176, 376, 576, 776, 976`, none with a 0. A heuristic count
(each of the ~`40 log10 b` digits is 0 with probability about 1/10) makes a zeroless `b^40`
extremely unlikely but proves nothing.

Search (`bun`, BigInt): all 80 000 bases `b ≤ 200000` with `b` even and `5 ∤ b` give a `b^40`
containing a 0.

```ts
let n = 0, z = 0;
for (let b = 2n; b <= 200000n; b++) {
  if (b % 2n !== 0n || b % 5n === 0n) continue;
  n++; if (!(b ** 40n).toString().includes("0")) z++;
}
console.log(n, z); // 80000 0
```

## Lean

`partial.lean` in this directory formalises cases 1–3 as
`Scratch.zero_digit_unless_even_coprime_five : ∀ b, 1 < b → (b % 2 = 1 ∨ b % 5 = 0) → 0 ∈ Nat.digits 10 (b ^ 40)`.
It compiles with `lake env lean` against the pinned FormalConjectures and Mathlib (no `sorry`,
no `native_decide`). It is not the problem's `solution` theorem, so Frontier's checker does not
judge it; anyone can rerun it.
