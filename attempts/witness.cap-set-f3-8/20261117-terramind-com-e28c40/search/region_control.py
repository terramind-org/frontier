"""Compare the projected boundary formula with direct pair enumeration."""
import runpy,pathlib,itertools
P=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(P/'search.py')); np=m['np']; log=m['log']; sp=m['Space'](4)
a=set(sp.load(P/'control20.json')); rng=np.random.default_rng(880)
for trial in range(24):
    r,meta=m['region_removal'](sp,a,rng,2+trial%2)
    forms=np.array(meta['forms']); offset=np.array(meta['offset'])
    region=set(np.flatnonzero(np.all((sp.v@forms.T)%3==offset,axis=1)))
    direct=a&region
    for u,v in itertools.combinations(a,2):
        if int(sp.t[u,v]) in region: direct|={u,v}
    assert r==direct
log('region_control',trials=24,aligned_and_dense=True,all_equal=True)
