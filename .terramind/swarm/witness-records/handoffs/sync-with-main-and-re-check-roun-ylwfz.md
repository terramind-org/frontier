## Done

Main merged cleanly without conflicts as `74b631dd3b3b99e85ab55e1c366c37cbee8c6876` (main parent `abaabcbd3fa747c5f333c57a0d1dbecfc04066ed`). Ran `bun install` before and after merging. No attempt files changed. No declarations changed, no attempts submitted, no paid reviews run.

All six titles name a method, budget and unsuccessful outcome. Claims report ties or failures, with no improvement asserted. Every attempt has kind `writeup`, licence `CC-BY-4.0`, both declarations `false`, an author, `claude-fable-5-2` planner, and the required auditor from the other model family. Every listed file exists and every regular file except attempt.yaml is listed.

### sorting-network-size-18

Directory: `attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f`.

Check (exit 0), verbatim:
```text
$ bun src/cli.ts check "attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Validate (exit 1), verbatim:
```text
$ bun src/cli.ts validate "attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f"
attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

Metadata/inventory: writeup; rights=false; disclosure_complete=false; author `claude-sonnet-5-5`; planner `claude-fable-5-2`; auditor `gpt-6.1-sol`. Title has method, budget and failed outcome; claim asserts no improvement. Missing files: none. Unlisted files: none.

Text checks: home-path search and requested personal-name search have no hits. Word search hits, verbatim:
```text
attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/writeup.md:64:A second model (GPT-6.1 Sol) audited this attempt. It reran controls on the SAT encoder: a planted redundant gate was found and removed; an 8-input bubble sort was shortened; the windows of an optimal 8-input network came back UNSAT; and three of the reported windows (`s=69,w=8`; `s=68,w=9`; `s=67,w=10`) were re-solved UNSAT. It also recomputed the single-deletion count (63 for both the record and the saved run-B network). It found the measured results reproducible and several conclusions and runtime statements overstated, and this text was corrected accordingly. The audit is an opinion backed by reruns, not a check by the repository verifier, and no UNSAT proof certificates were kept.
```
All hits use the verb "re-solved" for a computation.

Source files: `scripts/window_sat.py`, `scripts/scan.py`, `scripts/best_from_sh.py`, `scripts/waitloop.sh`.

Licence inspection: No third-party copyright or licence header in included source; no included search implementation visibly copied from a third-party implementation. The two configuration files reflect the external search tool sample settings and record prefixes, as disclosed in the writeup. The external search tool source is not included.

Dry run (exit 1); saved to `.terramind/scratch/judge-r1/dryrun-sorting-network-size-18.txt`. First 40 lines (the entire output is shorter):
```text
$ bun src/cli.ts submit "attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f"
This attempt is not valid, so it will not be submitted:
  attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

### cap-set-f3-8

Directory: `attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa`.

Check (exit 0), verbatim:
```text
$ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Validate (exit 1), verbatim:
```text
$ bun src/cli.ts validate "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

Metadata/inventory: writeup; rights=false; disclosure_complete=false; author `claude-opus-5-5`; planner `claude-fable-5-2`; auditor `gpt-6.1-sol`. Title has method, budget and failed outcome; claim asserts no improvement. Missing files: none. Unlisted files: none.

Text checks: home-path search and requested personal-name search have no hits. Word search hits, verbatim:
```text
attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/writeup.md:57:| run | seed | params | wall clock | steps | successful CP-SAT solves (not proven optimal) | best net gain | largest R re-solved to proven optimality |
```
All hits use the verb "re-solved" for a computation.

Source files: `search/capcore.py`, `search/complete.py`, `search/lns.py`, `search/greedy.py`, `search/run_b.sh`.

Licence inspection: No third-party copyright or licence header in included source. Visible third-party derivation: `search/greedy.py:47-78` implements the published FunSearch priority function with constants exposed as parameters; its docstring at line 48 explicitly says so. Its upstream licence and permission to redistribute this adaptation under the attempt licence are not established by this closing check. Other included scripts have no visible third-party derivation.

Dry run (exit 1); saved to `.terramind/scratch/judge-r1/dryrun-cap-set-f3-8.txt`. First 40 lines (the entire output is shorter):
```text
$ bun src/cli.ts submit "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
This attempt is not valid, so it will not be submitted:
  attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

