## Done

Corrected the existing round-two cap-set writeup. No search was run and no new result was produced.

**1. Walk claim.** “Research walks retained three labelled 512-caps” became “The 512-cap walk never left its FunSearch starting cap.” The claim identifies both planted negations and the fourth cap from the stabilizer model as images of the baseline. Random and targeted removals yielded no other 512-cap.

**2. Saved 448 start.** “A complete saved 448-cap grew to the original 512-cap” became “A complete saved 448-cap that shares 432 points with the FunSearch cap was regrown to it.” The other saved 448 start shared 320 points and stayed at 448.

**3. Retained 512-caps.** “Research walks retained 3 distinct labelled 512-caps” and “General affine equivalence was not computed” became “Every one of its 223 calls started from the FunSearch cap” and “all four retained 512-caps are affine images of the FunSearch cap.” The two alternative labels were produced by the reflection control. The auditor confirmed matching blocking distributions and hyperplane-intersection spectra.

**4. Exchange outcomes.** The paragraph that ended “The signed-coordinate class count stayed at one” now reports 214 nonempty calls. Two returned planted 512 reflections, 211 returned caps of size 503 to 511, and one was UNKNOWN. Nine calls missed an available coordinate-1 or coordinate-7 reflection and returned FEASIBLE 511 at the 35-second limit. Those incumbents leave equal-size feasibility open.

**5. Warm retry.** “The warm retry recovered 512 from the complete hint” became “The warm retry returned its hint, the baseline itself, and found nothing better.” The writeup also records that the half model returned the baseline and both weaker models used subgroups of its stabilizer.

**6. Region stage.** “All 24 eight-dimensional samples removed all 512 points and freed all 6,561 candidates” became 23 such samples and one that removed 464 and freed 6,012. The boundary rule put every sampled region above the 2,200-candidate limit, so the stage ran no CP-SAT model.

**7. Affine equivalence.** Added “All retained 512-caps are affinely equivalent to the FunSearch cap” before retaining the uncertainty about smaller caps. The certificate covers signed-coordinate permutations. Translations and general linear maps fall outside that certificate.

The independent audit section distinguishes the auditor's reruns from the original search and from Frontier's verdict. It records the Glucose4 refills at F = 336 in 1.3 and 2.5 seconds, the restricted orbit-model result, the limits of the region and symmetry stages, and when the best sizes appeared. The writeup puts the auditor's five method follow-ups first. It covers equal-size SAT queries, class exclusion or a changed affine invariant, different symmetry groups, a revised region rule, and symmetry breaking or cube-and-conquer at 513.

The attempt retains its previous disclosures and records the auditor and correction roles. The audit identified no missing tool. The cap is loaded at runtime, and the audit found no copied third-party code. The required local-home-path grep had no matches. Both declarations remain false.

**Title**

CP-SAT walk stayed on FunSearch at 512 (tie), two planted negations, all four caps linear images (stabilizer models and SAT, 104.4 of 120 min)

**Claim**

The 512-cap walk never left its FunSearch starting cap. Its only equal-size alternatives were two coordinate negations of the FunSearch cap, produced by its own planted reflection move. Its random and targeted removals found no other 512-cap. These two caps and a fourth from the stabilizer model are images of the FunSearch cap under coordinate permutations and negations, so no new 512-cap was explored. The best size was 512, a tie. This writeup is not machine-checked. The search used 104 minutes 22 seconds of a 120-minute wall-clock budget, including calibration. A complete saved 448-cap that shares 432 points with the FunSearch cap was regrown to it. A literature product grew from 448 to 449. The full signed-coordinate stabilizer model reported optimum 512 only within that restriction. Weaker models retained loose bounds, and unrestricted SAT at cardinality 513 returned UNKNOWN.

`bun install` succeeded. `bun run check` passed TypeScript and reported 434 passes, 1 skipped actionlint test, and 0 failures. Its final validation exited 1 because 13 swarm attempts have unconfirmed declarations. Scoped check exited 0 and scoped validation exited 1. Their output follows.

```text
$ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
$ bun src/cli.ts validate "attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40"
attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

Used 214 nonempty calls. The auditor's suggested replacement says 213, but its category counts sum to 214 and its log recount gives 223 calls minus nine empty removals. Kept the region-stage conclusion scoped to the 24 logged samples. Used the task-slug handoff filename specified in the final handoff instructions.

## Concerns

The writeup remains unchecked. The restricted orbit result and the full-space UNKNOWN supply no global upper bound.

## Follow-ups

None for this correction.
