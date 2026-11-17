import copy, json,sys,tempfile,unittest
from pathlib import Path
from datetime import timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import *
ROOT=Path(__file__).resolve().parents[1]
class BuilderTests(unittest.TestCase):
 def setUp(self):
  self.data=load(ROOT);self.s=copy.deepcopy(self.data['sites'][0]);self.p=self.data['policy'];self.start=dt('2026-09-26T00:00:00Z');self.now=dt('2026-10-02T00:00:00Z')
 def rain(self,rows=None):return rain_check(self.s,rows if rows is not None else self.data['rain'],self.now,self.start,self.p)
 def test_exact_threshold(self):self.assertEqual(self.rain()['events'][0]['rain_24h_in'],'0.25')
 def test_two_separated_events(self):self.assertEqual(len(self.rain()['events']),2)
 def test_below_threshold(self):
  rows=copy.deepcopy(self.data['rain'])
  for r in rows:
   if r['rain_in']=='0.15':r['rain_in']='0.14'
  self.assertEqual(len(self.rain(rows)['events']),1)
 def test_zero_rain(self):
  rows=copy.deepcopy(self.data['rain'])
  for r in rows:r['rain_in']='0'
  self.assertEqual(self.rain(rows)['events'],[])
 def test_gap_escalation(self):self.assertEqual(self.rain(self.data['rain'][:20]+self.data['rain'][21:])['status'],'ESCALATE')
 def test_duplicate_escalation(self):self.assertEqual(self.rain(self.data['rain']+[self.data['rain'][10]])['status'],'ESCALATE')
 def test_negative_rain(self):
  rows=copy.deepcopy(self.data['rain']);rows[20]['rain_in']='-1';self.assertEqual(self.rain(rows)['status'],'ESCALATE')
 def test_units(self):
  rows=copy.deepcopy(self.data['rain']);rows[20]['units']='mm';self.assertEqual(self.rain(rows)['status'],'ESCALATE')
 def test_nan(self):
  rows=copy.deepcopy(self.data['rain']);rows[20]['rain_in']='NaN';self.assertEqual(self.rain(rows)['status'],'ESCALATE')
 def test_far_station(self):self.s['station']['lat']=36;self.assertEqual(self.rain()['status'],'ESCALATE')
 def test_unapproved_station(self):self.s['station']['approved_by']='';self.assertEqual(self.rain()['status'],'ESCALATE')
 def test_stale(self):self.now+=timedelta(days=2);self.assertIn('Rain observations stale or absent',self.rain()['issues'])
 def test_weekly_no_storm(self):
  self.s['schedule']='weekly';self.assertEqual(len(due_list(self.s,self.rain(),[],self.now)),1)
 def test_missed_storm(self):self.assertEqual(due_list(self.s,self.rain(),[],self.now)[1]['state'],'OVERDUE')
 def test_late_stays_late(self):
  log=[{'site_id':'S01','status':'COMPLETED','inspector':'person','completed_at':'2026-09-29T16:00:00Z'}]
  self.assertEqual(due_list(self.s,self.rain(),log,self.now)[1]['state'],'COMPLETED_LATE')
 def test_sunday_with_monday_overlap(self):
  self.assertEqual(stamp(storm_deadline(dt('2026-09-27T17:00:00Z'),self.s)),'2026-09-28T17:00:00+00:00')
 def test_entirely_weekend_window(self):
  self.assertEqual(stamp(storm_deadline(dt('2026-09-26T18:00:00Z'),self.s)),'2026-09-28T23:00:00+00:00')
 def test_major_corrective(self):self.assertEqual(corrective(self.data['deficiencies'][0],self.s)['completion_due'],'2026-10-04T18:00:00+00:00')
 def test_routine_next_business_day(self):
  d=copy.deepcopy(self.data['deficiencies'][0]);d['kind']='routine';self.assertEqual(corrective(d,self.s)['completion_due'],'2026-09-28T23:00:00+00:00')
 def test_unknown_kind_escalates(self):
  d=copy.deepcopy(self.data['deficiencies'][0]);d['kind']='invented';self.assertEqual(corrective(d,self.s)['status'],'ESCALATE')
 def test_discharge_escalates(self):self.assertEqual(corrective(self.data['deficiencies'][2],self.s)['status'],'ESCALATE')
 def test_24h_log(self):self.assertEqual(corrective(self.data['deficiencies'][0],self.s)['record_due'],'2026-09-28T18:00:00+00:00')
 def test_missing_clause(self):self.assertTrue(retrieve(self.s,[])['missing_or_conflicting_controls'])
 def test_conflict(self):self.assertTrue(retrieve(self.s,self.data['swppp']+[self.data['swppp'][0]])['missing_or_conflicting_controls'])
 def test_quote_fabrication(self):
  h=retrieve(self.s,self.data['swppp'])['hits'];reply={'items':[{'section_id':x['id'],'quote':'fabrication','action':x['action']} for x in h]}
  with self.assertRaises(ValueError):validate_draft(reply,h)
 def test_prompt_injection_completion(self):
  with self.assertRaises(PermissionError):dispatch('complete_inspection',{'role':'inspector'},{'policy':self.p,'tools':{'complete_inspection':lambda:True}})
 def test_forged_sign_tool(self):
  with self.assertRaises(PermissionError):authorize('sign',self.p)
 def test_extra_status_field(self):
  with self.assertRaises(ValueError):validate_draft({'items':[],'inspection_status':'COMPLETED'},[])
 def test_naive_time_rejected(self):
  with self.assertRaises(ValueError):dt('2026-09-27T12:00:00')
 def test_context_arguments_denied(self):
  with self.assertRaises(ValueError):dispatch('check_rain',{'threshold':100},{'policy':self.p,'tools':{}})
 def test_unsupported_schedule(self):
  self.data['sites'][0]['schedule']='reduced'
  with self.assertRaises(ValueError):validate_inputs(self.data)
 def test_empty_workweek(self):
  self.data['sites'][0]['workdays']=[]
  with self.assertRaises(ValueError):validate_inputs(self.data)
 def test_multiday_escalation(self):
  rows=copy.deepcopy(self.data['rain'])
  for r in rows:
   if r['station_id']=='G01' and r['end_utc']=='2026-09-28T18:00:00+00:00':r['rain_in']='0.3'
  self.assertTrue(any('multi-day' in x for x in self.rain(rows)['issues']))
 def test_holiday(self):
  self.s['holidays']=['2026-09-28']
  self.assertEqual(stamp(storm_deadline(dt('2026-09-26T18:00:00Z'),self.s)),'2026-09-29T23:00:00+00:00')
 def test_full_path_and_replay(self):
  from agent import run
  from replay import verify
  before={str(p):sha(p) for p in (ROOT/'data').glob('*')}
  with tempfile.TemporaryDirectory() as temp:
   reports,out=run(out=Path(temp)/'run')
   self.assertEqual(len(reports),3)
   self.assertTrue(all(x['inspection_status']=='NOT_COMPLETED' for x in reports))
   self.assertEqual(verify(out)['deterministic_tools_replayed'],12)
   self.assertEqual(before,{str(p):sha(p) for p in (ROOT/'data').glob('*')})
   (out/'reports.json').write_text('tampered')
   with self.assertRaises(ValueError):verify(out)
if __name__=='__main__':unittest.main()
