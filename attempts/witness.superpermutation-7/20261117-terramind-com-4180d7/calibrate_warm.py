import sys,pathlib,random,subprocess,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import lkh_search as L
R=L.ROOT
wd=R/'pc6';wd.mkdir(exist_ok=True)
r=subprocess.run([str(R/'PermutationChains'),'6','ffc'],cwd=wd,capture_output=True,text=True,timeout=20)
(wd/'stdout.log').write_text(r.stdout+r.stderr)
w=next(p for p in wd.glob('6_872*.txt') if 'twoCycles' not in p.name).read_text().splitlines()[0].strip()
assert L.valid(w,6) and len(w)==872
p=L.path(w,6);assert len(p)==720 and len(set(p))==720
for seed in [1,2,3]:
 rng=random.Random(seed);bad=p.copy()
 for _ in range(5):
  a=rng.randrange(len(p));b=rng.randrange(len(p));bad[a],bad[b]=bad[b],bad[a]
 before=len(L.word(bad));q,row=L.solve(bad,R/f'cal-warm-n6-s{seed}',seed,60,full=True,trials=20000,runs=10,candidates=30)
 passed=q is not None and len(L.word(q))==872 and L.valid(L.word(q),6)
 L.emit(R/'calibration-warm.jsonl',event='damaged_record_control',before=before,target=872,passed=passed,**row)
 if not passed:sys.exit(2)
