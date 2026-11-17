"""Render the measured run record; requires completed logs and final-metrics.json."""
import pathlib,json,collections,datetime,sys
P=pathlib.Path(__file__).resolve().parent
out=pathlib.Path(sys.argv[1]); metrics=json.loads((P/'final-metrics.json').read_text())
def rows(name):
    result=[]
    for s in (P/(name+'.jsonl')).read_text().splitlines():
        try: result.append(json.loads(s))
        except json.JSONDecodeError: pass
    return result
def last(name,event): return next(r for r in reversed(rows(name)) if r.get('event')==event)
def status(name):
    f=P/(name+'.exit'); return f.read_text().strip() if f.exists() else 'not recorded'
def span(rr):
    return (datetime.datetime.fromisoformat(rr[-1]['utc'])-datetime.datetime.fromisoformat(rr[0]['utc'])).total_seconds()
walks=[]
for name,seed in [('plateau',211),('smaller-early',217),('product448',403),('product405',404),('other448',405),('smaller',216)]:
    rr=rows(name); vv=[r for r in rr if r.get('event')=='visit']; ee=[r for r in rr if r.get('event')=='exchange']
    counts=collections.Counter(r['status'] for r in ee)
    calls=max((r.get('call',0) for r in rr),default=0)
    walks.append(f"| {name} | {seed} | {vv[0]['size']} | {max(r['size'] for r in vv)} | {len({r['canonical'] for r in vv})} | {len(ee)} | {len({(r['start_hash'],r['r_hash']) for r in ee})} | {dict(counts)} | {span(rr):.1f} | {status(name)} |")
sym=[]
for name in ['exact-all','exact-few','exact-half','exact-few-warm']:
    rr=rows(name); a=next(r for r in rr if r.get('event')=='exact_model_start'); b=next(r for r in rr if r.get('event')=='exact_model_built'); e=last(name,'exact_end')
    sym.append(f"| {name} | {a['orbits']} | {b['constraints']} | {e['best']} | {e['bound']:g} | {e['status']} | {e['seconds']:.2f} |")
phases=[]
for name in ['calibration','exact-all','control-few','control-half','plateau','smaller-early','region','product-build','product448','product405','other448','exact-few','exact-half','sat-control','sat-region','smaller','exact-few-warm']:
    rr=rows(name)
    phases.append(f"| {name} | {rr[0]['utc']} | {rr[-1]['utc']} | {status(name)} |")
