# Prior-art check for C(13,7,4)

## Prior art

On 2026-11-17 UTC, the search covered the [La Jolla final dataset v1.2](https://doi.org/10.5281/zenodo.19735294), the historical entry and its successor, and indexed arXiv, Zenodo, OEIS and general web results for `C(13,7,4)`, 29-block covers and improved lower bounds. The archived `coverdata.json` entry gives 28 through 30, with the 30-block entry dated 1996-11-14 and attributed to a JCD article. The classical [Schönheim recurrence](https://doi.org/10.2140/pjm.1964.14.1405) gives 26 from the nested ceilings. Using the exact [minimum C(12,6,3) = 15](https://combinatorialpress.com/ars-articles/volume-040-ars-articles/minimum-12-6-3-covers/) as the input to its last step gives 28.

The July 2026 [class-52 certification](https://doi.org/10.5281/zenodo.21660461) excludes one type of minimum point link. The later [Hexagon preprint 2610.00669v1](https://hexagonmath.org/2610.00669v1), dated 2026-10-31 on the work page, gives the full lower bound of 30. It supplies an exact finite enumeration and a separate Lean argument conditional on the published minimum and classification. The [proof sources](https://github.com/jjtripodo-lgtm/c13-covering-number/tree/254ee82fdbc215ad73f732f807a83d69be7c1e22) are public. The preprint discloses AI assistance, no independent human specialist review and no fresh Lean build of the public export. The searches turned up no smaller construction or correction to the preprint.

## Measured

There are 1,716 possible 7-subsets of 13 points, 715 four-subsets to cover and 35 four-subsets per block. The [preprint's source copy of the La Jolla construction](https://github.com/jjtripodo-lgtm/c13-covering-number/blob/254ee82fdbc215ad73f732f807a83d69be7c1e22/lean/C13/CoverData.lean) supplied the 30 blocks after adding 1 to each label. Python enumeration and Frontier's `diagnose` both accepted it and counted 22 uncovered four-subsets after deleting the first block. Both diagnose calls exited 0. The validity comes from the output. The conversion and two calls ran at 2026-11-17T22:34:11Z and took about 0.32 wall seconds and 0.16 CPU seconds combined at the timer's precision. The third-party blocks stay in scratch.

## Inferred

In a hypothetical 29-block cover, each point lies in at least 15 blocks because its link covers all triples on the other 12 points. The sum of point degrees is 203, at most eight above the 13-point minimum of 195. At least five points therefore have degree 15. One such point determines a classified link and leaves just 14 blocks outside it. At four other degree-15 points, their classified links determine families of outside blocks that must agree on shared blocks. The preprint's exhaustive join reports that every compatible choice uses 15 distinct outside blocks. A smaller cover could be padded to 29, so the same exclusion applies.

The source is sufficient to retire the 29-block search under this task's prior-art rule. No orbit set cover, full CP-SAT or annealing ran. There was no search runtime or per-group result. Frontier treats this writeup as unchecked. The local verifier confirms the upper bound, and the cited preprint supplies the lower bound. This run reviewed the proof reduction and did not replay its finite enumeration or compile Lean.

A follow-up should audit the classification transcription and reproduce the finite obstruction before changing the catalog status.
