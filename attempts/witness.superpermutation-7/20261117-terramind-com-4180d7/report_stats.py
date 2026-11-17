"""Aggregate retained evidence; run after replay has processed the final archives."""
import collections,json,pathlib,sys
r=pathlib.Path(sys.argv[1]).resolve()
runs={name:[json.loads(x) for x in (r/file).read_text().splitlines()] for name,file in [('primary','lkh.jsonl'),('second','second/lkh.jsonl')]}
rows=[x for run in runs.values() for x in run if x.get('event')=='tour'];returned=[x for x in rows if 'hash' in x]
segments=[x for x in rows if not x['full']]
kernels=[json.loads(x) for x in (r/'kernel.jsonl').read_text().splitlines()]
kernels=[x for x in kernels if x.get('event')=='call' and x.get('n')==7]
by_score={}
for x in kernels:
 d=by_score.setdefault(str(x['score']),{'calls':0,'statuses':{},'rc':{},'seconds':0,'solutions':0})
 d['calls']+=1;d['statuses'][x['status']]=d['statuses'].get(x['status'],0)+1;d['rc'][str(x['rc'])]=d['rc'].get(str(x['rc']),0)+1;d['seconds']+=x['seconds'];d['solutions']+=len(x['solutions'])
out={'budget':json.loads((r/'budget.json').read_text()),'calls':len(rows),'returned_tours':len(returned),'full':sum(x['full'] for x in rows),'segments':len(segments),'window_sizes':dict(collections.Counter(x['hi']-x['lo'] for x in segments)),'distinct_returned_words':len({x['hash'] for x in returned}),'best':min([5905]+[x['returned_length'] for x in returned]),'heavy_at_5905':sorted({69}|{x['heavy'] for x in returned if x['returned_length']==5905}),'statuses':dict(collections.Counter(x['status'] for x in rows)),'return_codes':dict(collections.Counter(str(x['rc']) for x in rows)),'perturbations':dict(collections.Counter(x.get('perturbation','original_order') for x in rows)),'kernel_controls':by_score,'replay':json.loads((r/'replay-summary.json').read_text()),'call_start_utc':min(x['start'] for x in rows),'call_end_utc':max(x['end'] for x in rows)}
for file,key in [('deadline-stop.json','deadline_stop'),('second-phase-stop.json','phase_stop'),('archive/exit.json','archive_exit')]:
 if (r/file).exists():out[key]=json.loads((r/file).read_text())
(r/'report-stats.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
