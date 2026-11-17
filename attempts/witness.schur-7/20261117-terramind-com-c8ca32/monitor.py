import datetime,pathlib,subprocess,json,re
P=pathlib.Path(__file__).resolve().parent
lines=subprocess.check_output(['ps','-axo','pid,ppid,state,pcpu,rss,command'],text=True).splitlines()
active=[]
for line in lines:
 fields=line.split(maxsplit=5)
 if len(fields)!=6:continue
 cmd=fields[5]
 if cmd.startswith(str(P/'venv/bin/python')) and 'sat.py child' in cmd or cmd.startswith('.terramind/scratch/schur7/local-v2'):
  active.append({'pid':fields[0],'state':fields[2],'cpu_percent':fields[3],'rss_kib':fields[4],'command':cmd})
local=(P/'local3.log').read_text().splitlines()
windows=(P/'windows3.log').read_text().splitlines()
pairs=[x for x in windows if x.startswith('PAIRED_WINDOW')]
row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local':local[-1] if local else None,'latest_completed_window':pairs[-1] if pairs else '1200 from windows2','active':active}
with (P/'monitor.log').open('a') as out:out.write(json.dumps(row)+'\n')
print(row['utc'],row['local'],row['latest_completed_window'])
print('active_search_processes',len(active),'rss_kib',sum(int(x['rss_kib']) for x in active))
