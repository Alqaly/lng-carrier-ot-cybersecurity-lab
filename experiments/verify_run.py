#!/usr/bin/env python3
"""Verify evaluated evidence has not changed since evaluation.json was produced."""
import argparse,hashlib,json
from pathlib import Path

def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def verify(run):
 ev=json.loads((run/'evaluation.json').read_text()); index=json.loads((run/'evidence-index.json').read_text()); problems=[]
 for key,item in index.get('artifacts',{}).items():
  p=run/item['path']
  if not p.is_file(): problems.append(f'{key}: missing {item["path"]}'); continue
  actual=sha256(p)
  if actual!=item['sha256']: problems.append(f'{key}: SHA-256 mismatch {actual} != {item["sha256"]}')
 return {'experiment_id':ev.get('experiment_id'),'verified_artifacts':len(index.get('artifacts',{})),'problems':problems,'pass':not problems}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('run_dir'); a=ap.parse_args(); out=verify(Path(a.run_dir)); print(json.dumps(out,indent=2)); raise SystemExit(0 if out['pass'] else 2)
if __name__=='__main__': main()
