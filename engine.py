"""Deterministic tools. Educational EPA CGP Part 4.2 baseline scope only."""
import csv, hashlib, json, math
from datetime import datetime, timedelta, time, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo
UTC = timezone.utc

def dt(s):
    v = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if v.tzinfo is None: raise ValueError('Timezone is required')
    return v.astimezone(UTC)

def stamp(v): return v.astimezone(UTC).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def load(root):
    root=Path(root)
    return {k:json.loads((root/'data'/f'{k}.json').read_text()) for k in ['sites','swppp','deficiencies','inspections','policy']} | {'rain':read_csv(root/'data/rain.csv')}

def distance_km(a,b):
    lat1,lon1,lat2,lon2=map(math.radians,[a['lat'],a['lon'],b['lat'],b['lon']])
    h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return round(6371.0088*2*math.asin(min(1,math.sqrt(h))),3)

def next_business_close(when,site):
    z=ZoneInfo(site['timezone']); d=when.astimezone(z).date()+timedelta(days=1)
    while d.weekday() not in site['workdays'] or d.isoformat() in site['holidays']: d+=timedelta(days=1)
    return datetime.combine(d,time.fromisoformat(site['close']),z).astimezone(UTC)

def storm_deadline(trigger,site):
    """Elapsed 24h; footnote 67 exception only if the WHOLE window has no working hours."""
    end=trigger+timedelta(hours=24);z=ZoneInfo(site['timezone']);d=trigger.astimezone(z).date()
    while d<=end.astimezone(z).date():
        if d.weekday() in site['workdays'] and d.isoformat() not in site['holidays']:
            a=datetime.combine(d,time.fromisoformat(site['open']),z).astimezone(UTC)
            b=datetime.combine(d,time.fromisoformat(site['close']),z).astimezone(UTC)
            if max(a,trigger)<min(b,end): return end
        d+=timedelta(days=1)
    return next_business_close(end-timedelta(microseconds=1),site)

def rain_check(site,rows,as_of,start,policy):
    """Non-overlapping, complete hourly increments only. Never sum raw METAR p01i rows."""
    evidence={'station_id':site['station']['id'],'distance_km':distance_km(site,site['station']),
              'representative_approved_by':site['station']['approved_by'],'source':site['station']['source'],
              'window_start':stamp(start),'as_of':stamp(as_of),'trigger_rule':'EPA CGP 4.2.2a; 4.2.3a'}
    issues=[]; vals={}; times=[]
    if not site['station']['approved_by']: issues.append('Station representativeness not approved')
    if evidence['distance_km']>policy['max_station_km']: issues.append('Station exceeds project distance screen (not an EPA limit)')
    for r in rows:
        if r['station_id']!=site['station']['id']: continue
        try:
            t=dt(r['end_utc']);v=Decimal(r['rain_in'])
            if t>as_of: continue
            if t<=start-timedelta(hours=24): continue
            if r['units']!='in' or r['quality']!='ok' or not v.is_finite() or v<0: raise ValueError('Invalid rain amount, units or quality')
            if t in vals: raise ValueError('Duplicate hourly interval')
            if t.minute or t.second or t.microsecond: raise ValueError('Hour-aligned intervals required')
            if dt(r['start_utc'])!=t-timedelta(hours=1): raise ValueError('Non-hourly interval')
            vals[t]=v
        except (ValueError,ArithmeticError,KeyError) as e: issues.append(str(e))
    t=start-timedelta(hours=23)
    while t<=as_of:
        if t not in vals: issues.append('Missing hourly rain interval ending '+stamp(t))
        times.append(t);t+=timedelta(hours=1)
    evidence['last_observation']=stamp(max(vals)) if vals else None
    if not vals or (as_of-max(vals)).total_seconds()>policy['max_age_hours']*3600: issues.append('Rain observations stale or absent')
    events=[];above=False;wet_dates=set()
    for t in times:
        window=[t-timedelta(hours=i) for i in range(24)]
        if not all(x in vals for x in window): above=False;continue
        total=sum((vals[x] for x in window),Decimal('0'))
        active=total>=Decimal(policy['rain_threshold_in'])
        if t>=start and vals.get(t,0)>0:wet_dates.add(t.astimezone(ZoneInfo(site['timezone'])).date())
        if t>=start and active and not above:
            # Hourly data bounds threshold crossing to (t-1h,t]. Use earliest bound for conservative due clock.
            trigger=t-timedelta(hours=1)
            events.append({'event_id':site['id']+'@'+stamp(t),'detected_at':stamp(t),
                           'trigger_earliest':stamp(trigger),'rain_24h_in':str(total),
                           'due_utc':stamp(storm_deadline(trigger,site)),
                           'deadline_basis':'Conservative start of crossing hour; CGP 4.2.2a and footnote 67'})
        above=active
    # Multi-day patterns are not silently reduced to a single crossing.
    if any(d+timedelta(days=1) in wet_dates for d in wet_dates):
        issues.append('Rain on consecutive local dates: multi-day storm review required under CGP 4.2.2a')
    evidence['issues']=sorted(set(issues));evidence['events']=events
    evidence['status']='ESCALATE' if issues else 'OK'
    return evidence

