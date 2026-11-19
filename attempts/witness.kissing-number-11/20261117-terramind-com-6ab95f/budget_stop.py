"""Arm within 60 seconds of the shared deadline and stop the main process.

The main search starts its loop timer after its exact self-test, whereas the
worker budget starts at process launch. This removes that startup overrun.
The all-point process already uses the shared absolute deadline itself.
"""
import datetime
import json
import os
from pathlib import Path
import select
import signal
import time
root=Path(__file__).resolve().parent
start=datetime.datetime.fromisoformat((root/'launch-utc.txt').read_text().strip().replace('Z','+00:00')).timestamp()
remaining=start+7200-time.time()
if remaining>60:raise SystemExit('Arm this guard only in the final 60 seconds')
select.select([],[],[],max(0,remaining-.02))
pid=int((root/'search.pid').read_text())
action='already exited'
if not (root/'search.exit').exists():
    try:
        os.kill(pid,signal.SIGTERM);action='SIGTERM sent at shared wall-clock limit'
    except ProcessLookupError:pass
now=time.time()
report={'pid':pid,'action':action,'stopped_utc':datetime.datetime.fromtimestamp(now,datetime.timezone.utc).isoformat(),
        'elapsed_since_launch_seconds':now-start,'deadline_epoch':start+7200}
(root/'budget-stop.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
