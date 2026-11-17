"""Validate audit chain, input/output integrity and deterministic tool replay. No LLM calls."""
import argparse,json,hashlib
from pathlib import Path
from engine import *
ROOT=Path(__file__).resolve().parent

def verify(folder,root=ROOT):
 folder=Path(folder);root=Path(root);records=[json.loads(x) for x in (folder/'audit.jsonl').read_text().splitlines()];prev='0'*64
 if not records or records[0]['event']!='start' or records[-1]['event']!='finish':raise ValueError('Incomplete audit')
 for r in records:
  body={k:v for k,v in r.items() if k!='hash'}
  if body['previous_hash']!=prev or hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()!=r['hash']:raise ValueError('Audit chain mismatch')
  prev=r['hash']
 start=records[0]
 for p,digest in start['input_hashes'].items():
  if sha(root/p)!=digest:raise ValueError('Input changed: '+p)
 for p,digest in records[-1]['output_hashes'].items():
  if sha(folder/p)!=digest:raise ValueError('Output changed: '+p)
 data=load(root);now=dt(start['as_of']);begin=dt(start['start']);checked=0
 for r in records:
  if r['event']!='tool':continue
  site=next(x for x in data['sites'] if x['id']==r['site_id']);tool=r['tool']
  if tool=='check_rain':expected=rain_check(site,data['rain'],now,begin,data['policy'])
  elif tool=='list_due':expected=due_list(site,rain_check(site,data['rain'],now,begin,data['policy']),data['inspections'],now)
  elif tool=='retrieve_swppp':expected=retrieve(site,data['swppp'])
  elif tool=='compute_actions':expected=[corrective(d,site) for d in data['deficiencies'] if d['site_id']==site['id'] and dt(d['discovered_at'])<=now]
  else:continue
  if expected!=r['result']:raise ValueError('Tool replay mismatch: '+tool)
  checked+=1
 return {'audit_chain':'PASS','input_output_hashes':'PASS','deterministic_tools_replayed':checked,'model_regenerated':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();print(json.dumps(verify(a.folder),indent=2))
