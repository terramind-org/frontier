"""Event-driven log reader. Exit only after the search wrapper reports exit status."""
import pathlib, select
p=pathlib.Path('.terramind/scratch/matmul5/search.out')
with p.open() as f:
 q=select.kqueue()
 q.control([select.kevent(f.fileno(),filter=select.KQ_FILTER_VNODE,flags=select.KQ_EV_ADD|select.KQ_EV_CLEAR,fflags=select.KQ_NOTE_WRITE)],0,0)
 while True:
  s=f.read()
  if s: print(s,end='',flush=True)
  if 'search_exit_status=' in s: break
  q.control(None,1,None)
