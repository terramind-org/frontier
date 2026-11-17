import pathlib,sys,itertools,json,random
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent));import lkh_search as L
r=L.ROOT
for mode,n in [('cal-n5-s',5),('cal-fixed-n5-s',5),('cal-adjacent-n6-s',6)]:
 for seed in [1,2,3]:
  if n==5:p=[''.join(q) for q in itertools.permutations('12345')]
  else:
   f=next(f for f in (r/'pc6').glob('6_872*.txt') if 'twoCycles' not in f.name);p=L.path(f.read_text().splitlines()[0].strip(),6)
   rng=random.Random(seed);a=rng.randrange(len(p));b=(a+1)%len(p);p[a],p[b]=p[b],p[a]
  full=mode!='cal-fixed-n5-s';nodes=[p[0]]+p if full else [p[0]]+p[1:-1]
  lines=(r/f'{mode}{seed}'/'result.tour').read_text().split('TOUR_SECTION')[1].split();tour=[]
  for x in lines:
   if x=='-1':break
   tour.append(int(x)-1)
  z=tour.index(0);tour=tour[z:]+tour[:z]
  q=[p[i-1] for i in tour[1:]] if full else [p[0]]+[nodes[i] for i in tour[1:]]+[p[-1]]
  (r/f'{mode}{seed}'/'word.json').write_text(json.dumps({'n':n,'word':L.word(q)}))
p=L.path(json.loads((r/'baseline.json').read_text())['word'],7);bad=p[1800:2800];bad[300],bad[301]=bad[301],bad[300]
tour=[]
for x in (r/'cal-fixed-n7/result.tour').read_text().split('TOUR_SECTION')[1].split():
 if x=='-1':break
 tour.append(int(x)-1)
z=tour.index(0);tour=tour[z:]+tour[:z]
q=[bad[0]]+[bad[i] for i in tour[1:]]+[bad[-1]]
(r/'n7-repair-control.json').write_text(json.dumps({'n':7,'word':L.word(p[:1800]+q+p[2800:])}))
(r/'n7-repair-frontier.json').write_text(json.dumps({'word':L.word(p[:1800]+q+p[2800:])}))
