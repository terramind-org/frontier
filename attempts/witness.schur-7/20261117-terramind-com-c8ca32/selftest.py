import importlib.util,pathlib,sys,datetime
P=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('schur_sat',P/'sat.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
print('ENCODING_SELFTEST',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
for n,k,expected in [(1,1,True),(2,1,False),(4,2,True),(5,2,False)]:
 actual=m.child({'label':f'selftest_n{n}_k{k}','n':n,'k':k,'free':list(range(1,n+1))})
 assert actual==expected,(n,k,actual,expected)
 print('PASS',n,k,expected,flush=True)
print('ALL FOUR ENCODING SELFTESTS PASS',flush=True)