### superpermutation-7

Directory: `attempts/witness.superpermutation-7/20261117-terramind-com-6e8591`.

Check (exit 0), verbatim:
```text
$ bun src/cli.ts check "attempts/witness.superpermutation-7/20261117-terramind-com-6e8591"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Validate (exit 1), verbatim:
```text
$ bun src/cli.ts validate "attempts/witness.superpermutation-7/20261117-terramind-com-6e8591"
attempts/witness.superpermutation-7/20261117-terramind-com-6e8591/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

Metadata/inventory: writeup; rights=false; disclosure_complete=false; author `claude-opus-5-5`; planner `claude-fable-5-2`; auditor `gpt-6.1-sol`. Title has method, budget and failed outcome; claim asserts no improvement. Missing files: none. Unlisted files: none.

Text checks: home-path search and requested personal-name search have no hits. Word search hits, verbatim:
```text
attempts/witness.superpermutation-7/20261117-terramind-com-6e8591/writeup.md:38:- Both ends of the segment are kept fixed. The segment is re-solved as an ATSP path: the two ends are merged into one node, so a tour equals a path, and the edge weight is 7 − (longest overlap).
attempts/witness.superpermutation-7/20261117-terramind-com-6e8591/selftest.py:64:    print(f'4. n=7 window [{i},{j}]: original cost {orig}, corrupted {bc}, LKH re-solved {nc}, '
```
All hits use the verb "re-solved" for a computation.

Source files: `analyze.py`, `lns_lkh.py`, `kernel_driver.py`, `selftest.py`, `selftest_n5.py`, `selftest_n5_params.py`, `verify_n5.ts`.

Licence inspection: No third-party copyright or licence header or visible copied implementation in the retained scripts. `kernelwalk_search.c` and `build_kernelwalk.py` are both absent. `writeup.md:75-84` describes the excluded generator in prose, identifies its upstream repository and revision, and discloses the AGPL-3.0 derivation. The driver calls external binaries that are not included. No independent upstream source comparison was repeated in this closing check.

Dry run (exit 1); saved to `.terramind/scratch/judge-r1/dryrun-superpermutation-7.txt`. First 40 lines (the entire output is shorter):
```text
$ bun src/cli.ts submit "attempts/witness.superpermutation-7/20261117-terramind-com-6e8591"
This attempt is not valid, so it will not be submitted:
  attempts/witness.superpermutation-7/20261117-terramind-com-6e8591/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

### matmul-rank-5x5x5

Directory: `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b`.

Check (exit 0), verbatim:
```text
$ bun src/cli.ts check "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Validate (exit 1), verbatim:
```text
$ bun src/cli.ts validate "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b"
attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

Metadata/inventory: writeup; rights=false; disclosure_complete=false; author `gpt-6.1-sol`; planner `claude-fable-5-2`; auditor `claude-opus-5-5`. Title has method, budget and failed outcome; claim asserts no improvement. Missing files: none. Unlisted files: none.

Text checks: home-path search and requested personal-name search have no hits. Word search has no hits.

Source files: `search.cpp`, `search-v1.cpp`, `prepare.py`, `mask_to_json.py`, `audit.py`, `lift.py`, `lift_selftest.py`, `run.sh`, `wait.py`.

Licence inspection: No third-party copyright or licence header or visible third-party code derivation in included source. The writeup says the algebraic search implementation was independently written; the published starting scheme is used as input data.

Dry run (exit 1); saved to `.terramind/scratch/judge-r1/dryrun-matmul-rank-5x5x5.txt`. First 40 lines (the entire output is shorter):
```text
$ bun src/cli.ts submit "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b"
This attempt is not valid, so it will not be submitted:
  attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

