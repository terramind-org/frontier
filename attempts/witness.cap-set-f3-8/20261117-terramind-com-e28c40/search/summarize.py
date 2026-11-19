"""Summarize retained JSONL search logs without interpreting missing bounds."""
import json,pathlib,collections,sys
root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parent
summary={}; raw512=set(); classes512=set(); visits=collections.defaultdict(set)
for f in sorted(root.glob('*.jsonl')):
    rows=[]
    for line in f.read_text().splitlines():
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: pass
    if not rows: continue
    exchanges=[r for r in rows if r.get('event')=='exchange']
    vr=[r for r in rows if r.get('event')=='visit']
    for r in vr:
        visits[r['stage']].add(r['canonical'])
        if r['size']==512: raw512.add(r['hash']); classes512.add(r['canonical'])
    statuses=collections.Counter(r['status'] for r in exchanges)
    data=dict(first=rows[0].get('utc'),last=rows[-1].get('utc'),exchange_calls=len(exchanges),
              distinct_neighbourhoods=len({(r['start_hash'],r['r_hash']) for r in exchanges}),statuses=dict(statuses),
              best_returned=max((r['size'] for r in exchanges if r['size'] is not None),default=None),
              max_r=max((r['r'] for r in exchanges),default=None),max_f=max((r['f'] for r in exchanges),default=None),
              skips=sum(r.get('event')=='skip' for r in rows),restorations=sum(r.get('restore') is True for r in exchanges),empty_removal_solves=sum(r.get('r')==0 for r in exchanges),
              summary=[r for r in rows if r.get('event') in ('walk_end','exact_end','sat_model','sat_end','hill_products','calibration_end','controller_process_end')])
    e=root/(f.stem+'.exit'); data['process_exit']=e.read_text().strip() if e.exists() else None
    summary[f.stem]=data
out=dict(logs=summary,labelled512_walk_caps=len(raw512),signed_coordinate_classes512_walk=len(classes512),
         visited_classes_by_stage={k:len(v) for k,v in visits.items()})
print(json.dumps(out,indent=2))
