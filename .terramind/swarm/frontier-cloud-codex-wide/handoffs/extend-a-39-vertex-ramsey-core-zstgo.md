Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c8` from recovered `c1e85b25`; made no attempt, submission, declaration change, push, PR, or merge.
- Recovered and matched the third McKay fixture (`f7b6530fc32e2544bd0b37fce3a9d605691254db49027f4514d68cd3f5249135`), encoder (`7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`), degree-sequence/color-swap-aware provenance, lexicographic triple ordering, and prior raw result (`e71773e1aa11f7bcc118df2a647469671dd53aa1e91d125a03bad23deaa7333a`). Repeated the exhaustive 262,144-assignment encoder/scanner equivalence and planted 39-to-42 reconstruction controls successfully; control result hash is `a9b475c77bae528df87b369f0d5579358f5adb9f98859d6efac94539fbf8f4ce`.
- Retried only previously unresolved index 3,395 (`[4,16,27]`) under a separately recorded 120-second cap. It was UNSAT in 0.388268077000248 seconds and 1,972 decisions; retry result hash is `87550bc31c0361872f22787d9bcfe90fb7e1d4ac3b75cc60da7fa3df8cc65222`. This does not overwrite the original timeout record.
- Ran only the non-overlapping suffix from index 3,396 on one `taskset -c 0` core for 1,740.033896724999 seconds. It recorded 4,854 UNSAT, 1 timeout, and 0 SAT with 9,722,357 decisions. The timeout is index 8,250 (`[14,16,37]`), which remains unresolved. The first unvisited cursor is 8,251; raw suffix hash is `2dc190ccfb1dece5b662476f6afc96cac7022a2b183be79ab4031d3d975046ad`.
- Combined third-seed coverage: indices 0–8,249 are UNSAT exactly once (including the separate retry at 3,395); index 8,250 is unresolved; indices 8,251–11,479 are unvisited. No candidate arose, so Frontier candidate `diagnose` and `check` were inapplicable. Raw fixtures, controls, scripts, stdout/stderr, and JSON results are retained under `.terramind/swarm/frontier-cloud-codex-wide/`.

## Deviations

- Used the managed foreground shell for the pinned-core run. No visible-terminal launch was used; raw stdout/stderr and exit status 0 were retained.

## Concerns

- This only excludes the tested frozen-39-core/four-insertion family; it does not determine `R(5,5)`.
- Index 8,250 is unresolved, and indices 8,251–11,479 are unvisited; neither category is UNSAT.
- No SAT candidate arose for independent Frontier validation. Declarations remain false and publication remains pending human approval.

## Follow-ups

1. Re-run only index 8,250 with a separately recorded longer cap, then resume at 8,251 using the same fixture and ordering.
2. Validate any SAT candidate with disposable Frontier `diagnose` and `check` before any claim.
3. On exhausting this third seed, pivot only with a recorded color-swap-aware inequivalence certificate and fixture/order hashes.
