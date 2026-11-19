"""Rebuild seven-colour partitions from all three supplied product templates."""
import pathlib,json,xlrd,time,datetime
P=pathlib.Path(__file__).resolve().parent
start=time.monotonic();print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),'deterministic: no random seed')
s=xlrd.open_workbook(str(P/'ancillary/specimens.xls')).sheet_by_name('TFT-4,5,6')
def objective(a):
 return sum(a[x-1]==a[y-1]==a[x+y-1] for x in range(1,len(a)//2+1) for y in range(x,len(a)-x+1))
def compound(m,col,base):
 template=[int(s.cell_value(r,col))-1 for r in range(16,16+m)]
 q=max(template)+1;tc=template[-1];phi=template.index(tc)
 labels={c:i for i,c in enumerate(sorted(set(template)-{tc}))}
 a=[]
 for i in range(1,m*len(base)+phi+1):
  block,res=divmod(i-1,m);c=template[res]
  a.append(q-1+base[block] if c==tc else labels[c])
 print('TEMPLATE',m,'q',q,'phi',phi,'base_length',len(base),'N',len(a),'colours',max(a)+1,'objective',objective(a),flush=True)
 assert objective(a)==0
 return a
s4=compound(33,6,[0])
s3=[0 if i in {1,4,10,13} else 1 if i in {2,3,11,12} else 2 for i in range(1,14)]
assert objective(s3)==0
for m,col,base in [(33,6,s4),(109,7,s3),(376,8,[0,1,1,0])]:
 a=compound(m,col,base);(P/f'product{m}.json').write_text(json.dumps({'colors':a})+'\n')
print('END seconds',time.monotonic()-start,'exit 0')
