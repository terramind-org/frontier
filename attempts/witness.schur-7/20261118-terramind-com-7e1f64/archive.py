import json
from pathlib import Path
import sqlite3
import zlib

DB=Path("checkpoints.sqlite")
db=None

def connection():
    global db
    if db is None:
        db=sqlite3.connect(DB,timeout=30,isolation_level=None)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("""
            CREATE TABLE IF NOT EXISTS records(
                kind TEXT NOT NULL,
                key TEXT NOT NULL,
                n INT,
                status TEXT,
                worker INT,
                started TEXT,
                data BLOB NOT NULL,
                PRIMARY KEY(kind,key)
            ) WITHOUT ROWID
        """)
        db.execute("CREATE INDEX IF NOT EXISTS status_idx ON records(kind,status,n,worker)")
    return db

def pack(record):
    record=record.copy()
    if "job" in record:
        job=record["job"].copy()
        pairs=job.get("mirror")
        if pairs and pairs==[[x,job["n"]+1-x] for x in range(1,(job["n"]+1)//2+1)]:
            job["mirror"]="full"
        fixed=job.get("fixed")
        if isinstance(fixed,dict) and fixed:
            dense=["."]*max(map(int,fixed))
            for x,c in fixed.items():
                dense[int(x)-1]=str(c)
            job["fixed"]="".join(dense)
        record["job"]=job
    if "phase" in record:
        record["phase"]="".join(str((x-1)%6) for x in record["phase"])
    if "fixed" in record and isinstance(record["fixed"],dict) and record["fixed"]:
        fixed=record["fixed"]
        dense=["."]*max(map(int,fixed))
        for x,c in fixed.items():
            dense[int(x)-1]=str(c)
        record["fixed"]="".join(dense)
    return zlib.compress(json.dumps(record,separators=(",",":")).encode(),5)

def unpack(raw):
    record=json.loads(zlib.decompress(raw))
    job=record.get("job",{})
    if job.get("mirror")=="full":
        n=job["n"]
        job["mirror"]=[[x,n+1-x] for x in range(1,(n+1)//2+1)]
    for obj in (job,record):
        if isinstance(obj.get("fixed"),str):
            obj["fixed"]={str(i):int(c) for i,c in enumerate(obj["fixed"],1) if c!="."}
    if isinstance(record.get("phase"),str):
        record["phase"]=[6*i+int(c)+1 for i,c in enumerate(record["phase"])]
    return record

def store(kind,key,record,unique=False):
    selected=record.get("job",record)
    n=selected.get("n")
    if kind=="solution":
        n=len(record["colors"])
    status=record.get("status")
    worker=record.get("worker")
    started=record.get("utc_start",record.get("utc"))
    command="INSERT OR IGNORE" if unique else "INSERT OR REPLACE"
    return connection().execute(f"{command} INTO records VALUES(?,?,?,?,?,?,?)",
                                (kind,key,n,status,worker,started,pack(record))).rowcount == 1

def get(kind,key):
    found=connection().execute("SELECT data FROM records WHERE kind=? AND key=?",(kind,key)).fetchone()
    return unpack(found[0]) if found is not None else None

def exists(kind,key):
    return connection().execute("SELECT 1 FROM records WHERE kind=? AND key=?",(kind,key)).fetchone() is not None

def select(kind,prefix="",n=None,worker=None,order="key",limit=None):
    if order not in ("key","key DESC","started DESC","RANDOM()"):
        raise ValueError("Unknown checkpoint order")
    filters=["kind=?"]
    values=[kind]
    if prefix:
        filters+=["key>=?","key<?"]
        values += [prefix,prefix+"\U0010ffff"]
    for column,value in (("n",n),("worker",worker)):
        if value is not None:
            filters.append(f"{column}=?")
            values.append(value)
    where=" AND ".join(filters)
    sql=f"SELECT key,data FROM records WHERE {where} ORDER BY {order}"
    if limit is not None:
        sql += " LIMIT ?"
        values.append(limit)
    for key,raw in connection().execute(sql,values):
        yield key,unpack(raw)

def summary():
    conn=connection()
    base=conn.execute("SELECT COUNT(*) FROM records WHERE kind='base'").fetchone()[0]
    solutions=dict(conn.execute("""SELECT n,COUNT(*) FROM records WHERE kind='solution'
                                     AND key LIKE 'base-%' GROUP BY n"""))
    best=conn.execute("SELECT MAX(n) FROM records WHERE kind='solution'").fetchone()[0]
    return base, solutions, best

def migrate():
    mappings=[("job",Path("jobs")),("base",Path("bases")),("solution",Path("solutions"))]
    mappings.extend(("generation",p) for p in Path("jobs").glob("generation-*"))
    conn=connection()
    conn.execute("BEGIN IMMEDIATE")
    try:
        for kind,directory in mappings:
            for p in directory.glob("*.json"):
                record=json.loads(p.read_text())
                key=p.stem
                if kind=="generation":
                    worker=int(directory.name.rsplit("-",1)[-1])
                    key=f"{worker}:{p.stem}"
                    record["worker"]=worker
                store(kind,key,record,unique=True)
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise

if __name__=="__main__":
    migrate()
    print(summary())
