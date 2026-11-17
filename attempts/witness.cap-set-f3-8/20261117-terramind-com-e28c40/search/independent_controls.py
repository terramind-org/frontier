"""Independent coordinate checks and exhaustive tiny orbit-model comparison."""
import json,itertools,pathlib,runpy,hashlib,datetime
p=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(p/'search.py')); np=m['np']; sp=m['Space'](8)
a=set(sp.load(p/'baseline.json')); coords={tuple(sp.v[i]) for i in a}
assert len(coords)==512
cnt={}
for u,v in itertools.combinations(coords,2):
    w=tuple((-x-y)%3 for x,y in zip(u,v))
    assert w not in coords
    cnt[w]=cnt.get(w,0)+1
assert min(cnt.values())==4 and len(cnt)==6561-512
rng=np.random.default_rng(811)
cert=sp.canonical(a)
for _ in range(12):
    permutation=rng.permutation(8); signs=rng.choice([1,2],8)
    b=set((sp.v[sorted(a)][:,permutation]*signs%3)@sp.p)
    assert sp.canonical(b)==cert
# Enumerate ALL centrally symmetric subsets of F3^2 and compare a direct
# coordinate checker with the same repeated-orbit line clauses used by exact_sym.
small=list(itertools.product(range(3),repeat=2)); neg=lambda u:tuple(-x%3 for x in u)
orbits=[]; handled=set()
for u in small:
    if u not in handled:
        o={u,neg(u)}; orbits.append(o); handled|=o
which={u:i for i,o in enumerate(orbits) for u in o}; clauses=set()
for a,b,c in itertools.combinations(small,3):
    if all((a[d]+b[d]+c[d])%3==0 for d in range(2)):
        clauses.add(tuple(sorted({which[a],which[b],which[c]})))
valid=0; best=0
for bits in itertools.product([0,1],repeat=len(orbits)):
    a=set().union(*(o for o,b in zip(orbits,bits) if b))
    direct=not any(all((u[d]+v[d]+w[d])%3==0 for d in range(2)) for u,v,w in itertools.combinations(a,3))
    model=all(not all(bits[i] for i in q) for q in clauses)
    assert direct==model
    if direct: valid+=1; best=max(best,len(a))
assert best==4
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_valid=True,min_block=4,outside_count=len(cnt),canonical_transform_tests=12,tiny_symmetric_subsets=2**len(orbits),tiny_valid=valid,tiny_best=best)))