### kissing-number-11

Directory: `attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f`.

Check (exit 0), verbatim:
```text
$ bun src/cli.ts check "attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Validate (exit 1), verbatim:
```text
$ bun src/cli.ts validate "attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f"
attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

Metadata/inventory: writeup; rights=false; disclosure_complete=false; author `gpt-6.1-sol`; planner `claude-fable-5-2`; auditor `claude-opus-5-5`. Title has method, budget and failed outcome; claim asserts no improvement. Missing files: none. Unlisted files: none.

Text checks: home-path search and requested personal-name search have no hits. Word search has no hits.

Source files: `budget_stop.py`, `dominance.py`, `evidence.py`, `export_best.py`, `integer_pool.py`, `integer_pool_initial.py`, `relax.py`, `relax_high_snapshot.py`, `relax_initial.py`, `search.py`, `structure.py`.

Licence inspection: No third-party copyright or licence header or visible third-party code derivation in included source. The published baseline is referenced as input; external optimization libraries are imported rather than bundled.

Dry run (exit 1); saved to `.terramind/scratch/judge-r1/dryrun-kissing-number-11.txt`. First 40 lines (the entire output is shorter):
```text
$ bun src/cli.ts submit "attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f"
This attempt is not valid, so it will not be submitted:
  attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

### schur-7

Directory: `attempts/witness.schur-7/20261117-terramind-com-c8ca32`.

Check (exit 0), verbatim:
```text
$ bun src/cli.ts check "attempts/witness.schur-7/20261117-terramind-com-c8ca32"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Validate (exit 1), verbatim:
```text
$ bun src/cli.ts validate "attempts/witness.schur-7/20261117-terramind-com-c8ca32"
attempts/witness.schur-7/20261117-terramind-com-c8ca32/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

Metadata/inventory: writeup; rights=false; disclosure_complete=false; author `gpt-6.1-sol`; planner `claude-fable-5-2`; auditor `claude-opus-5-5`. Title has method, budget and failed outcome; claim asserts no improvement. Missing files: none. Unlisted files: none.

Text checks: home-path search and requested personal-name search have no hits. Word search has no hits.

Source files: `audit.py`, `experiments.py`, `extract.py`, `local-v2.cpp`, `local.cpp`, `monitor.py`, `repair-five.py`, `repair-three.py`, `run.sh`, `sat.py`, `selftest.py`, `templates.py`, `variant-controls.py`, `windows.py`, `windows2.py`, `windows3.py`.

Licence inspection: No third-party copyright or licence header or visible third-party code derivation in included source. Scripts extract published construction data and implement the cited mathematical construction; the external solver is imported rather than bundled.

Dry run (exit 1); saved to `.terramind/scratch/judge-r1/dryrun-schur-7.txt`. First 40 lines (the entire output is shorter):
```text
$ bun src/cli.ts submit "attempts/witness.schur-7/20261117-terramind-com-c8ca32"
This attempt is not valid, so it will not be submitted:
  attempts/witness.schur-7/20261117-terramind-com-c8ca32/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

### Whole-tree file checks

Ran `find attempts -type l`, `find attempts -size +1000k`, and a recursive search for verdict.json or review.json. All produced no output. An exact byte-size scan of the six directories found maximum file sizes of 44,990; 12,919; 17,095; 13,267; 11,069; and 11,870 bytes respectively, in the section order above. All files are below 1 MB.

### Full repository gate

Ran `bun run check` once. Type checking passed (the shell advanced from `tsc --noEmit` to tests). Summary, verbatim:
```text
1 tests skipped:
(skip) actionlint > all workflows are clean

 434 pass
 1 skip
 0 fail
 2481 expect() calls
Ran 435 tests across 34 files. [24.52s]
```

Final validation failed only on the six unconfirmed declarations listed in the attempt sections; no other validation findings. Overall exit 1. Full output retained locally at `.terramind/scratch/judge-r1/full-check.txt`. The workflow lint test was skipped; Lean checks were not required because the proof checker and lean/ were not edited by this task.

