"""Independent Python GF(2) tensor audit and log summary. Run from repo root."""
import datetime, json, pathlib, re
root=pathlib.Path('.terramind/scratch/matmul5')
def valid_mask(path,broken=False):
 v=list(map(int,path.read_text().split()));assert len(v)==1+3*v[0]
 if broken:v[1]^=1
 z=[0]*625
 for s in range(v[0]):
  a,b,d=v[1+3*s:4+3*s]
  for i in range(25):
   if a>>i&1:
    for j in range(25):
     if b>>j&1:z[i*25+j]^=d
 for i in range(5):
  for j in range(5):
   for k in range(5):z[(i*5+j)*25+j*5+k]^=1<<(k*5+i)
 return not any(z)
assert valid_mask(root/'baseline.mask')
assert not valid_mask(root/'baseline.mask',True)
for f in ['final-0.mask','final-1.mask']:
 assert valid_mask(root/f),f
 print(f'{f}: GF2 tensor ACCEPT')
print('independent checker: baseline ACCEPT, deliberately broken baseline REJECT')
segments=[]
for name in ['search-segment1.out','search-segment2.out','search.out']:
 text=(root/name).read_text();workers={}
 for line in text.splitlines():
  if line.startswith(('PROGRESS','FINISH')):
   fields=dict(re.findall(r'(\w+)=([^ ]+)',line));workers[fields['worker']]=fields
 entry=dict(log=name,start=re.search(r'start_utc=(.*)',text)[1],end=re.search(r'end_utc=(.*)',text)[1],exit_status=int(re.search(r'search_exit_status=(\d+)',text)[1]),workers=workers)
 entry['wall_seconds']=(datetime.datetime.fromisoformat(entry['end'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(entry['start'].replace('Z','+00:00'))).total_seconds()
 segments.append(entry)
print(json.dumps(segments,indent=2))
print('guaranteed_flips_at_least',sum(int(w['flips']) for s in segments for w in s['workers'].values()))
print('guaranteed_restarts_at_least',sum(int(w['restarts']) for s in segments for w in s['workers'].values()))
(root/'summary.json').write_text(json.dumps(segments,indent=2))
