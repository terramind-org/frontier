# An edge-colouring search for R(4,6)

Frontier accepted 35 vertices, tying the known record. The best 36-vertex candidates had 12 forbidden cliques. No candidate above 35 passed the checker.

The target was a complete graph on at least 36 vertices with no colour-0 K₄ and no colour-1 K₆. The known 35-vertex lower-bound construction dates to 2012. The paper reports that adding a vertex to an unusual 34-vertex graph worked after a search that favoured induced four-vertex paths. It found 37 related constructions. A short search starting from those graphs is unlikely to improve a bound that has lasted this long. The survey's revision 18 gives 40 as the upper bound in Table Ib. [2012 paper](https://doi.org/10.37236/2102), [DS1 revision 18](https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS1/pdf/0).

The reference input was the literal matrix in `r4.6.35`, with its colour bits preserved and a zero diagonal. Its SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`. This file has an automorphism group of order two by exhaustive colour refinement with individualization, while the tabulated graph in the paper has a group of order four. The 37-graph collection supplied additional starting graphs. [Downloaded matrix](https://cs.indstate.edu/ge/RAMSEY/r4.6.35), [37-graph collection](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html).

## Calibration

Frontier's `diagnose` accepted the baseline at 35 and rejected a copy with the six edges among vertices 0 through 3 set to colour 0. It counted 40 colour-0 K₄'s and zero colour-1 K₆'s on that copy. The Python and C++ counters agreed on both inputs. The C++ counter also compared the incremental clique and induced-path counts with full recounts across 100 consecutive random flips from each input, with seeds 352602 and 352603.

The unrestricted clique CNF found colourings on 13 vertices for R(3,5), 17 for R(3,6) and R(4,4), and 24 for R(4,5), starting with no supplied colouring. The degree-strengthened CNFs returned UNSAT at 14 vertices for R(3,5) and at 18 for R(4,4). The redundant degree inequalities use two smaller clique Ramsey numbers in each case. Those inequalities alone imply a contradiction at the two orders, so that initial negative control has limited power to test clique encoding.

Full edge-flip annealing found the 17- and 24-vertex controls from random starts with seeds 44017 and 45024. Induced-path annealing did the same with seeds 144017 and 145024. Orbit annealing first missed the 17-vertex control with the single-edge temperature. Scaling the starting temperature by the square root of the mean edge-orbit size made it find the circulant 17 and a 24-vertex colouring with six orbits, using seeds 1717 and 2424. The Gray-code enumerator found the circulant 17 and 24 in 256 and 4,096 assignments respectively. Orbit SAT found 17 in the circulant family and 24 in all five tested controls with one, two, three, four or six equal vertex orbits. Frontier's verifier accepted the positive controls using their respective clique sizes.

## Fixed cores

For each fresh edge `ij`, `x_ij = 1` denotes colour 1. For each potential forbidden clique, the model discards it if its fixed edges include the opposite colour. Otherwise it adds a clause over the fresh edges that forces at least one to take the opposite colour. With one new vertex this is one positive clause per colour-0 triangle and one negative clause per colour-1 K₅. The same construction for two and three added vertices includes the edges between new vertices. Deletion sets in the logs use the zero-based labels of the downloaded matrix.

## Symmetric families

The cycle lengths of one generator specify each cyclic action. Each unordered edge orbit gives one Boolean variable. Every forbidden clique can be mapped to one containing a vertex-orbit representative. SAT models examine such cliques and remove duplicate clauses. Full enumeration uses Gray code on the edge variables. For each colour and forbidden size `k`, it sums the number of `(k−1)`-cliques in the neighbourhood of each representative, weighted by its vertex-orbit size, and divides by `k`. This counts each `k`-clique once. Full graph recounts checked all enumeration incumbents.

For order 36 the regular actions cover the cyclic group and 13 semidirect products. The label `v9` means C₃ × C₃ and `v4` means C₂ × C₂. The products with a normal Sylow 3-subgroup use the actions of C₄ or C₂ × C₂ on C₉ or C₃ × C₃. The two products with a non-normal Sylow 3-subgroup use the order-three action on the normal C₂ × C₂, once with quotient C₉ and once with quotient C₃ × C₃. The group code checks the action relations, closure of the left translations and transitivity. [Classification by order](https://github.com/lixiang90/smallgroups#readme).

The strengthened CNF bounds colour-0 degree by 17 and colour-1 degree by 24. A colour-0 neighbourhood must avoid a colour-0 triangle and a colour-1 K₆. A colour-1 neighbourhood must avoid a colour-0 K₄ and a colour-1 K₅. The bounds follow from R(3,6) = 18 and R(4,5) = 25. The encoding uses the edge-orbit variable once for each incident edge it represents. It also fixes the lexicographically least cyclic rotation of each cross-block word incident to the first block. Each other block can be shifted independently. The final six-block run additionally ordered the internal words of equal-length blocks before canonicalizing the rotations.

## Local moves

The counter stores both colours as bitsets. Flipping `uv` changes the number of forbidden `k`-cliques by the number of `(k−2)`-cliques in the common neighbourhood in the relevant colour. Applying flips sequentially gives the exact change for an orbit move or a pair. Annealing minimizes the weighted sum of forbidden clique counts. Some runs subtract a weight times the count of induced four-vertex paths. Checkpoints rank candidates by the raw number of forbidden cliques.

The first unrestricted batches tried weights 1, 0.55 and 1.7 for colour-1 K₆ and a separate induced-path weight of 0.035. Each batch had eight restarts of three million proposals, or six of 1.5 million when counting paths. The start types were the best star extension then available, a random matrix and the selected current structured checkpoint. The follow-up batches allowed opposite-colour edges sharing a vertex to flip together. Some drew proposed edges from a periodically refreshed list of edges in forbidden cliques. Both versions preserve a chance of proposing any single edge. Reported distinct counts are counts of 128-bit fingerprints of labelled states within a batch. Restart-specific edge distances are Hamming distances from the start of that restart.

## Measured

### Fixed-core searches

Deleting vertex 34 and adding one vertex restored a valid 35 in 38 CaDiCaL conflicts. Frontier's `diagnose` printed `valid: yes` and `ties the best known value` for the returned graph. The control used the same extension encoder as the target runs.

| Removed from the downloaded 35 | Added | Formulas | Edge variables | Clauses per formula | Conflicts per formula | Outcome |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 1 | 1 | 35 | 1,199 | 53 | UNSAT |
| 1 | 2 | 35 | 69 | 3,786 to 3,995 | 97 to 195 | All UNSAT |
| 2 | 3 | 595 | 102 | 7,948 to 9,050 | 165 to 485 | All UNSAT |
| 3 | 4 | 6,545 | 134 | 14,533 to 17,226 | 331 to 1,204 | All UNSAT |

These were all removal sets at each size. The four-vertex extension runs had a 30,000-conflict cap per case. The solver logged each outcome and its statistics in `all-extensions.log` and `results/delete-three.log`. A separate Glucose run emitted DRUP traces for the original core, the core without vertex 0 the core without vertices 0 and 1, and the core without vertices 0, 1 and 2. A reverse-unit-propagation checker derived the empty clause from each trace, with 80, 93, 316 and 729 additions respectively.

Recolouring just the incident edges of a new vertex reached 14 forbidden K₄'s and six forbidden K₆'s with seed 463601. A branch-and-bound optimizer then proved 20 to be the minimum raw count with that core fixed. It visited 1,295,109 nodes and covered 34,359,738,368 star assignments through explicit leaves and pruned subtrees. At a partial assignment it charges every falsified clause and, for each unassigned variable, the smaller of the numbers of positive and negative unit clauses on that variable. This lower bound suffices for pruning because the unit clauses are disjoint across variables. The optimizer rebuilt valid 17- and 24-vertex controls from damaged last stars and agreed with RC2 on a minimum of 12 for a fixed 17-vertex core of an 18-vertex R(4,4) instance.

The 37 published graphs in the Graph6 collection each passed the clique counter at 35. The same fixed-core model returned UNSAT for every one-vertex extension, with 29 to 76 conflicts per graph. Their best sampled last-star assignment had 11 forbidden K₄'s and four forbidden K₆'s. Its run visited 340,335 distinct fingerprints across 4.8 million proposals. Exact optimization of these additional stars was outside this run.

On the raw SAT negative controls, vertex zero in K₁₄ must have at least five colour-0 neighbours or nine colour-1 neighbours. In K₁₈ it must have at least nine neighbours of one colour, and the two colours are interchangeable in R(4,4). Relabelling let the clause encoder test the three cases with only the required incident edges fixed, without the degree-bound clauses. All three were UNSAT. The run logged 1 and 10,994 conflicts for the two K₁₄ branches and 17,192 for K₁₈.

### Bounded SAT repairs

For each of six candidates, the repair script chose 140 distinct sets of four to seven vertices meeting every forbidden clique. The SAT solver could change all edges incident to the selected vertices, plus 0, 16 or 32 sampled extra edges depending on the candidate. Every other edge was fixed. There were 839 UNSAT results and one UNKNOWN at the 10,000-conflict cap. The repair restored deliberately damaged witnesses at 17, 24 and 35 in its controls.

### Complete enumerations

| Family | Assignments | Minimum total | K₄ and K₆ at saved minimum |
| --- | ---: | ---: | --- |
| `n36-circle` | 262,144 | 72 | 0 + 72 |
| `n37-circle` | 262,144 | 111 | 111 + 0 |
| `n37-b2` | 524,288 | 288 | 108 + 180 |
| `g36-c9-c4-invert` | 262,144 | 72 | 36 + 36 |
| `g36-c9-v4-trivial` | 524,288 | 72 | 36 + 36 |
| `g36-v9-c4-trivial` | 262,144 | 96 | 72 + 24 |
| `g36-v9-c4-reflect` | 262,144 | 60 | 36 + 24 |
| `g36-v9-c4-invert` | 262,144 | 108 | 108 + 0 |
| `g36-v9-c4-rotate` | 4,194,304 | 72 | 36 + 36 |
| `g36-v9-v4-trivial` | 524,288 | 108 | 108 + 0 |
| `g36-v9-v4-trivial-reflect` | 2,097,152 | 60 | 36 + 24 |
| `g36-v4-c9` | 524,288 | 63 | 63 + 0 |
| `g36-v4-v9` | 524,288 | 87 | 63 + 24 |
| `g36-v9-v4-two-chars` | 33,554,432 | 45 | 45 + 0 |
| `g36-c9-v4-invert` | 134,217,728 | 72 | 36 + 36 |
| `g36-v9-v4-trivial-invert` | 134,217,728 | 96 | 72 + 24 |

### Additional cyclic actions

| Family | Vertex cycle sizes | Distinct fingerprints by batch | Best total found | Clique SAT | Strengthened SAT |
| --- | --- | --- | ---: | --- | --- |
| `n36-b2` | 18 + 18 | 30,971, 36,439, 9,262, 16,960 | 36 | UNSAT | n/a |
| `n36-b3` | 12 + 12 + 12 | 57,168, 102,480, 41,192, 54,880 | 21 | UNKNOWN | UNSAT |
| `n36-b4` | 4 × 9 | 92,259, 196,087, 84,745, 124,799 | 18 | UNKNOWN | UNSAT |
| `n36-b6` | 6 × 6 | 227,085, 393,613, 189,026, 222,764 | 21 | UNKNOWN | UNKNOWN |
| `n37-b3` | 18 + 18 + 1 | 11,432, 28,868, 1,818, 6,025 | 63 | UNSAT | n/a |
| `n37-b4` | 12 + 12 + 12 + 1 | 36,139, 87,656, 28,853, 43,482 | 47 | UNSAT | UNSAT |
| `n37-b6` | 4 × 8 + 4 + 1 | 111,454, 190,450, 76,543, 123,499 | 24 | UNKNOWN | UNSAT |

All the complete enumerations also returned UNSAT in the separate orbit SAT encoding. The second table records four annealing batches per remaining family, in order of colour-1 weights 1, 0.6, 1.6 and 1. Counts are per batch and can overlap. Those minima describe sampled graphs. The SAT columns describe only zero-violation feasibility. The 36-vertex six-block case stayed UNKNOWN after ordering the equal-length blocks, at 1,000,001 solver conflicts.

The 37-vertex two-block case uses a 36-cycle and one fixed vertex. Other cycle partitions with the same numbers of orbits were outside this sweep. Frontier's checker agreed with the logged count on each of the 16 fully enumerated families' saved minima. The best 37-vertex candidate overall had 20 forbidden K₄'s and four forbidden K₆'s. It came from the six-block annealing and failed `diagnose`.

### Unrestricted starts at 36

| Start type | Batches started | Largest per-batch count of distinct fingerprints | Best raw count | K₄ and K₆ at that count |
| --- | ---: | ---: | ---: | --- |
| Best fixed-core extension of the downloaded graph | 10 | 3,467,534 | 18 | 16 + 2 |
| Random | 10 | 3,909,547 | 30 | 15 + 15 |
| Structured | 8 | 3,423,799 | 18 | 18 + 0 |

The fixed-core starting graph reached 18 at 21:30:07 UTC one edge from the restart input in the induced-path batch. The recorded 30 from a random start was at 21:37:12 UTC, 298 edge colours from its restart's input. A completed random batch also reached 30. The structured minimum was the 18 of the selected four-block input itself. The unrestricted lane interrupted its final random batch at 21:37:15 UTC to spend the core on other neighbourhoods. Its last checkpoints survive in scratch.

The order-two orbit run on the downloaded record started with an all-zero new star and allowed all edge orbits to change. It had seed 4636035 and reached 12 colour-0 K₄'s and zero colour-1 K₆'s at 21:39:01 UTC, in restart 2. It logged 134,731 distinct fingerprints over 24 million proposals. The saved matrix differs from the original in 36 edges between old vertices. Frontier's `diagnose` rejected it with 12 violations. Follow-up unrestricted refinement from 12 labelled inputs tried 48 batches at lower temperatures, allowing guided moves and paired flips. Those runs matched 12. One catalogue start reached the same total with ten K₄'s and two K₆'s. The largest distinct count in a refinement batch was 107,340.

The repair-and-grow sweep made 74 perturbations of the 35-vertex catalogue graphs, using seeds 4662000 through 4662073. It recovered 23 valid graphs, all colour-preserving isomorphic to a graph in the input collection. The positive controls recovered the damaged 17- and 24-vertex graphs. No new class entered the extension stage.

### Other symmetry seeds and run time

Eight inputs from the catalogue with an order-two generator were each extended by a fixed new vertex, then annealed with all of that generator's edge orbits mutable. All eight reached 12 colour-0 K₄'s and zero colour-1 K₆'s. The peak distinct count was 106,921 in one batch. A separate run preserved the full order-four group of catalogue graph 36. It reached 24 colour-0 K₄'s and three colour-1 K₆'s, with 728 distinct fingerprints in 24 million proposals.

The search clock ran from 21:23:17 to 22:05:16 UTC on 17 November 2026, 41 minutes and 59 seconds within the 120-minute cap. The two search lanes each ran one search process at a time. The structured lane ran 21:28:58 to 21:55:45, and the main unrestricted lane 21:28:59 to 21:37:15. The catalogue starts, refinement and SAT repairs ended at 21:56:48. The 35-vertex regrowth sweep ended at 21:59:24, the ordered six-block rerun at 22:01:38, the full-group trial at 22:03:31 and the catalogue symmetry runs at 22:05:16.

The initial RC2 minimization was stopped with exit 143 so the exact extension cases could run first. Branch and bound supplied the minimum later. The unrestricted lane exited 130 when interrupted to switch to targeted searches. The final structured, supplemental, regrowth, ordered-block and group runs reported exit 0. For capped SAT calls, the per-case solver status records UNKNOWN independently of the process exit. Scratch contains the UTC logs, solver statistics, seeds, start and end records, saved candidates and the four sampled DRUP traces.

## Reproduction

The source in `search/` is original to this attempt. The two downloaded graph files, binaries, certificates and logs stay in scratch. The second input has SHA-256 `89a39d9cccb6a538e8d71d8e82abf84030ff9cde400727291b978fbad0003fc3`.

Copy the sources to `.terramind/scratch/ramsey46-replay/` and run from that directory. Put the downloads in separate input directories.

```sh
mkdir -p input input-mckay
curl -fsSL https://cs.indstate.edu/ge/RAMSEY/r4.6.35 -o input/r4.6.35
curl -fsSL https://users.cecs.anu.edu.au/~bdm/data/r46_35some.g6 -o input-mckay/r46_35some.g6
UV_CACHE_DIR="$PWD/uv-cache" uv venv --python python3.12 venv
UV_CACHE_DIR="$PWD/uv-cache" uv pip install --python venv/bin/python 'python-sat==1.9.dev22'
clang++ -std=c++20 -O3 -Wall -Wextra -Werror ramsey.cpp -o ramsey
venv/bin/python -I search.py baseline
./ramsey check 35 4 6 baseline.json 352602 100
./ramsey check 35 4 6 broken.json 352603 100
venv/bin/python -I search.py controls
venv/bin/python -I search.py raw-negative-controls
venv/bin/python -I search.py extend-three
venv/bin/python neighborhoods.py proof-controls
venv/bin/python orbits.py maps
```

From the repository root, run `bun frontier diagnose .terramind/scratch/ramsey46-replay/baseline.json --problem witness.ramsey-4-6`. The bitset control parameters, launch configurations and time limits are in the search scripts and the logs. `campaign.py` takes an ISO-8601 UTC deadline. The structured and unrestricted lanes can run concurrently. The unrestricted lane selects then-current structured checkpoints, so the exact starts it selects can vary with scheduling. `supplemental.py`, `star.py`, `canonical.py`, `automorphisms.py` and `grow.py` run the follow-up experiments.

## Inferred

A 36-vertex colouring cannot contain a 32-vertex induced sub-colouring of this particular 35, if the fixed-core encoding and solver results are correct. The separately enumerated minima rule out the listed regular actions and the stated circulant and fixed-point families. The larger block actions with unresolved SAT status and the broader 36-vertex space remain open to search.

Forbidden-clique counts describe the candidates and their search objectives. The edit distance from any of these candidates to a valid colouring remains unknown. A different direction would generate 34-vertex colourings with unusually high induced-path counts and low colour-1 K₄ counts, then test two-vertex extensions. That follows the successful construction's route through a different 34-vertex starting class.
