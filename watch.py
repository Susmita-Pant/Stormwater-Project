"""Poll atomically replaced local exports; reevaluate clocks each cycle, even without new rain."""
import argparse,time
from datetime import datetime,timezone,timedelta
from agent import run
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--interval-seconds',type=int,default=3600);p.add_argument('--once',action='store_true');p.add_argument('--mode',choices=['fixture','ollama'],default='ollama');a=p.parse_args()
 if a.interval_seconds<60:raise SystemExit('Use interval >= 60 seconds')
 while True:
  now=datetime.now(timezone.utc).replace(minute=0,second=0,microsecond=0)
  run(mode=a.mode,as_of=now.isoformat(),start=(now-timedelta(days=7)).isoformat())
  if a.once:break
  time.sleep(a.interval_seconds)
