#!/usr/bin/env python3
"""Evaluate an experiment from concrete evidence artifacts, never run.json booleans."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = {
 'cargo_modbus_pcap':'cargo-modbus.pcap', 'pms_modbus_pcap':'pms-modbus.pcap', 'propulsion_modbus_pcap':'propulsion-modbus.pcap',
 'cargo_state_timeline':'cargo-state.jsonl', 'pms_state_timeline':'pms-state.jsonl', 'propulsion_state_timeline':'propulsion-state.jsonl',
 'vessel_state_timeline':'vessel-state.jsonl', 'alarm_timeline':'alarm-timeline.jsonl', 'cargo_state_csv':'cargo-state.csv',
 'process_residual_json':'process-residual.json', 'modbus_conn_log':'conn.log', 'conduit_classification_json':'conduit-classification.json',
 'historian_freshness_before':'freshness-before.json', 'historian_freshness_after':'freshness-after.json',
}
PCAP_KEYS={'cargo_modbus_pcap','pms_modbus_pcap','propulsion_modbus_pcap'}
JSON_KEYS={'process_residual_json','conduit_classification_json','historian_freshness_before','historian_freshness_after'}
JSONL_KEYS={'cargo_state_timeline','pms_state_timeline','propulsion_state_timeline','vessel_state_timeline','alarm_timeline'}
PCAP_MAGICS={b'\xd4\xc3\xb2\xa1',b'\xa1\xb2\xc3\xd4',b'\x4d\x3c\xb2\xa1',b'\xa1\xb2\x3c\x4d',b'\x0a\x0d\x0d\x0a'}

def sha256(path:Path)->str:
 h=hashlib.sha256();
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()

def jsonl(path:Path)->list[dict[str,Any]]:
 out=[]
 for i,line in enumerate(path.read_text(errors='strict').splitlines(),1):
  if not line.strip(): continue
  item=json.loads(line)
  if not isinstance(item,dict): raise ValueError(f'line {i} is not a JSON object')
  out.append(item)
 return out

def resolve(run:Path,key:str,meta:dict[str,Any])->Path:
 rel=(meta.get('evidence_files') or {}).get(key, DEFAULT_FILES.get(key,key))
 p=(run/rel).resolve(); base=run.resolve()
 if p != base and base not in p.parents: raise ValueError(f'evidence path escapes run directory: {rel}')
 return p

def validate_artifact(key:str,path:Path)->dict[str,Any]:
 if not path.is_file() or path.stat().st_size==0: raise ValueError('missing or empty')
 detail={'path':str(path.name),'bytes':path.stat().st_size,'sha256':sha256(path)}
 if key in PCAP_KEYS:
  if path.read_bytes()[:4] not in PCAP_MAGICS: raise ValueError('not recognized PCAP/PCAPNG magic')
 elif key in JSON_KEYS:
  val=json.loads(path.read_text()); detail['json_type']=type(val).__name__
 elif key in JSONL_KEYS:
  rows=jsonl(path); 
  if not rows: raise ValueError('JSONL contains no records')
  detail['records']=len(rows)
 elif key=='cargo_state_csv':
  head=path.read_text().splitlines()[0] if path.read_text().splitlines() else ''
  for col in ('time_s','levelSource','flowMeasured'):
   if col not in head.split(','): raise ValueError(f'CSV missing {col}')
 elif key=='modbus_conn_log':
  text=path.read_text(errors='ignore')
  if '#fields' not in text: raise ValueError('Zeek conn.log #fields header missing')
 return detail

def states(path:Path)->list[dict[str,Any]]:
 return [x.get('state',x) for x in jsonl(path) if isinstance(x.get('state',x),dict)]

def alarms(path:Path)->list[dict[str,Any]]: return jsonl(path)

def experiment_checks(exp_id:str,run:Path,meta:dict[str,Any])->list[dict[str,Any]]:
 checks=[]
 def add(name,ok,detail): checks.append({'name':name,'pass':bool(ok),'detail':detail})
 if exp_id in {'EXP-CARGO-NORMAL','EXP-CARGO-BLOCKED-FLOW'}:
  rows=states(resolve(run,'cargo_state_timeline',meta))
  if exp_id=='EXP-CARGO-NORMAL':
   ok=any(bool(r.get('pumpFeedback')) and bool(r.get('valveFeedback')) and float(r.get('flowMeasured',0))>0.05 for r in rows)
   add('normal cargo causal state observed',ok,'pump+valve feedback true with positive measured flow')
  else:
   ok=any(bool(r.get('pumpFeedback')) and bool(r.get('valveFeedback')) and abs(float(r.get('flowMeasured',999)))<=0.05 for r in rows)
   add('blocked-flow process contradiction observed',ok,'healthy pump/valve feedback with near-zero flow')
   al=alarms(resolve(run,'alarm_timeline',meta)); aok=any(x.get('alarm_id') in {'CARGO_NO_FLOW','CARGO_FLOW_MISMATCH'} and str(x.get('transition','')).startswith('ACTIVE') for x in al)
   add('blocked-flow alarm observed',aok,'active no-flow/flow-mismatch alarm transition')
 elif exp_id=='EXP-CARGO-SENSOR-BIAS':
  payload=json.loads(resolve(run,'process_residual_json',meta).read_text()); vals=payload.get('results',payload if isinstance(payload,list) else [])
  add('process residual anomaly observed',any(bool(x.get('anomaly')) for x in vals if isinstance(x,dict)),'at least one independent mass-balance residual exceeded threshold')
 elif exp_id=='EXP-UNEXPECTED-MODBUS-SOURCE':
  payload=json.loads(resolve(run,'conduit_classification_json',meta).read_text())
  add('unexpected Modbus source observed',any(x.get('classification')=='UNEXPECTED' for x in payload if isinstance(x,dict)),'classifier output contains an UNEXPECTED connection')
 elif exp_id=='EXP-OPCUA-STALE-CARGO':
  before=json.loads(resolve(run,'historian_freshness_before',meta).read_text()); after=json.loads(resolve(run,'historian_freshness_after',meta).read_text())
  add('historian transitions fresh to stale',before.get('fresh') is True and after.get('fresh') is False,'fresh-before=true and stale-after=false')
 return checks

def evaluate(run:Path)->dict[str,Any]:
 meta=json.loads((run/'run.json').read_text())
 experiments=json.loads((ROOT/'experiments/manifest.json').read_text())['experiments']
 exp=next(x for x in experiments if x['id']==meta['experiment_id'])
 artifacts={}; missing=[]; invalid=[]
 for key in exp['required_evidence']:
  p=resolve(run,key,meta)
  try: artifacts[key]=validate_artifact(key,p)
  except Exception as exc:
   (missing if not p.exists() else invalid).append({'key':key,'path':str(p.relative_to(run)) if p.is_relative_to(run) else str(p),'reason':str(exc)})
 checks=[]
 if not missing and not invalid:
  try: checks=experiment_checks(exp['id'],run,meta)
  except Exception as exc: checks=[{'name':'experiment-specific checks','pass':False,'detail':f'{type(exc).__name__}: {exc}'}]
 required=len(exp['required_evidence']); valid=len(artifacts)
 passed=(valid==required and all(x['pass'] for x in checks))
 out={'schema_version':2,'experiment_id':exp['id'],'run_git':meta.get('git'),'release_manifest_sha256':meta.get('release_manifest_sha256'),
      'evidence_completeness':valid/required if required else 1.0,'artifacts':artifacts,'missing_evidence':missing,'invalid_evidence':invalid,'experiment_checks':checks,'pass':passed}
 (run/'evidence-index.json').write_text(json.dumps({'schema_version':1,'experiment_id':exp['id'],'artifacts':artifacts},indent=2)+'\n')
 (run/'evaluation.json').write_text(json.dumps(out,indent=2)+'\n')
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('run_dir'); a=ap.parse_args(); out=evaluate(Path(a.run_dir)); print(json.dumps(out,indent=2)); raise SystemExit(0 if out['pass'] else 2)
if __name__=='__main__': main()
