#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_FILES={
 'cargo_modbus_pcap':'cargo-modbus.pcap','pms_modbus_pcap':'pms-modbus.pcap','propulsion_modbus_pcap':'propulsion-modbus.pcap',
 'cargo_state_timeline':'cargo-state.jsonl','pms_state_timeline':'pms-state.jsonl','propulsion_state_timeline':'propulsion-state.jsonl','vessel_state_timeline':'vessel-state.jsonl','alarm_timeline':'alarm-timeline.jsonl',
 'cargo_state_csv':'cargo-state.csv','process_residual_json':'process-residual.json','modbus_conn_log':'conn.log','conduit_classification_json':'conduit-classification.json',
 'historian_freshness_before':'freshness-before.json','historian_freshness_after':'freshness-after.json'}
def cmd(*args):
 try:return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception:return None
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
ap=argparse.ArgumentParser(); ap.add_argument('experiment_id'); ap.add_argument('--root',default='evidence/runs'); a=ap.parse_args()
manifest=json.loads((ROOT/'experiments/manifest.json').read_text())['experiments']; exp=next((x for x in manifest if x['id']==a.experiment_id),None)
if not exp: raise SystemExit('Unknown experiment')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%SZ'); d=Path(a.root)/f"{stamp}-{a.experiment_id.lower()}"; d.mkdir(parents=True)
status=cmd('git','status','--porcelain')
run={'schema_version':2,'experiment_id':a.experiment_id,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'evidence_files':{k:DEFAULT_FILES.get(k,k) for k in exp['required_evidence']},'notes':'',
     'git':{'commit':cmd('git','rev-parse','HEAD'),'origin':cmd('git','remote','get-url','origin'),'tree_dirty':bool(status) if status is not None else None},
     'release_manifest_sha256':sha(ROOT/'release-manifest.json')}
(d/'run.json').write_text(json.dumps(run,indent=2)+'\n'); print(d)
