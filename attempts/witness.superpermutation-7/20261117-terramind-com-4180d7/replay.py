"""Replay archived solver tours independently of the search driver's overlap routine."""
import collections,hashlib,itertools,json,pathlib,sys
r=pathlib.Path(sys.argv[1]).resolve()
def permutations(w):return [w[i:i+7] for i in range(len(w)-6) if len(set(w[i:i+7]))==7]
def make_word(p):
 out=p[0]
 for a,b in zip(p,p[1:]):
  overlap=max([0]+[j for j in range(1,7) if a[-j:]==b[:j]])
  out+=b[overlap:]
 return out
base=[permutations(json.loads((r/f).read_text())['word']) for f in ['baseline.json','sol2.json']]
all_perms={''.join(p) for p in itertools.permutations('1234567')};summary=[]
for run in ['primary','second']:
 paths=[x.copy() for x in (base if run=='primary' else base[::-1])];initial=[x.copy() for x in paths];seen=set();calls=0;full=0;segments=0;novel=0;failures=0;distances=[];initial_hashes=set();initial_lengths=[]
 folder=r/'archive'/run
 for wd in sorted(folder.iterdir(),key=lambda x:int(x.name)):
  row=json.loads((wd/'row.json').read_text())
  which=row['start_word']-1;p=paths[which];lo=row['lo'];hi=row['hi'];seg=p[lo:hi]
  seg=[seg[i] for i in row.get('initial_order',range(len(seg)))]
  iw=make_word(p[:lo]+seg+p[hi:]);initial_hashes.add(hashlib.sha256(iw.encode()).hexdigest());initial_lengths.append(len(iw))
  if 'hash' not in row:
   assert row.get('word_length') is None
   failures+=1;calls+=1;full+=int(row['full']);segments+=int(not row['full']);continue
  tour=[]
  for x in (wd/'result.tour').read_text().split('TOUR_SECTION')[1].split():
   if x=='-1':break
   tour.append(int(x)-1)
  expected=len(seg)+(1 if row['full'] else -1)
  assert sorted(tour)==list(range(expected))
  z=tour.index(0);tour=tour[z:]+tour[:z]
  if row['full']:q=[seg[i-1] for i in tour[1:]];full+=1
  else:q=[seg[0]]+[seg[i] for i in tour[1:]]+[seg[-1]];segments+=1
  assert sorted(q)==sorted(seg)
  candidate=p[:lo]+q+p[hi:];w=make_word(candidate)
  assert set(permutations(w))==all_perms
  assert w==json.loads((wd/'word.json').read_text())['word']
  digest=hashlib.sha256(w.encode()).hexdigest();assert digest==row['hash']
  assert len(w)==row['returned_length'] and len(make_word(p))==row['old']
  assert row['distance']==sum(a!=b for a,b in zip(p,candidate))
  heavy=sum(1 for a,b in zip(candidate,candidate[1:]) if max([0]+[j for j in range(1,7) if a[-j:]==b[:j]])<=4)
  assert heavy==row['heavy']
  assert row['accepted']==(len(w)<=row['old'])
  if row['accepted']:paths[which]=candidate
  seen.add(digest);assert len(seen)==row['distinct_words']
  calls+=1;novel+=len(w)<5905
  distances.append({'iteration':row['iteration'],'from_start':sum(a!=b for a,b in zip(initial[which],candidate)),'word_length':len(w),'heavy':heavy,'accepted':row['accepted']})
 summary.append({'run':run,'calls':calls,'no_returned_tour':failures,'full':full,'segments':segments,'distinct_initial_words':len(initial_hashes),'max_initial_length':max([5905]+initial_lengths),'distinct_returned_words':len(seen),'below_record':novel,'max_distance_from_start':max([0]+[x['from_start'] for x in distances]),'best':min([5905]+[x['word_length'] for x in distances]),'heavy_at_best':min([69]+[x['heavy'] for x in distances if x['word_length']==5905])})
 (r/f'replay-{run}-distances.json').write_text(json.dumps(distances))
(r/'replay-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
