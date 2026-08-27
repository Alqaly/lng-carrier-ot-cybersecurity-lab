#!/usr/bin/env python3
"""Collect Docker resource evidence. It deliberately does not invent CPU/RAM limits."""
from __future__ import annotations
import argparse,datetime,hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args): return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def git(arg):
 try:return run('git',*arg)
 except Exception:return None
def manifest_sha():
 p=ROOT/'release-manifest.json'; return hashlib.sha256(p.read_bytes()).hexdigest()
def collect(samples:int,interval:float,out:Path):
 if samples<1 or interval<0: raise ValueError('samples must be >=1 and interval >=0')
 out.mkdir(parents=True,exist_ok=True); path=out/'docker-stats.jsonl'
 count=0
 with path.open('w') as f:
  for i in range(samples):
   text=run('docker','stats','--no-stream','--format','{{json .}}')
   now=datetime.datetime.now(datetime.timezone.utc).isoformat()
   for line in text.splitlines():
    if not line.strip(): continue
    row=json.loads(line); row['_observed_at']=now; f.write(json.dumps(row,sort_keys=True)+'\n'); count+=1
   if i+1<samples: time.sleep(interval)
 meta={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'samples_requested':samples,'rows':count,'interval_s':interval,
       'git_commit':git(('rev-parse','HEAD')),'release_manifest_sha256':manifest_sha(),
       'policy':'measurement only; no automatic resource limits or sizing recommendation'}
 (out/'resource-profile.json').write_text(json.dumps(meta,indent=2)+'\n'); return meta
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--samples',type=int,default=12); ap.add_argument('--interval',type=float,default=5); ap.add_argument('--out',default=None); a=ap.parse_args()
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'); out=Path(a.out or f'evidence/resource-profiles/{stamp}'); print(json.dumps(collect(a.samples,a.interval,out),indent=2))
if __name__=='__main__': main()
