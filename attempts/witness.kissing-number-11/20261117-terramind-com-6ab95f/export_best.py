"""Export the best saved floating 605 to exact integer coordinates for diagnose.

This is a diagnostic, not a claim of validity. At zero angular slack, rounding
can destroy contacts. The repository verifier is authoritative.
"""
from pathlib import Path
import json
import numpy as np

root=Path(__file__).resolve().parent
choices=[]
for name in ['best605.npz','relax-best605.npz','relax-high-best605.npz','relax-wide-best605.npz']:
    if not (root/name).exists():continue
    x=np.load(root/name)['vectors'];x=x/np.linalg.norm(x,axis=1,keepdims=True)
    g=x@x.T;np.fill_diagonal(g,-1)
    choices.append((float(g.max()),name,x))
score,name,x=min(choices,key=lambda c:c[0])
rounded=np.rint(x*10**12).astype(np.int64)
rows=np.zeros((605,22),dtype=np.int64);rows[:,::2]=rounded
(root/'rounded-best605.json').write_text(json.dumps({'vectors':rows.tolist()}))
summary={'source':name,'max_pairwise_cosine':score,'maximum_positive_overlap':score-.5,
    'minimum_angle_degrees':float(np.degrees(np.arccos(score))), 'scale':10**12,
    'all_finite':bool(np.isfinite(x).all()),'minimum_norm':float(np.linalg.norm(x,axis=1).min()),
    'maximum_norm':float(np.linalg.norm(x,axis=1).max())}
(root/'best-objective.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
