"""Export bitmask coefficients as 0/1 integers; this does NOT lift GF(2) to Z."""
import json, pathlib, sys
v=list(map(int,pathlib.Path(sys.argv[1]).read_text().split()))
assert len(v)==1+3*v[0]
terms=[]
for s in range(v[0]):
 mats=[[[int((v[1+3*s+k]>>(i*5+j))&1) for j in range(5)] for i in range(5)] for k in range(3)]
 mats[2]=list(map(list,zip(*mats[2])))
 terms.append(dict(zip(('a','b','c'),mats)))
pathlib.Path(sys.argv[2]).write_text(json.dumps(dict(terms=terms)))
