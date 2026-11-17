"""Clip an added search to the original 120-minute envelope, with five seconds spare."""
import pathlib,json,datetime,time,sys
p=pathlib.Path(__file__).resolve().parent
start=(p/'calibration.start').read_text().strip()
deadline=datetime.datetime.fromisoformat(start).timestamp()+7200
print(max(0,int(min(float(sys.argv[1]),deadline-time.time()-5))))