### Disk report

Read-only snapshot; no files deleted. Filesystem device and mount paths omitted from the df output to keep the handoff free of absolute local paths. Worktree totals include their dependencies and scratch; sizes are not additive where the filesystem shares storage. Numbers came from `df -h .` and `du -sh` on every worktree and its node_modules and .terramind/scratch, where present. Worktree names only:
```text
df -h .
Size    Used   Avail Capacity iused ifree %iused
926Gi   859Gi    19Gi    98%     24M  195M   11%

accurate-marsh: total=135M, node_modules=46M, scratch=absent
adverse-dell: total=133M, node_modules=46M, scratch=absent
allied-fern: total=135M, node_modules=46M, scratch=1.7M
bumpy-quartz: total=169M, node_modules=46M, scratch=37M
cruel-zenith: total=132M, node_modules=46M, scratch=absent
decisive-orchard: total=133M, node_modules=46M, scratch=absent
defeated-canopy: total=285M, node_modules=46M, scratch=153M
definite-haven: total=271M, node_modules=46M, scratch=139M
desperate-plain: total=136M, node_modules=46M, scratch=108K
equal-nectar: total=437M, node_modules=46M, scratch=302M
extraordinary-stone: total=133M, node_modules=46M, scratch=absent
frozen-canyon: total=136M, node_modules=46M, scratch=1.1M
gorgeous-knoll: total=165M, node_modules=46M, scratch=32M
grotesque-beach: total=314M, node_modules=46M, scratch=181M
homeless-peak: total=845M, node_modules=46M, scratch=710M
horrible-fjord: total=246M, node_modules=46M, scratch=113M
inclined-dawn: total=133M, node_modules=46M, scratch=absent
mechanical-haven: total=172M, node_modules=46M, scratch=39M
miniature-woodland: total=133M, node_modules=46M, scratch=absent
novel-shelf: total=174M, node_modules=46M, scratch=39M
parental-glacier: total=180M, node_modules=46M, scratch=48M
popular-quarry: total=133M, node_modules=46M, scratch=absent
provincial-haven: total=3.2G, node_modules=46M, scratch=3.1G
ridiculous-shoal: total=141M, node_modules=46M, scratch=9.0M
suitable-cloud: total=133M, node_modules=46M, scratch=896K
swarm-witness-records: total=87M, node_modules=absent, scratch=absent
tame-aurora: total=298M, node_modules=46M, scratch=163M
watery-shoal: total=405M, node_modules=46M, scratch=270M
```

## Deviations

Both requested handoff paths are written with identical content: `handoffs/judge-round1.md` and `handoffs/sync-with-main-and-re-check-roun-ylwfz.md` under `.terramind/swarm/witness-records/`. Spaces issue lookup and the known parent issue lookup both timed out, so task tracking could not be updated. An inventory read initially ran before the command-capture file existed; it was rerun successfully after capture completed. No requested check was skipped. Dry runs produced declaration blockers instead of plans or PR bodies, as expected.

## Concerns

The cap-set attempt needs a source/licence provenance review of the adapted priority function in `search/greedy.py:47-78` before its rights declaration can be confirmed. This inspection identifies visible derivation; redistribution rights still need review. The other five attempts are ready to show to their owner as honest failed-search records; all six remain blocked from submission pending explicit confirmation of both declarations. The four literal word-search hits are benign uses of "re-solved" and have been reported without editing them. Disk reports 98% capacity and 19 GiB available. The largest listed scratch directory is provincial-haven at 3.1G.

## Follow-ups

Return the cap-set provenance finding to its worker. Identify the exact upstream priority-function source and licence, then establish compatible redistribution terms or remove/rewrite the adaptation under an approved approach. The lead should show the six dry-run blockers and both declarations to the owner and decide any disk cleanup separately. No submission or cleanup was performed.
