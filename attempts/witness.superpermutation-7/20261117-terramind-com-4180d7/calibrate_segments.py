import sys,pathlib,itertools,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import lkh_search as L
for seed in [1,2,3]:
 p=[''.join(q) for q in itertools.permutations('12345')]
 q,row=L.solve(p,L.ROOT/f'cal-fixed-n5-s{seed}',seed,20,trials=20000,runs=10,candidates=30)
 passed=q is not None and len(L.word(q))==153 and L.valid(L.word(q),5)
 L.emit(L.ROOT/'calibration-segment.jsonl',event='fixed_n5',target=153,passed=passed,**row)
 if not passed:sys.exit(2)
p=L.path(json.loads((L.ROOT/'baseline.json').read_text())['word'],7)
seg=p[1800:2800];bad=seg.copy();bad[300],bad[301]=bad[301],bad[300]
q,row=L.solve(bad,L.ROOT/'cal-fixed-n7',71,60,trials=20000,runs=10,candidates=30)
passed=q is not None and len(L.word(q))<=len(L.word(seg)) and L.valid(L.word(p[:1800]+q+p[2800:]),7)
L.emit(L.ROOT/'calibration-segment.jsonl',event='fixed_n7_repair',before=len(L.word(bad)),target=len(L.word(seg)),passed=passed,**row)
if not passed:sys.exit(2)
