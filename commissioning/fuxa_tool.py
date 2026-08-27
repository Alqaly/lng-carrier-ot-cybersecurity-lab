#!/usr/bin/env python3
"""Authenticated FUXA project export/import helper.

This tool intentionally does not manufacture OPC UA bindings. It round-trips the
actual project from a running FUXA instance after the engineer commissions devices.
"""
import argparse, json, os, sys
from pathlib import Path
import httpx

BASE=os.getenv('FUXA_URL','http://fuxa:1881').rstrip('/')

def headers(args):
    h={'Accept':'application/json','Content-Type':'application/json'}
    token=args.token or os.getenv('FUXA_TOKEN')
    api_key=args.api_key or os.getenv('FUXA_API_KEY')
    if token: h['x-access-token']=token
    if api_key: h['x-api-key']=api_key
    return h

def export_project(args):
    r=httpx.get(BASE+'/api/project',headers=headers(args),timeout=10)
    r.raise_for_status(); data=r.json()
    p=Path(args.file); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2)+'\n')
    print(f'Exported live FUXA project → {p}')

def import_project(args):
    p=Path(args.file)
    data=json.loads(p.read_text())
    required={'version','devices','hmi','server'}
    missing=required-set(data)
    if missing: raise SystemExit('Invalid FUXA project; missing: '+', '.join(sorted(missing)))
    if not args.yes:
        raise SystemExit('Import replaces the full FUXA project. Re-run with --yes after reviewing the file.')
    r=httpx.post(BASE+'/api/project',headers=headers(args),json=data,timeout=15)
    r.raise_for_status()
    print(f'Imported {p} into {BASE}')

def validate(args):
    data=json.loads(Path(args.file).read_text())
    required={'version','devices','hmi','server'}
    missing=required-set(data)
    if missing: raise SystemExit('Missing: '+', '.join(sorted(missing)))
    print(json.dumps({'valid_shell':True,'devices':len(data.get('devices',{})),'views':len(data.get('hmi',{}).get('views',[]))},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description='Round-trip the commissioned FUXA project')
    ap.add_argument('action',choices=['export','import','validate'])
    ap.add_argument('--file',default='/evidence/fuxa/fuxa-project.json')
    ap.add_argument('--token')
    ap.add_argument('--api-key')
    ap.add_argument('--yes',action='store_true')
    args=ap.parse_args()
    try:
        {'export':export_project,'import':import_project,'validate':validate}[args.action](args)
    except httpx.HTTPStatusError as e:
        print(f'FUXA API error: {e.response.status_code} {e.response.text}',file=sys.stderr); raise SystemExit(2)
    except Exception as e:
        print(f'FUXA tool failed: {e}',file=sys.stderr); raise SystemExit(2)
