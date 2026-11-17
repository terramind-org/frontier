# Security

Report security problems privately to contact@terramind.com, not in a public issue or pull request. Say what you found, how to reproduce it, and what it affects. Terramind will reply, fix it, and credit you in the fix unless you ask not to be named.

In scope:

- A way to get an attempt a `verified` verdict it should not have: a Lean proof the checker accepts that uses `sorry`, an axiom outside `propext`, `Classical.choice` and `Quot.sound`, or a statement of a different type; or a witness the verifier accepts that is not valid.
- A way for a pull request to run code with secrets or a write token, write to `main`, poison the Lean cache that `lean-check.yml` restores, or get merged by `automerge.yml` with files other than one new attempt directory.
- A way to make the AI review of a writeup spend more than `review.config.json` allows, or to read the model API keys.
- A secret or private data committed to this repository.

A wrong or misleading problem statement is not a security problem: open an issue (see CONTRIBUTING.md).
