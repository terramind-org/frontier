"""Run after all search processes exit: repository-diagnose every saved colouring."""
import pathlib,json,subprocess,sys,hashlib,datetime,time
P=pathlib.Path(__file__).resolve().parent;start=time.monotonic();print('AUDIT_START',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
bun=str(pathlib.Path.home()/'.bun/bin/bun');counts={'candidates':0,'valid':0,'invalid':0,'errors':0,'improvements':0};best=0
with (P/'candidate-audit.jsonl').open('w') as out:
 for path in sorted(P.glob('*.json')):
  try:w=json.loads(path.read_text())
  except (ValueError,UnicodeDecodeError):continue
  if not isinstance(w,dict) or set(w)!={'colors'}:continue
  proc=subprocess.run([bun,'frontier','diagnose',str(path),'--problem','witness.schur-7','--json'],capture_output=True,text=True)
  try:result=json.loads(proc.stdout)
  except ValueError:result=None
  row={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'n':len(w['colors']),'exit_code':proc.returncode,'result':result,'stdout':proc.stdout,'stderr':proc.stderr}
  out.write(json.dumps(row)+'\n');out.flush();counts['candidates']+=1
  if proc.returncode or result is None:counts['errors']+=1
  else:
   # Record the actual shape; schema-independent valid flag lookup permits the CLI's envelope.
   r=result.get('verification',result.get('result',result))
   if not isinstance(r,dict):r=result
   valid=r.get('valid',result.get('valid'))
   if valid is True:counts['valid']+=1;best=max(best,len(w['colors']));counts['improvements']+=int(len(w['colors'])>1696)
   elif valid is False:counts['invalid']+=1
   else:counts['errors']+=1
  if counts['candidates']%25==0:print('AUDIT_PROGRESS',counts,'best_valid',best,'seconds',time.monotonic()-start,flush=True)
print('AUDIT_END',counts,'best_valid',best,'seconds',time.monotonic()-start,flush=True)
(P/'audit-summary.json').write_text(json.dumps({'counts':counts,'best_valid':best,'seconds':time.monotonic()-start})+'\n')
if counts['errors']:sys.exit(2)
