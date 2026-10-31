# Erdős 727, k = 2: a reduction, a necessary condition, and data

## What is shown

The problem asks whether `((n+2)!)^2 ∣ (2n)!` for infinitely many `n`. This writeup does **not**
answer it. It proves, in Lean (`partial.lean`, no `sorry`, axioms `propext`, `Classical.choice`,
`Quot.sound` only):

1. `((n+2)!)^2 ∣ (2n)!  ↔  ((n+1)(n+2))^2 ∣ C(2n, n)` (`Erdos727Partial.reduce`).
2. If `((n+2)!)^2 ∣ (2n)!` then for every prime `p`,
   `2 · v_p((n+1)(n+2)) ≤ ⌊log_p(2n)⌋` (`two_mul_factorization_le_log`).
3. Hence every prime factor `p` of `(n+1)(n+2)` satisfies `p^2 ≤ 2n` (`prime_sq_le`): both
   `n+1` and `n+2` must be `√(2n)`-smooth.

It also reports a computation of all solutions up to `2·10^6`.

## Reasoning

(1) is `(2n)! = C(2n,n)·(n!)^2` and `(n+2)! = n!(n+1)(n+2)`, cancelling `(n!)^2`.
(2) combines (1) with Mathlib's `Nat.factorization_choose_le_log`
(`v_p(C(m,k)) ≤ log_p m`, the Kummer carry bound). (3) follows because a prime factor gives
`v_p ≥ 1`, so `log_p(2n) ≥ 2`.

By Kummer's theorem the exact condition is: for each prime `p` dividing `(n+1)(n+2)`, adding
`n + n` in base `p` has at least `2·v_p((n+1)(n+2))` carries. If `p^a ∥ n+1` the lowest `a`
digits of `n` are `p−1` and give `a` carries, so `a` more carries are needed from the higher
digits; similarly for `n+2`. That is the obstruction: a proof needs an infinite family where
`n+1` and `n+2` are simultaneously smooth *and* have the right high digits for every prime
factor.

## Data

Exact check of the condition (Legendre's formula, every prime of `(n+1)(n+2)`), `n ≤ 2·10^6`:

| range | solutions | proportion |
|---|---|---|
| `n ≤ 10^4` | 55 | 0.55% |
| `n ≤ 10^5` | 913 | 0.91% |
| `n ≤ 10^6` | 11 205 | 1.12% |
| `n ≤ 2·10^6` | 23 760 | 1.19% |

The smallest solution is `n = 208` (`n+1 = 11·19`, `n+2 = 2·3·5·7`); the next are 458, 987,
1220, 1455. The proportion grows over this range, which suggests infinitely many solutions but
proves nothing. The simple families `2^j − 1`, `2^j − 2`, `2^j − 3`, `3^j − 1`, `3^j − 2`,
`3^j − 3` were tested for every `j` with `1 ≤ n < 10^7`: the only solution among them is
`2^12 − 3 = 4093`.

## What is not shown

Infinitude. No family of solutions was found. Families with `n + 2 = p^j` fail outright: `n`
then has only `j` base-`p` digits, giving at most `j < 2j` carries.