sat=last('sat-region','sat_end'); model=last('sat-region','sat_model')
initial=rows('plateau'); ee=[r for r in initial if r.get('event')=='exchange']
empty=sum(r['r']==0 for r in ee)
text=f'''# Exclusion-guided cap plateaus, stabilizer models and full-line SAT in F_3^8

No cap larger than 512 was found. This writeup records the failed search. Frontier reports `unchecked` for writeups.
The largest retained valid cap has {metrics['largest_valid_retained']} points and ties the recorded 512 lower bound.
One saved 448 start stayed at 448. The other grew through exchanges to the original 512-cap.
A separately constructed 448-point literature product grew to 449.

## Measured

The search-process envelope is **{metrics['start']} to {metrics['end']}**, about
{metrics['elapsed_seconds']/60:.2f} minutes of a 120-minute budget, including calibration and overlapping streams.
The first time is the shell timestamp immediately before the first Python process, so it includes its import time.
UTC phase timestamps below are the first and last JSON log records and may exclude imports.

Research walks retained {metrics['labelled512_walk']} distinct labelled 512-caps. Including the full stabilizer model,
there were {metrics['labelled512_including_symmetry']} distinct retained labelled 512-caps, in
{metrics['signed_classes512']} signed-coordinate {'class' if metrics['signed_classes512']==1 else 'classes'} under coordinate permutations and independent coordinate negations.
The smallest outside-point blocking count among these 512-caps was {metrics['min_block512']}.
These counts cover saved walk states and returned incumbents. Internal solver assignments were unobserved.
Calibration objects are excluded from the research count. General affine equivalence was not computed.

`bun frontier diagnose` accepted the baseline, recovered 512, constructed products, 449 gain, 494 intermediate
and regrown 512. The regrown 512 matches the original labelled baseline exactly and ties the record.
All retained cap objects also passed the exact inner checker. No research candidate above the record was produced; the broken 513 was a negative control.

### Exchange runs

`OPTIMAL` means CP-SAT reports optimality for that conditional model. `FEASIBLE` is only an incumbent;
`UNKNOWN` gives no result. Neither status is a Frontier verdict. The neighborhood count uses the pair
(start-cap hash, removed-set hash), so repeated removals are not counted as distinct.
Canonical counts include starts and accepted or inspected equal-size alternatives at every size in that run.

| Run | Seed | Start | Best | Canonical states | Completed calls | Distinct neighborhoods | Call statuses | Logged seconds | Process exit |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
{chr(10).join(walks)}

The first 512-cap walk sampled 244 neighborhoods: 223 solver calls and 21 memory-cap skips. Its 223 calls included
{empty} empty removals, whose tabu clauses made the model infeasible. Later walks skip empty removals directly.
It recorded three labelled 512-caps, all in the starting signed-coordinate class, with minimum blocking count four.
The signed-coordinate class count stayed at one.

The `other448` run began at a complete 448-cap (minimum outside blocking count one). Its first recovered 512 was
logged at {next(r['utc'] for r in rows('other448') if r.get('event')=='visit' and r['size']==512)}.
It was deliberately stopped with SIGTERM after recovery of the known baseline, releasing a core for full-space SAT.
Its exit is 143; 65 solver returns are complete, and call 79 was interrupted. The controller's stop reason, UTC time,
last neighborhood and exit status are retained. Its log ends with a controller-generated termination record.
The later `smaller` run starts at the saved 449 literature-product cap.

### Symmetry models

A colored point-coordinate incidence graph gives signed-coordinate stabilizer generators of the baseline.
The discovered full stabilizer has order 512. The full model uses those eight generators plus global negation;
`few` uses global negation plus the first two generators, and `half` uses it plus the first four.
Every affine line is enumerated and its point orbits become a Boolean clause. Repeated orbit variables are
collapsed: three points in one orbit forbid that orbit; two orbits give a pair clause. Orbit cardinalities are the weights.
These models include every affine line within the selected invariant families.

| Run | Orbit variables | Constraints | Returned incumbent | Upper bound | CP-SAT status | Seconds |
|---|---:|---:|---:|---:|---|---:|
{chr(10).join(sym)}

The all-generator bound of 512 applies only to that symmetry restriction. No independently checkable proof
certificate was retained. The weaker models' loose bounds leave the target unresolved.
The first `few` run used the baseline with one orbit removed as its hint and failed to recover 512 within its limit,
although the baseline is feasible in the model. This measures failure to recover the known feasible baseline with that weakened hint.
The `half` and `few-warm` runs use the complete known 512 as a hint and require cardinality at least 512.
The warm retry recovered 512 from the complete hint.

### Region plus boundary

For each sampled codimension-two or -three affine region, the removal contains all cap points in the region and
both endpoints of every cap pair whose third point is inside it. The projected-frequency implementation was
checked against direct enumeration on 24 small tests, including dense and coordinate-aligned forms.
All 24 eight-dimensional samples removed all 512 points and freed all 6,561 candidates. Their forms and offsets
are logged. They exceeded the 2,200-candidate CP-SAT cap, so **none of those 24 CP-SAT models was run**.
The 24 regions are a finite logged sample.

The lower-memory replacement is a full-space SAT decision model for cardinality at least 513, allowing all points
to change. It contains {model['lines']:,} affine-line clauses and {model['cardinality_clauses']:,} cardinality-network clauses,
with {model['aux_vars']:,} auxiliary variables. All 6,561 point variables remain free. The baseline supplies branching phases only;
other solver randomization settings retain their library defaults.
Glucose4 returned **{sat['status']}** after {sat['seconds']:.2f} seconds including construction, with no witness and no upper bound.
Its recorded statistics are {sat['stats']['conflicts']:,} conflicts, {sat['stats']['decisions']:,} decisions and
{sat['stats']['propagations']:,} propagations. The decision problem remains undetermined.

## Method and calibration

Points use most-significant-first base-three integer IDs. The inner checker enumerates unordered pairs and their
coordinatewise third points. The published 512-cap was downloaded from
[the public data file](https://github.com/google-deepmind/funsearch/blob/main/cap_set/n8_size512.txt), compared with
the retained baseline, and accepted by the repo verifier at 512. Both checkers rejected a broken 513-point copy.

Before the main exchange run, deleting five baseline points was repaired to 512 (OPTIMAL). Forbidding the original
128-point refill found a different valid 512-cap (FEASIBLE); its signed-coordinate hash equals the baseline's.
A nonmaximal 12-point cap in dimension four grew to 20 (FEASIBLE), and the region/refill control grew 19 to 20.
Independent checks reproduced the complete baseline blocking distribution, tested 12 random signed-coordinate
transformations, and exhaustively compared orbit clauses with direct cap checks on all 32 centrally symmetric
subsets of F_3^2 (largest valid size four).

The first incremental symmetry encoder failed its 90-second known-20 control in dimension four.
It was dropped from the main schedule. Its failed control, source and exit 1 are retained for audit. Only calibration used this encoder.
The replacement full-line orbit encoder found 20 in the small controls. The SAT encoder separately found 20 from a
12-point phase hint in 1.59 seconds before its large run.

For an exchange, keep K, compute every addable candidate F, and maximize the refill over F with all pair/triple
constraints. For nonempty R, forbid restoration of R; previous compatible labelled states also get no-good clauses.
Accept gains and equal-size caps with new signed-coordinate certificates; retain each returned equal-size labelled
alternative even when its certificate is already known. Candidate sets above 2,200 are skipped explicitly.
Removals mix sizes 128, 192, 256, 320, 384 and 416, coordinate-reflection controls, and low-blocker targeting with
8, 32, 96 or 160 extra removals. Each CP-SAT call has one worker and normally at most 35 seconds.
Seeds, R/F/start hashes, sizes, statuses, bounds, restoration flags and timings are logged per completed call.
Every retained state has its full outside blocking histogram, distance from the start and raw/canonical hashes.
Unvisited neighborhoods and models interrupted before optimality remain uncharacterized.

## Literature starts

The 45- and 112-caps were constructed from the projective 56-cap. The starting point is
the weights-three/six description in [Large caps in projective Galois spaces, section 3](https://www.yvesedel.de/Papers/CapSurvey.pdf).
An explicitly derived 2-(6,3,2) support design selects 40 projective weight-three points; a product condition selects
16 weight-six points. All projective pair combinations were checked, giving a 56-cap. Its positive and negative
representatives give a checked 112-cap in F_3^6. Deleting an 11-hyperplane, normalizing its complement, and taking
an affine chart gives a checked 45-cap in F_3^5. The construction and direct checks are original code here.

Products with explicit four- and nine-caps give 448 and 405 in dimension eight, both accepted by the repo verifier.
A five-point deletion from the 448 product was restored to 448 before its run. That product then reached a
valid 449. The 405 product remained at 405. Their values remain below the record of 512.
The two priority-generated 448 inputs came from the prior attempt's retained data, named `variant2_448.json` and
`variant3_448.json`. They are distinct starts. Their coordinates and all new caps remain in scratch for audit;
the attempt contains the writeup and original source code.

## Evidence, runtime and reproduction

Retained evidence is in the `tame-aurora` worktree under `.terramind/scratch/capset8-r2/`.
`*.jsonl` holds progress, `*.stderr` diagnostics, and `*.start`, `*.end`, `*.exit` process metadata.
`visited/` holds accepted and inspected equal-size caps; the exact/SAT files hold returned solver incumbents.
`interruptions.jsonl` explains the deliberate termination. `summary-final.json` and `final-metrics.json` summarize
observations. Phase-specific `*.search-source.py` files preserve earlier source versions.

Two single-worker search streams ran concurrently, with OMP and BLAS thread counts set to one. There was no
OS-level CPU or memory sandbox; a brief independent checker overlapped both streams. Some later checks paused one
stream first. The largest logged single-process peak RSS was {metrics['max_logged_process_rss']/1024**3:.3f} GiB on this machine;
this is not an aggregate resource certificate. Disk usage remained below the 2 GiB limit.
Dependencies used were Python 3.12.1, NumPy 2.5.5, OR-Tools 9.15.6755, pynauty 2.8.8.1 and python-sat 1.9.dev22
with Glucose4. No paid APIs, cloud compute or Lean were used.

| Phase | First JSON UTC | Last JSON UTC | Exit |
|---|---|---|---:|
{chr(10).join(phases)}

Copy the source files and inputs to fresh scratch before running them.
Prepare `baseline.json` from the linked text file as `{{"points": [...]}}`, create the Python environment with the
versions above, and run `search.py calibrate`. `hill_products.py` builds the literature starts; `exact_sym.py` runs
the orbit models; `full_region_sat.py control` and then `full_region_sat.py 600` run the SAT tests. The shell schedules
record phase parameters. The archived `calibration_initial.py` reproduces the dropped control.
The two historical priority-generated inputs and the saved 449 continuation input are required for exact replay of
those particular starts; they are retained for audit rather than embedded in source. Time-limited solver outputs
and state counts can vary with machine load.

## Inferred

These runs found no cap above 512. The saved second 448-cap can reach the known 512 construction through exchanges;
that successful recovery does not demonstrate a route past it. The canonical quotient shows exactly how much of
the apparent labelled 512 diversity survives signed-coordinate equivalence. It does not settle affine equivalence
of the smaller caps. The loose subgroup bounds and unrestricted SAT UNKNOWN leave larger caps open.

A later search should test substantially different 512 classes, global exclusion of known signed-coordinate images,
and stronger cuts or symmetry handling for the full-space SAT model. The retained smaller-cap trajectories are
usable starts. The outcome of other plateau walks, regions and symmetry groups remains undetermined.
'''
(out/'writeup.md').write_text(text)
