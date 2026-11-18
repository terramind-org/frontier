# r8 checkpointed deterministic continuation

This continuation resumes the 12-anchor mixed-slice search at seed 165. Each
seed is a separate one-core invocation, so every completed outcome has an
independent durable checkpoint in `seed-<n>/ledger.json` before the next seed
is started. The scope is fixed at 264 frozen points and 813 optionals, with
248 planted selected optionals and target 249.

The strict screen is integer-only: `125 * eligible > 60 * deletions`. Before
a solve, each fingerprint is checked against r1--r7 and all earlier completed
r8 seeds. An UNSAT result therefore concerns only its recorded frozen
assignment; it is not a claim about the unrestricted 813-optional pool.

Inputs and evaluator hashes:

- fixture: `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`
- mixed-pool screen: `7ed2e8b2a4caec32f242a60d461f2d41df706df5ba8d23109997c88d17260bac`
- evaluator: `171732ef571287fa4e783c2ebb65d76deab3ed446184e4bb40ff60242af34e13`

The fixture was directly scanned and accepted by Frontier diagnose at 512.
All solved r8 cases passed their planted assignment, 256-assignment
direct-versus-encoding control (zero mismatches), and the positive-gain toy
control. No candidate file was generated. The next unvisited seed is 173.

