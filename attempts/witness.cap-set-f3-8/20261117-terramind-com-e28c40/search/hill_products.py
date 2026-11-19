"""Construct the Hill 56-cap, its affine 45-cap and doubled 112-cap.

Reference: Large caps in projective Galois spaces,
https://www.yvesedel.de/Papers/CapSurvey.pdf, section 3.
The support design and all encoding code below are derived here, not copied.
"""
import runpy,pathlib,itertools,json
P=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(P/'search.py')); np=m['np']; log=m['log']
sp6=m['Space'](6)
# A 2-(6,3,2) support design: infinity joined to the edges of a pentagon,
# together with complements of its diagonals inside the five finite points.
edges={frozenset((i,(i+1)%5)) for i in range(5)}
supports=[set(e)|{5} for e in edges]
for e in itertools.combinations(range(5),2):
    if frozenset(e) not in edges: supports.append(set(range(5))-set(e))
assert len(supports)==10
assert all(sum(set(e)<=s for s in supports)==2 for e in itertools.combinations(range(6),2))
assert all(set(range(6))-s not in supports for s in supports)
projective=[]
for v in sp6.v:
    nz=np.flatnonzero(v)
    if len(nz)==0 or v[nz[0]]!=1: continue
    if len(nz)==3 and set(map(int,nz)) in supports: projective.append(tuple(map(int,v)))
    if len(nz)==6 and int(np.prod(v.astype(np.int64)))%3==1: projective.append(tuple(map(int,v)))
assert len(projective)==56
# Check the projective cap directly: all linear combinations with two nonzero
# coefficients must avoid every third projective point, up to scalar.
projective_set=set(projective)
for a,b in itertools.combinations(projective,2):
    for c in [tuple((x+y)%3 for x,y in zip(a,b)),tuple((x+2*y)%3 for x,y in zip(a,b))]:
        nz=next(i for i,t in enumerate(c) if t)
        norm=tuple((c[nz]*t)%3 for t in c)
        assert norm not in projective_set
p=np.array(projective,dtype=np.int32)
cap112=set(np.concatenate((p,(-p)%3))@sp6.p)
assert len(cap112)==112 and sp6.valid(cap112)
sp6.save(P/'hill112.json',cap112)
# Find and delete an 11-hyperplane, normalize its complement to h.x=1,
# then drop one pivot coordinate to identify that affine chart with F3^5.
for h in sp6.v[1:]:
    dot=(p@h)%3
    if int(np.count_nonzero(dot==0))==11: break
else: raise AssertionError('11-hyperplane missing')
q=(p[dot!=0]*dot[dot!=0,None])%3
pivot=int(np.flatnonzero(h)[0]); affine=np.delete(q,pivot,axis=1)
sp5=m['Space'](5); cap45=set(affine@sp5.p)
assert len(cap45)==45 and sp5.valid(cap45)
sp5.save(P/'hill45.json',cap45)
# Four-cap in dimension two; elliptic-paraboloid nine-cap in dimension three.
s2=list(itertools.product([1,2],repeat=2))
s3=[(x,y,(x*x+y*y)%3) for x,y in itertools.product(range(3),repeat=2)]
sp8=m['Space'](8)
product448={tuple(sp6.v[u])+v for u,v in itertools.product(cap112,s2)}
product405={tuple(sp5.v[u])+v for u,v in itertools.product(cap45,s3)}
a=set(np.array(sorted(product448))@sp8.p); b=set(np.array(sorted(product405))@sp8.p)
assert len(a)==448 and sp8.valid(a) and len(b)==405 and sp8.valid(b)
sp8.save(P/'hill-product448.json',a); sp8.save(P/'hill-product405.json',b)
# Calibrate the actual product starting object through the same refill engine.
rng=np.random.default_rng(402); weak=a-set(map(int,rng.choice(sorted(a),5,replace=False)))
out,row=sp8.exchange(weak,set(),30,402,exclude=False)
assert out is not None and len(out)>=448
log('hill_products',projective=56,affine45=len(cap45),doubled112=len(cap112),product448=len(a),product405=len(b),h=h.tolist(),pivot=pivot,calibration_restored=len(out),min_block448=int(sp8.blocks(a)[[u for u in range(sp8.m) if u not in a]].min()))
