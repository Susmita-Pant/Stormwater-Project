"""Bounded multi-tool agent, local Ollama or explicit deterministic fixture mode."""
import argparse, hashlib, json, time, urllib.request, uuid, html
from pathlib import Path
from engine import load, dt, sha, rain_check, due_list, retrieve, corrective, validate_draft, authorize, dispatch, validate_inputs
ROOT=Path(__file__).resolve().parent

def ask(payload,model):
    request=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps({
      'model':model,'stream':False,'format':'json','options':{'temperature':0},
      'messages':[{'role':'system','content':(ROOT/'prompts/system.txt').read_text()},
                  {'role':'user','content':json.dumps(payload)}]}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=120) as r: body=json.load(r)
    return json.loads(body['message']['content'])

class Audit:
    def __init__(self,path):self.path=path;self.previous='0'*64
    def write(self,event):
        record={'previous_hash':self.previous,**event}
        self.previous=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()
        record['hash']=self.previous
        with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')

def run(root=ROOT,mode='fixture',as_of='2026-10-02T00:00:00+00:00',start='2026-09-26T00:00:00+00:00',model='llama3.2:3b',out=None):
    root=Path(root); data=load(root);validate_inputs(data);now=dt(as_of);begin=dt(start)
    if now<begin:raise ValueError('as_of precedes start')
    runid=uuid.uuid4().hex;out=Path(out or root/'outputs'/runid);out.mkdir(parents=True,exist_ok=False)
    inputs={str(p.relative_to(root)):sha(p) for folder in ['data','prompts','sources'] for p in sorted((root/folder).glob('*')) if p.is_file()}
    inputs.update({p.name:sha(p) for p in sorted(root.glob('*.py'))})
    audit=Audit(out/'audit.jsonl');audit.write({'event':'start','run_id':runid,'mode':mode,'model':model if mode=='ollama' else None,'as_of':as_of,'start':start,'input_hashes':inputs})
    reports=[];started=time.perf_counter()
    for site in data['sites']:
        state={};issues=[];trace=[]
        def draft():
            hits=state['retrieve_swppp']['hits']
            if mode=='fixture':reply={'items':[{'section_id':h['id'],'quote':h['text'],'action':h['action']} for h in hits]}
            else:reply=ask({'task':'draft','schema':{'items':[{'section_id':'source id','quote':'exact source text','action':'exact source action'}]},'sources':hits},model)
            print("AI DRAFT RESPONSE:", site['id'], repr(reply))
            return validate_draft(reply,hits)
        tools={
          'check_rain':lambda:rain_check(site,data['rain'],now,begin,data['policy']),
          'list_due':lambda:due_list(site,state['check_rain'],data['inspections'],now),
          'retrieve_swppp':lambda:retrieve(site,data['swppp']),
          'compute_actions':lambda:[corrective(d,site) for d in data['deficiencies'] if d['site_id']==site['id'] and dt(d['discovered_at'])<=now],
          'draft_report':draft}
        context={'policy':data['policy'],'tools':tools}
        # Every stage is mandatory. The model chooses between available independent tools, but cannot skip gates.
        for step in range(5):
            pending=[t for t in tools if t not in state]
            allowed=[t for t in pending if (t!='list_due' or 'check_rain' in state) and (t!='draft_report' or 'retrieve_swppp' in state)]
            tool=allowed[0];reason='Required workflow stage (fixture mode)'
            if mode=='ollama':
                try:
                    choice=ask({'task':'route','allowed_tools':allowed,'schema':{'tool':'one allowed tool','reason':'brief reason'},'site_id':site['id']},model)
                    tool=choice['tool'];reason=choice['reason']
                    authorize(tool,data['policy'])
                    if tool not in allowed:raise ValueError('Dependency or repeated tool violation')
                except Exception as e:
                    issues.append('Model route rejected: '+str(e));tool=allowed[0];reason='Deterministic recovery after model failure'
            t0=time.perf_counter()
            try:result=dispatch(tool,{},context)
            except Exception as e:
                issues.append(tool+': '+str(e));result=[] if tool=='draft_report' else {'status':'ESCALATE','error':str(e)}
            state[tool]=result;trace.append(tool)
            audit.write({'event':'tool','site_id':site['id'],'tool':tool,'reason':reason,'args':{},'result':result,'latency_seconds':time.perf_counter()-t0})
        rain=state['check_rain'];retrieved=state['retrieve_swppp'];actions=state['compute_actions']
        issues+=rain.get('issues',[])
        if retrieved.get('missing_or_conflicting_controls'):issues.append('SWPPP missing/conflicting control sections')
        if any(a['status']=='ESCALATE' for a in actions):issues.append('Deficiency needs inspector assessment')
        report={'schema_version':'1.0','run_id':runid,'site_id':site['id'],'site_name':site['name'],
          'status':'ESCALATE' if issues else 'DRAFT','inspection_status':'NOT_COMPLETED','inspector_of_record':site['inspector'],
          'mode':mode,'as_of':as_of,'rain_evidence':rain,'due_list':state['list_due'],
          'checklist':state['draft_report'],'corrective_actions':actions,'escalations':issues,
          'field_observations':None,'inspection_started_at':None,'inspection_finished_at':None,'signature':None,
          'limitations':['Preparation draft only. Inspector must enter observations and certify in the external form.',
          'Baseline Part 4.2 only; snowmelt, dewatering and special/reduced schedules need domain review.',
          'Consecutive wet dates escalate; hourly crossings use conservative earliest-hour deadlines.'], 'tool_trace':trace}
        reports.append(report)
    (out/'reports.json').write_text(json.dumps(reports,indent=2))
    import csv
    with (out/'due_list.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['site_id','kind','due_utc','state','review_status'])
        for r in reports:
            for due in r['due_list']:w.writerow([r['site_id'],due['kind'],due['due_utc'],due['state'],r['status']])
    sections=[]
    for r in reports:
        lines=['<h2>'+html.escape(r['site_id']+' - '+r['site_name'])+'</h2>', '<p><strong>'+r['status']+' | NOT COMPLETED</strong></p>']
        lines.append('<p>Inspector: '+html.escape(r['inspector_of_record'])+' | Station: '+html.escape(r['rain_evidence']['station_id'])+' | Distance (km): '+str(r['rain_evidence']['distance_km'])+'</p>')
        lines.append('<table><tr><th>Inspection</th><th>Due UTC</th><th>State</th></tr>')
        for d in r['due_list']:lines.append('<tr>'+''.join('<td>'+html.escape(str(d[k]))+'</td>' for k in ['kind','due_utc','state'])+'</tr>')
        lines.append('</table><h3>Checklist for inspector review</h3><ul>')
        for c in r['checklist']:lines.append('<li>'+html.escape(c['task'])+'<br><small>'+html.escape(c['citation']+' | '+c['version'])+'</small></li>')
        lines.append('</ul><h3>Corrective actions</h3>')
        for a in r['corrective_actions']:
            lines.append('<p><strong>'+html.escape(a['id']+' | '+a['status'])+'</strong><br>'+html.escape(a['note'])+'</p>')
            lines.append('<p>Completion due (UTC): '+html.escape(str(a['completion_due'] or 'Human review required'))+'<br>Initial record due (UTC): '+html.escape(str(a['record_due'] or 'See inspector requirements'))+'<br>Basis: '+html.escape(str(a['citation'] or a.get('reason','Needs review')))+'</p>')
        lines.append('<h3>Needs review</h3><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in r['escalations'])+'</ul>')
        sections.append(''.join(lines))
    (out/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Stormwater inspection preparation</title><style>body{font:17px Arial;max-width:1000px;margin:40px auto;padding:20px;color:#18322e}table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #ccc;text-align:left}h2{margin-top:48px}small{color:#555}p{overflow-wrap:anywhere}</style><h1>Stormwater inspection preparation</h1><p>Educational synthetic replay | Mode: '+mode+' | DRAFT - NOT AN INSPECTION RECORD</p>'+''.join(sections)+'</html>')
    metrics={'mode':mode,'runtime_seconds':time.perf_counter()-started,'site_count':len(reports),'energy_kwh':None,'operator_minutes_saved':None,'live_model_validated':False}
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    hashes={p.name:sha(p) for p in out.iterdir() if p.name!='audit.jsonl'}
    audit.write({'event':'finish','output_hashes':hashes,'metrics':metrics})
    print('Output folder:',out);return reports,out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['fixture','ollama'],default='fixture');p.add_argument('--as-of',default='2026-10-02T00:00:00+00:00');p.add_argument('--start',default='2026-09-26T00:00:00+00:00');p.add_argument('--model',default='llama3.2:3b');p.add_argument('--out');a=p.parse_args()
    run(mode=a.mode,as_of=a.as_of,start=a.start,model=a.model,out=a.out)