def due_list(site,rain,inspections,as_of):
    done=sorted([dt(i['completed_at']) for i in inspections if i['site_id']==site['id'] and i['status']=='COMPLETED' and i.get('inspector') and dt(i['completed_at'])<=as_of])
    last=done[-1] if done else dt(site['baseline_inspection'])
    days=7 if site['schedule']=='weekly' else 14
    z=ZoneInfo(site['timezone']);regular=(last.astimezone(z)+timedelta(days=days)).astimezone(UTC)
    out=[{'kind':'routine','due_utc':stamp(regular),'state':'OVERDUE' if as_of>regular else 'UPCOMING',
          'basis':'Conservative same-time calendar interval; EPA CGP 4.2.1/4.2.2'}]
    if site['schedule']=='biweekly_rain':
        for e in rain['events']:
            completions=[x for x in done if x>=dt(e['detected_at'])]
            completed=completions[0] if completions else None
            state=('COMPLETED_ON_TIME' if completed<=dt(e['due_utc']) else 'COMPLETED_LATE') if completed else ('OVERDUE' if as_of>dt(e['due_utc']) else 'DUE')
            out.append({'kind':'storm',**e,'state':state,'completed_at':stamp(completed) if completed else None})
    return out

def corrective(d,site):
    t=dt(d['discovered_at']);kind=d.get('kind');review=d.get('domain_confirmed',False)
    result={'id':d['id'],'note':d['note'],'discovered_at':stamp(t),'status':'DRAFT',
            'immediate_action':'Inspector/operator must assess and take appropriate immediate steps.',
            'completion_due':None,'record_due':None,'citation':None}
    if d.get('possible_discharge') or kind=='dewatering' or not review or kind not in ['routine','minor_corrective','major_corrective']:
        result.update(status='ESCALATE',reason='Possible discharge, unsupported condition, or unconfirmed classification; contact inspector now.')
        return result
    result['completion_due']=stamp((t.astimezone(ZoneInfo(site['timezone']))+timedelta(days=7)).astimezone(UTC) if kind=='major_corrective' else next_business_close(t,site))
    result['citation']='EPA CGP 2.1.4b' if kind=='routine' else 'EPA CGP 5.2.1b-c'
    if kind!='routine':result['record_due']=stamp(t+timedelta(hours=24));result['record_citation']='EPA CGP 5.4.1a'
    return result

def retrieve(site,corpus):
    hits=[];missing=[]
    for control in site['controls']:
        found=[c for c in corpus if c['site_id']==site['id'] and c['version']==site['swppp_version'] and c['control']==control]
        if len(found)!=1:missing.append(control)
        else:hits.extend(found)
    return {'hits':hits,'missing_or_conflicting_controls':missing}

def validate_draft(reply,hits):
    """Only exact source quotations and whitelisted actions enter the output. No free-text calculations."""
    if set(reply)!={'items'} or not isinstance(reply['items'],list):raise ValueError('Invalid output contract')
    expected={h['id']:h for h in hits};seen=set();out=[]
    for item in reply['items']:
        if set(item)!={'section_id','quote','action'}:raise ValueError('Unexpected draft field')
        h=expected.get(item['section_id'])
        if not h or item['section_id'] in seen or item['quote']!=h['text'] or item['action']!=h['action']:raise ValueError('Unverified source, duplicate or altered action')
        seen.add(h['id']);out.append({'control':h['control'],'task':item['action'],'quote':item['quote'],'citation':h['id'],'version':h['version']})
    if seen!=set(expected):raise ValueError('Omitted required control')
    return out

def authorize(tool,policy):
    if tool not in policy['agent_tools']: raise PermissionError('Agent tool denied: '+str(tool))

def dispatch(tool,args,context):
    authorize(tool,context['policy'])
    if args:raise ValueError('Tools use validated context; model-supplied arguments prohibited')
    return context['tools'][tool]()

def validate_inputs(data):
    ids=[s['id'] for s in data['sites']]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate site IDs')
    for s in data['sites']:
        if s['schedule'] not in ['weekly','biweekly_rain']:raise ValueError('Unsupported inspection schedule')
        if not s['workdays'] or any(type(d)!=int or not 0<=d<=6 for d in s['workdays']):raise ValueError('Invalid workweek')
        if time.fromisoformat(s['open'])>=time.fromisoformat(s['close']):raise ValueError('Overnight/invalid work shifts unsupported')
        ZoneInfo(s['timezone']);dt(s['baseline_inspection'])
        for obj in [s,s['station']]:
            if not (-90<=obj['lat']<=90 and -180<=obj['lon']<=180):raise ValueError('Invalid coordinates')
    for key in ['deficiencies','inspections','swppp']:
        if any(r['site_id'] not in ids for r in data[key]):raise ValueError('Unknown site reference')
