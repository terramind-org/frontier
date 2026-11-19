# Two hours of GF(2) flip walks from the rank-93 scheme

The lowest rank reached was 93 over GF(2). The only integer construction validated for the target problem was the published rank-93 baseline. Frontier reports that it ties the best known value. No scheme with 92 or fewer integer terms was found. This writeup is not machine-checked and establishes no lower bound.

## Baseline and conventions

The starting object is the scheme of Jakob Moosbauer and Michael Poole, described in [Flip Graphs with Symmetry and New Matrix Multiplication Schemes](https://arxiv.org/abs/2502.04514). I downloaded its [Maple tensor from the Lille catalogue](https://fmm.univ-lille.fr/5x5x5_tensor.mpl.bz2). The compressed download has SHA-256 `087fcb6c29dbfc3d376536e0a86a316b6f710c7e83ac988db264267a74ca328e`.

`prepare.py` parses the matrix arrays with `ast.literal_eval`; it never executes Maple or downloaded Python. The source uses the trace convention, with tensor coordinates a[i,j], b[j,k], d[k,i]. Frontier stores the output coefficient directly as c[i,k]. The conversion sets c = transpose(d). The resulting `baseline.json` has SHA-256 `c073f10a68e9fbaf0066d4180342b434984fe72cd7b0e135d53db6e016675295`.

The command run from the repository root was:

```sh
bun frontier diagnose .terramind/scratch/matmul5/baseline.json --problem witness.matmul-rank-5x5x5
```

Its result was:

```text
problem:  witness.matmul-rank-5x5x5 (verifier matmul)
value:    93 (best known 93, lower is better)
valid:    yes
result:   ties the best known value
```

The same verifier rejected `broken.json`, which changes the first term's a[0][0] coefficient by 1, reporting 12 incorrect tensor coefficients. The baseline was obtained and validated before any attempt directory was scaffolded. The authors' [public repository](https://github.com/jakobmoosbauer/symmetric-flips) listed `schemes/555m93.txt` and its lift; the files `code/r5-93-1.txt` and `code/r5-93-seeded.txt` were not inspected. No second starting construction was used. The search code here was independently written from the algebraic identities.

## Search

Each factor is a 25-bit unsigned mask. A full scheme has three masks per term. An exact GF(2) checker accumulates all 15,625 tensor coefficients, represented as 625 rows of 25 bits, and compares them with the trace tensor. The initial scheme is the integer baseline reduced modulo 2.

For a shared factor, a flip replaces

```text
(a,b,c), (a,e,f)
```

with

```text
(a,b+e,c), (a,e,f+c).
```

All arithmetic here is over GF(2). The implemented plus-transition replaces arbitrary terms (a,b,c), (d,e,f) with (a+d,b,c), (d,e+b,c), (d,e,f+c). Expanding these tensors shows that their sum is unchanged. The transformations also allow cyclic permutations of factor positions.

Two threads ran concurrently. Worker 0 used unrestricted flips, removed zero terms and cancelling duplicates, and repeatedly combined terms sharing two factors by XORing the third factor. Worker 1 preserved cyclic C3 symmetry. It transformed two disjoint three-element input orbits together, then removed zeros and cancelling duplicates. The paper found its 5x5 rank-93 scheme with C3 alone, starting from the diagonal partition {{1,5},{2,4},{3}}. It used the extra row/column-reversal symmetry only for 6x6. The published scheme reduced mod 2 is C3-invariant (3 fixed terms and 30 full orbits) and is not reversal-invariant.

Fixed terms are excluded from orbit moves, so the C3 walk kept the baseline's 3 fixed terms throughout. Its rank stayed of the form 3k+3: only 93, 96, 99 and 102 occur, in the logs and in a rerun. The next lower rank it could reach was 90, so it could not have produced a scheme with 92 or 91 terms. Only the ordinary walk could have reached 92.

Both workers used a rank cap of 102. Restarts chose the original baseline or the latest state with rank at most 93. Initial seeds were 2026111700 and 2026111701. At restart number r, worker i reseeded its generator with 2026111700 + i + 1000003*r. Counts below include revisits; they are not counts of distinct schemes.

The initial implementation cycled plus-transition periods of 256, 2,048 and 16,384 steps, with restart limits of 100,000, 300,000 and 500,000 steps. The revised implementation added a 256-state tabu history, periods of 1,024, 16,384 and 262,144 steps, and restart limits of 1,000,000, 3,000,000 and 10,000,000 steps. At a tabu dead end it tried a plus-transition before restarting. The reason for the change was to reduce short revisits and try longer walks. No cycle-frequency statistic was collected during the original run; the independent audit's measurements are reported below.

A full tensor check ran every 65,536 search steps, at restarts, before saving any strict improvement, and at normal completion. Each implementation also ran 2,000 transition tests per mode before its search. The recorded controls were:

```text
SELFTEST mode=ordinary baseline=ACCEPT broken=REJECT flips=1894 plus=106 all_transition_tensors=ACCEPT
SELFTEST mode=C3 baseline=ACCEPT broken=REJECT flips=1927 plus=73 all_transition_tensors=ACCEPT
```

All transition and checkpoint checks passed. After completion, `audit.py` independently checked both final masks in Python and accepted them. It also accepted the baseline and rejected a deliberately changed baseline mask.

## Time and measured results

The budget includes the initial three-second smoke search. Its log was created at approximately 16:08:52 UTC on 17 November 2026. The final wrapper exited at 18:08:48 UTC, just under 120 minutes later, including pauses for compilation and relaunching.

The first long segment ran from 16:10:10 to 16:14:09 UTC. It was deliberately terminated with exit status 143 to correct the overall cutoff. The second ran from 16:14:19 to 16:27:19 UTC and was deliberately terminated with exit status 143 to switch search parameters. The final segment ran from 16:27:44 to 18:08:48 UTC, for 6,064 seconds, and exited with status 0. It used `search.cpp`; the earlier source is preserved as `search-v1.cpp`. The earlier segments replayed a deterministic prefix after relaunch, so their counts overlap in search states.

The final segment's exact counters were:

```text
FINISH worker=1 elapsed=6064 best_GF2=93 rank=93 flips=593575320 plus=270781 restarts=128 reductions=270527 tensor_checks=9190 final_tensor=ACCEPT
FINISH worker=0 elapsed=6064.01 best_GF2=93 rank=93 flips=443445962 plus=38286 restarts=95 reductions=38094 tensor_checks=6863 final_tensor=ACCEPT
search_exit_status=0
```

That is 1,037,021,282 flips and 223 restarts in the final segment. Adding the last logged counters from the two interrupted segments gives a lower bound of 1,216,402,434 flips and 822 restarts across the three long segments. Their unlogged tails are omitted. Smoke-test counts are also omitted from this total. The reduction counter includes every event that lowers the current rank, including returns to rank 93.

The independent auditor instrumented separate 180-second reruns from the same baseline. The ordinary walk visited 4,193,637 distinct states in its first 4,194,304 steps (almost only new states), and saw ranks 93 to 96. The C3 walk visited only 1,210,749 distinct states in about 28.3 million steps (about 4.3%) and returned to the start 7,525 times. These are the audit's measurements, not measurements collected during the original run. The C3 worker accounts for about 57% of the final segment's flips, so the headline count of about 1.2 billion flips overstates exploration; it is not a count of distinct states.

The audit also found that 78 of the 93 baseline terms share no factor with any other term, and 66 never changed in any saved state examined (the original run's two final and two checkpoint masks, and the audit's four end states). Walking at rank 93 from this one scheme is near-rigid. This finding concerns that starting scheme and rank, not the flip-graph method as the paper uses it, descending from high-rank diagonal-partition starts.

The best GF(2) rank stayed at 93. Frontier accepted the original integer baseline at rank 93. No lower-rank candidate appeared, so no candidate triggered Hensel lifting or an improvement check with Frontier. A conditional lifting script, `lift.py`, is included for inspection. It solves the full linearized Brent system over GF(2), fixes free variables to zero, and tests centered small integer coefficients after each lift. `lift_selftest.py` checks the linear solver and the Jacobian. Its schoolbook case has zero residual mod 2, so it exercises no lifting step. On the mod-2 reduction of the published rank-93 scheme, which is known to lift to the integers, `lift.py` is consistent at level 1 but inconsistent at modulus 4. With free variables drawn at random (20 seeds) it also failed every time: at modulus 4 (16 seeds), 8 (3) or 16 (1). As written, the lift would very likely not have turned a rank-92 GF(2) scheme into an integer scheme. A cyclic-symmetric lift as in the paper, or a search over free variables, is needed. Rational reconstruction and alternate choices of free variables were not implemented.

The main search processes each had two threads. An early `ps` sample, not retained, showed about 198% CPU and about 2 MB resident memory. Scratch occupied less than 2 MB at completion. Resources were observed without OS-enforced limits. Compilation and a short preflight overlapped the previous two-thread segment during the revision, so a strict two-core ceiling was not enforced during that brief overlap.

## Independent audit

A second model, Claude Opus 5.5, re-verified the integer baseline and its reduction mod 2, reviewed the move code, and ran the ordinary walk from schoolbook 2x2 and 3x3 starts, reaching ranks 7 and 23 respectively. It instrumented separate reruns for distinct states, recounted the original logs, and tested the lift on the published scheme's mod-2 reduction, a case known to lift; the lift failed. Four statements about lifting, symmetry, the cyclic walk's reachable ranks, and resource evidence were corrected accordingly; the repository listing was also clarified. The audit is an opinion backed by reruns, not a check by the repo verifier. This writeup remains not machine-checked.

## Reproduction and limits

All retained local evidence is under:

```text
<scratch>/matmul5/
```

The evidence includes `commands.log`, `sha256.log`, `baseline-diagnose.log`, `broken-diagnose.log`, `selftest.log`, `selftest-v2.log`, `search-segment1.out`, `search-segment2.out`, `search.out`, `audit.log`, `summary.json` and `lift-selftest.log`. The directory also retains the downloads, baseline JSON/masks, checkpoint masks and final masks. Binaries and data dumps are deliberately excluded from this attempt directory.

For a fresh rerun, from the repository root, copy the source files from this attempt into `.terramind/scratch/matmul5/`, download the tensor into its empty `lille/` subdirectory, then run:

```sh
python3 -I .terramind/scratch/matmul5/prepare.py
bun frontier diagnose .terramind/scratch/matmul5/baseline.json --problem witness.matmul-rank-5x5x5
bun frontier diagnose .terramind/scratch/matmul5/broken.json --problem witness.matmul-rank-5x5x5
clang++ -O3 -std=c++17 -pthread .terramind/scratch/matmul5/search.cpp -o .terramind/scratch/matmul5/search-v2
.terramind/scratch/matmul5/search-v2 .terramind/scratch/matmul5/baseline.mask 6064 .terramind/scratch/matmul5
```

`run.sh` records the final segment's actual invocation and exit status. `wait.py` is the macOS event-driven log reader used with the persistent terminal. The first native-shell background launch did not survive shell exit and wrote an empty log; the successful runs used a persistent terminal and were awaited there. Final counters depend on machine load because the stopping condition is wall time.

The result is a failed bounded search. Its cause is unknown. The rank cap, restart pool, retained diagonal structure of the cyclic walk, and parameter choices may have limited exploration. None of those explanations was tested against a competing search design. The run does not rule out rank 92 over GF(2) or over the integers.

## Follow-ups / untried

The independent audit identified the following concrete follow-ups. These were not carried out in this attempt.

- Use a C3 start with the right number of fixed terms: rank 92 needs 3*30 + 2 terms, so a diagonal partition with 2 blocks; rank 91 needs a single block.
- Descend from high-rank diagonal-partition starts as the paper does, with many independent descents.
- Keep the best state of the current run in the restart pool, rather than only states of rank at most 93.
- Apply orbit reductions greedily in C3 mode.
- Replace the lift with a cyclic-symmetric Hensel lift or a search over free variables. Test it first on the baseline's mod-2 reduction, which must succeed.
- Log distinct states and distance from the start.

Further untried options include inspecting `code/r5-93-1.txt` and `code/r5-93-seeded.txt` for more starting schemes, larger intermediate ranks, C3 combined with row/column reversal symmetry, reductions involving larger groups of terms, and walks over GF(3). The short initial schedules alone already consumed two logged segments without lowering rank.
