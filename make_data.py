"""Project-specific synthetic generator inspired by lab make_data.py pattern; not instructor data."""
import csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
 d=ROOT/'data';d.mkdir(exist_ok=True)
 def save(n,x):(d/(n+'.json')).write_text(json.dumps(x,indent=2))
 sites=[];clauses=[]
 for ident,name,lat,mode in [('S01','Mesa access road',35.05,'biweekly_rain'),('S02','Arroyo staging area',35.08,'weekly'),('S03','North utility trench',35.12,'biweekly_rain')]:
  sites.append({'id':ident,'name':name,'lat':lat,'lon':-106.62,'timezone':'America/Denver',
   'schedule':mode,'baseline_inspection':'2026-09-18T16:00:00+00:00','swppp_version':'teaching-v1',
   'inspector':'Synthetic inspector '+ident,'controls':['silt_fence','inlet_protection','stabilized_exit'],
   'workdays':[0,1,2,3,4],'open':'07:00','close':'17:00','holidays':[],
   'station':{'id':'G'+ident[1:],'lat':lat+.01,'lon':-106.63,'approved_by':'Synthetic domain lead', 'source':'SYNTHETIC hourly gauge; not public observations'}})
  for sec,ctrl,txt,action in [
   ('3.1','silt_fence','Inspect perimeter silt fence for tears, undermining and sediment buildup.','Check fence condition and record observed defects.'),
   ('3.2','inlet_protection','Inspect inlet protection for damage, blockage and bypass flow.','Check inlet protection and document blockage or bypass.'),
   ('3.3','stabilized_exit','Inspect the stabilized exit for sediment tracking onto adjacent pavement.','Check the exit and document visible sediment tracking.')]:
   clauses.append({'id':ident+' SWPPP '+sec,'site_id':ident,'version':'teaching-v1','control':ctrl,'text':txt,'action':action})
 save('sites',sites);save('swppp',clauses)
 save('policy',{'version':'1.0','agent_tools':['check_rain','list_due','retrieve_swppp','compute_actions','draft_report'],
 'rain_threshold_in':'0.25','max_station_km':10,'max_age_hours':2,
 'prohibited':['complete_inspection','sign','submit','write_source'],'permit_scope':'EPA 2022 CGP Part 4.2 baseline only'})
 save('inspections',[{'site_id':'S02','status':'COMPLETED','completed_at':'2026-09-25T16:00:00+00:00','inspector':'Synthetic inspector S02'}])
 save('deficiencies',[
 {'id':'D01','site_id':'S01','discovered_at':'2026-09-27T18:00:00+00:00','kind':'major_corrective','domain_confirmed':True,'possible_discharge':False,'note':'Silt fence collapsed; replacement needed.'},
 {'id':'D02','site_id':'S02','discovered_at':'2026-09-28T18:00:00+00:00','kind':'routine','domain_confirmed':True,'possible_discharge':False,'note':'Remove debris at inlet protection.'},
 {'id':'D03','site_id':'S03','discovered_at':'2026-09-28T18:00:00+00:00','kind':'minor_corrective','domain_confirmed':False,'possible_discharge':True,'note':'Possible muddy discharge beyond site boundary. Inspector assessment required.'}])
 start=datetime(2026,9,25,tzinfo=timezone.utc)
 with (d/'rain.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['station_id','start_utc','end_utc','rain_in','units','quality'])
  for station in ['G01','G02','G03']:
   for h in range(24*8+1):
    t=start+timedelta(hours=h)
    if station=='G03' and t==datetime(2026,9,27,17,tzinfo=timezone.utc):continue
    v='0.00'
    if t==datetime(2026,9,27,17,tzinfo=timezone.utc):v='0.10'
    if t==datetime(2026,9,27,18,tzinfo=timezone.utc):v='0.15'
    if t==datetime(2026,9,30,18,tzinfo=timezone.utc):v='0.30'
    w.writerow([station,(t-timedelta(hours=1)).isoformat(),t.isoformat(),v,'in','ok'])
 print('Synthetic fixtures generated. Existing data files replaced; outputs untouched.')
if __name__=='__main__':main()
