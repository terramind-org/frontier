"""Audit retained caps and assemble final, observation-based run metrics."""
import pathlib,runpy,json,datetime,hashlib,struct
P=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(P/'search.py')); sp=m['Space'](8)
files=list((P/'visited').glob('*.json'))+list(P.glob('exact_8_*.json'))+list(P.glob('sat_region_8_*.json'))
raw={}; walk_raw=set(); canonical=set(); counts=[]
for f in files:
    a=set(sp.load(f)); assert sp.valid(a)
    if len(a)==512:
        h=m['digest'](a); raw[h]=f.name
        if f.parent.name=='visited': walk_raw.add(h)
        c=sp.canonical(a); canonical.add(c)
        bc=sp.blocks(a); outside=[u for u in range(sp.m) if u not in a]
        counts.append(int(bc[outside].min()))
assert not (P/'candidate513.json').exists(),'A record candidate needs official verification first'
ends=[]
search_phases={'calibration','plateau','region','exact-all','exact-few','exact-half','smaller-early','product-build','product448','product405','other448','smaller','sat-control','sat-region','exact-few-warm'}
for f in P.glob('*.end'):
    if f.stem not in search_phases: continue
    try: ends.append(datetime.datetime.fromisoformat(f.read_text().strip()))
    except ValueError: pass
start=datetime.datetime.fromisoformat((P/'calibration.start').read_text().strip())
end=max(ends)
rows={}
for f in P.glob('*.jsonl'):
    rr=[]
    for line in f.read_text().splitlines():
        try: rr.append(json.loads(line))
        except json.JSONDecodeError: pass
    rows[f.stem]=rr
metrics=dict(start=start.isoformat(),end=end.isoformat(),elapsed_seconds=(end-start).total_seconds(),
             valid_retained_caps=len(files),largest_valid_retained=max(len(sp.load(f)) for f in files),
             labelled512_walk=len(walk_raw),labelled512_including_symmetry=len(raw),signed_classes512=len(canonical),
             min_block512=min(counts),caps512=raw,
             max_logged_process_rss=max((r.get('max_rss_bytes',0) for rr in rows.values() for r in rr),default=0))
(P/'final-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps(metrics,indent=2))
