"""Summarize retained run provenance and independently recompute saved metrics."""
import datetime
import hashlib
import json
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent
utc=lambda t:datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
specs={
 'search':('search.py',17112026,'--scratch .terramind/scratch/kissing11 --seconds 7200'),
 'structure':('structure.py',None,'baseline coordinate types; deterministic'),
 'expanded':('structure.py',None,'--expanded; deterministic'),
 'integer-pool':('integer_pool_initial.py',None,'aborted full integer-pool model; archived source'),
 'integer-subset':('integer_pool.py',17112028,'guarded 5000-point subset'),
 'dominance':('dominance.py',None,'128-row blocks; 128 low-degree dominator tests per vertex'),
 'relax':('relax_initial.py',17112027,'p<=16; stopped at plateau'),
 'relax-high':('relax_high_snapshot.py',17112029,'--p-max 64 --label relax-high'),
 'relax-wide':('relax.py',17112030,'--p-max 256 --jitter-scale 3 --label relax-wide'),
}
index={}
for name,(script,seed,params) in specs.items():
    log=root/(name+'.out');st=log.stat();status=root/(name+'.exit')
    records=[]
    for line in log.read_text().splitlines():
        try:
            if line.startswith('{'):records.append(json.loads(line))
            elif line.startswith('END {'):records.append(json.loads(line[4:]))
        except json.JSONDecodeError:pass
    index[name]={'script':script,'script_sha256':hashlib.sha256((root/script).read_bytes()).hexdigest(),
        'seed':seed,'parameters':params,'stdout_log':log.name,'stdout_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
        'log_redirect_creation_utc':utc(st.st_birthtime),'start_time_note':'filesystem creation of redirected log; process header is more precise when present',
        'exit_status':int(status.read_text()) if status.exists() else None,
        'exit_status_written_utc':utc(status.stat().st_mtime) if status.exists() else None,
        'first_json_record':records[0] if records else None,'last_json_record':records[-1] if records else None}
(root/'run-index.json').write_text(json.dumps(index,indent=2))
raw=np.array(json.loads((root/'baseline.json').read_text())['vectors'])
base=(raw[:,::2]+np.sqrt(2)*raw[:,1::2])/6
holes=np.load(root/'holes.npz')['directions']
backbone=np.all(raw[:,1::2]==0,axis=1)
overlaps=holes@base.T
blockers=np.count_nonzero(overlaps>.5+1e-12,axis=1)
values,counts=np.unique(blockers,return_counts=True)
objective=json.loads((root/'best-objective.json').read_text())
x=np.load(root/objective['source'])['vectors'];x=x/np.linalg.norm(x,axis=1,keepdims=True)
g=x@x.T;independent=np.einsum('ik,jk->ij',x,x)
diff=float(np.max(abs(g-independent)))
assert np.isfinite(g).all() and diff<1e-12
np.fill_diagonal(independent,-1)
summary={'backbone_count':int(backbone.sum()),'extension_count':int((~backbone).sum()),
 'baseline_contacts':int((np.abs(base@base.T-.5)<1e-12).sum()//2),
 'retained_holes':len(holes),'distinct_holes_rounded_1e8':len(np.unique(np.round(holes,8),axis=0)),
 'hole_blocker_histogram':{str(int(v)):int(c) for v,c in zip(values,counts)},
 'best605_matmul_vs_einsum_max_absolute_difference':diff,
 'best605_einsum_max_pairwise_cosine':float(independent.max()),
 'scratch_file_bytes':sum(p.stat().st_size for p in root.rglob('*') if p.is_file())}
(root/'evidence-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
