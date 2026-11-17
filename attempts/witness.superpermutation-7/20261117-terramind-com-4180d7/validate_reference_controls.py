"""Validate published reference words independently of fresh completion searches."""
import datetime,hashlib,json,pathlib,subprocess
r=pathlib.Path(__file__).resolve().parent;repo=r.parents[2]
rows=[json.loads(x) for x in (r/'kernel.jsonl').read_text().splitlines()]
keys=list(dict.fromkeys(x['kernel'] for x in rows if x.get('event')=='call' and x.get('score')==10))
results=[]
for i,k in enumerate(keys):
 source=r/'kernel-download/repo/superpermutations/7/7_5906'/f'7_5906_nsk{k}_2SYMM_FS.txt'
 w=source.read_text().splitlines()[0].strip();dest=r/f'published-control-{i}.json';dest.write_text(json.dumps({'word':w}))
 p=subprocess.run(['bun','frontier','diagnose',str(dest.relative_to(repo)),'--problem','witness.superpermutation-7'],cwd=repo,capture_output=True,text=True)
 dest.with_suffix('.diagnose.log').write_text(p.stdout+p.stderr)
 assert 'valid:    yes' in p.stdout and len(w)==5906
 results.append({'kernel':k,'word_length':len(w),'sha256':hashlib.sha256(w.encode()).hexdigest(),'rc':p.returncode,'valid':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
(r/'published-controls-summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
