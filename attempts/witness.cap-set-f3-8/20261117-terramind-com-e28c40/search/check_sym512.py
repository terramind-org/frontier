import runpy,pathlib,json
p=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(p/'search.py')); sp=m['Space'](8)
a=set(sp.load(p/'baseline.json')); b=set(sp.load(p/'exact_8_all_512.json'))
assert len(b)==512 and sp.valid(b)
outside=[u for u in range(sp.m) if u not in b]; bc=sp.blocks(b)
m['log']('sym512_check',size=len(b),hash=m['digest'](b),canonical=sp.canonical(b),baseline_canonical=sp.canonical(a),same_signed_class=sp.canonical(b)==sp.canonical(a),min_block=int(bc[outside].min()),intersection=len(a&b))
