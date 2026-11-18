#!/usr/bin/env python3
"""Bounded exact triple-exchange screen for Station construction 3.

The completed c9 pair ledger is deliberately not read or extended.  This
experiment samples a deterministic, overlap-biased stream of compatible
triples from its separate 5,156-direction reservoir, deduplicating only the
new size-21..30 deletion pools.  Eligibility is always computed over the full
6,116-direction recovered shell.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, random, sqlite3, time
from pathlib import Path
import numpy as np

CERT=Path('/tmp/station-data-c5/artifacts/kissing_number/kissing_certificates.npz')
OUT=Path('.terramind/scratch/kissing11-c10')
FIXTURE='61b3a572ad194a3b97d8bcae8694d57ae676328a81ef0e4db95e57a2c9d44f37'
SEED=0xC10_21_30

def sign(a,b):
    if a==b==0:return 0
    if b==0:return 1 if a>0 else -1
    if a==0:return 1 if b>0 else -1
    if (a>0)==(b>0):return 1 if a>0 else -1
    c=a*a-2*b*b
    return (1 if c>0 else -1) if a>0 else (1 if c<0 else -1)
def comp(p,q,r,s):return sign(int(p@r+2*(q@s)-8),int(p@s+q@r))<=0
def clique(adj,deadline):
    best=[]; timed=False
    def go(R,P,X):
        nonlocal best,timed
        if time.monotonic()>=deadline:timed=True;return
        if len(R)+len(P)<=len(best):return
        if not P and not X:
            if len(R)>len(best):best=R[:]
            return
        u=max(P|X,key=lambda v:len(P&adj[v]),default=-1)
        for v in sorted(P-adj[u]):
            go(R+[v],P&adj[v],X&adj[v]);P.remove(v);X.add(v)
            if timed:return
    go([],set(range(len(adj))),set());return best,timed
def controls():
    g=[set() for _ in range(7)]
    for i in range(4):
        for j in range(i):g[i].add(j);g[j].add(i)
    got,_=clique(g,time.monotonic()+1);assert len(got)==4
    for m in range(1<<15):
        a=[set() for _ in range(6)];b=0
        for i in range(6):
            for j in range(i):
                if m>>b&1:a[i].add(j);a[j].add(i)
                b+=1
        got,_=clique(a,time.monotonic()+1)
        brute=max((len(x) for n in range(7) for x in itertools.combinations(range(6),n)
                   if all(y in a[x] for x,y in itertools.combinations(x,2))),default=0)
        assert len(got)==brute
def load():
    assert hashlib.sha256(CERT.read_bytes()).hexdigest()==FIXTURE
    z=np.load(CERT,allow_pickle=False);P=z['config_coefficients'][2,:,:,0].astype(np.int64)//3;Q=z['config_coefficients'][2,:,:,1].astype(np.int64)//3
    ys=[]
    for k in range(12):
        for v in(-2,2):
            y=np.zeros(12,dtype=np.int64);y[k]=v;ys.append(y)
    for I in itertools.combinations(range(12),4):
        for S in itertools.product((-1,1),repeat=4):
            y=np.zeros(12,dtype=np.int64);y[list(I)]=S;ys.append(y)
    ys=[y for y in ys if int(y.sum())%2==0 and y[11]*(y[6]+y[8])==0]
    CP=[];CQ=[]
    for y in ys:
        p=2*y[:11].copy();q=np.zeros(11,dtype=np.int64);q[6]=q[8]=y[11];CP.append(p);CQ.append(q)
    keys={tuple(x.tolist()+y.tolist()) for x,y in zip(P,Q)}
    keep=[tuple(x.tolist()+y.tolist()) not in keys for x,y in zip(CP,CQ)]
    CP=np.asarray([x for x,k in zip(CP,keep) if k]);CQ=np.asarray([x for x,k in zip(CQ,keep) if k])
    B=[tuple(i for i,(r,s) in enumerate(zip(P,Q)) if not comp(p,q,r,s)) for p,q in zip(CP,CQ)]
    select=[i for i,b in enumerate(B) if 3<=len(b)<=10]
    order=hashlib.sha256(b''.join(np.asarray(CP[i],dtype='<i2').tobytes() for i in select)).hexdigest()
    return P,Q,CP,CQ,B,select,order
def dbopen():
    d=sqlite3.connect(OUT/'triple_ledger.sqlite');d.execute('pragma journal_mode=WAL');d.execute('pragma synchronous=FULL')
    d.executescript('create table if not exists meta(k text primary key,v text not null);'
      'create table if not exists triples(pos integer primary key,i integer,j integer,k integer,d text not null);'
      'create table if not exists pools(d text primary key,n integer not null,status text not null default "unvisited",clique integer,detail text);'
      'create index if not exists pool_state on pools(status,d);')
    return d
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=1440);ap.add_argument('--per-pool',type=float,default=.15);ap.add_argument('--batch',type=int,default=256);a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);begin=time.monotonic();deadline=begin+a.seconds;controls();P,Q,CP,CQ,B,select,order=load();M=[sum(1<<x for x in b) for b in B]
    # exact 604 baseline control, separate from candidate screening
    assert len(P)==604 and len({tuple(x.tolist()+y.tolist()) for x,y in zip(P,Q)})==604
    assert all(comp(P[i],Q[i],P[j],Q[j]) for i in range(604) for j in range(i))
    d=dbopen();meta={'fixture_sha256':FIXTURE,'candidate_order_sha256':order,'selected_directions':str(len(select)),'full_shell_directions':str(len(CP)),'stream':'python.Random(seed=0xc102130), sorted triple indices, accept compatibility + blocker-overlap>=1 + union size 21..30','seed':str(SEED)}
    with d:d.executemany('insert or replace into meta values(?,?)',meta.items())
    # predicate equivalence controls on the first deterministic pool prefix
    for (key,) in d.execute('select d from pools order by d limit 32'):
        D={int(x) for x in key.split(',')};mask=sum(1<<x for x in D)
        assert [i for i,b in enumerate(B) if set(b)<=D]==[i for i,m in enumerate(M) if m&~mask==0]
    pos=int(dict(d.execute('select k,v from meta')).get('stream_cursor','0'));rng=random.Random(SEED)
    for _ in range(pos):rng.randrange(len(select));rng.randrange(len(select));rng.randrange(len(select))
    generated=0
    while time.monotonic()<deadline:
        rows=[];pools={}
        for _ in range(a.batch):
            i,j,k=sorted((select[rng.randrange(len(select))],select[rng.randrange(len(select))],select[rng.randrange(len(select))]));pos+=1
            if len({i,j,k})<3 or not(comp(CP[i],CQ[i],CP[j],CQ[j]) and comp(CP[i],CQ[i],CP[k],CQ[k]) and comp(CP[j],CQ[j],CP[k],CQ[k])):continue
            # Favor triples with actual shared blockers, while retaining exact tests.
            if not (M[i]&M[j] or M[i]&M[k] or M[j]&M[k]):continue
            D=M[i]|M[j]|M[k];n=D.bit_count()
            if not 21<=n<=30:continue
            key=','.join(map(str,(x for x in range(604) if D>>x&1)))
            rows.append((pos,i,j,k,key));pools[key]=n
        with d:
            d.executemany('insert or ignore into triples values(?,?,?,?,?)',rows)
            d.executemany('insert or ignore into pools(d,n) values(?,?)',pools.items())
            d.execute('insert or replace into meta values(?,?)',('stream_cursor',str(pos)))
        generated+=a.batch
        # One full-shell exact eligibility screen per generated batch.
        row=d.execute("select d,n from pools where status='unvisited' order by d limit 1").fetchone()
        if row:
            key,n=row;D=sum(1<<int(x) for x in key.split(','));elig=[x for x,m in enumerate(M) if m&~D==0]
            if len(elig)<=n:
                with d:d.execute("update pools set status='pruned',clique=? where d=?",(len(elig),key))
            else:
                adj=[set() for _ in elig]
                for x,u in enumerate(elig):
                    for y in range(x):
                        v=elig[y]
                        if comp(CP[u],CQ[u],CP[v],CQ[v]):adj[x].add(y);adj[y].add(x)
                best,to=clique(adj,min(deadline,time.monotonic()+a.per_pool));status='timeout' if to else 'exhaustive';detail=json.dumps([elig[x] for x in best])
                with d:d.execute('update pools set status=?,clique=?,detail=? where d=?',(status,len(best),detail,key))
                if len(best)>n:raise SystemExit('GAIN '+key+' '+detail)
    counts=dict(d.execute('select status,count(*) from pools group by status'));first=d.execute("select d from pools where status='unvisited' order by d limit 1").fetchone()
    summary={'fixture_sha256':FIXTURE,'candidate_order_sha256':order,'selected_directions':len(select),'full_shell_directions':len(CP),'stream_cursor':pos,'accepted_triples':d.execute('select count(*) from triples').fetchone()[0],'unique_pools':d.execute('select count(*) from pools').fetchone()[0],'counts':counts,'first_unvisited':first[0] if first else None,'elapsed':time.monotonic()-begin}
    (OUT/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
