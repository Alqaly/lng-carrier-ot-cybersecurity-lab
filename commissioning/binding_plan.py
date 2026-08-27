#!/usr/bin/env python3
"""Create a commissioning binding plan from *discovered* OPC UA evidence.

No identifiers are guessed. A desired teaching tag is resolved only when exactly
one live discovered variable matches one of the documented PLC symbol aliases.
"""
import argparse, json, re
from pathlib import Path

INTENT=Path('/project/commissioning/tag_intent.json')

def norm(s):
    if s is None: return ''
    s=str(s)
    # asyncua BrowseName often renders like "2:LevelSource_m"
    s=re.sub(r'^\d+:','',s)
    return re.sub(r'[^a-z0-9]','',s.lower())

def resolve(domain, discovery, intents):
    vars=[n for n in discovery['nodes'] if n.get('node_class')=='Variable']
    out={}; missing={}; ambiguous={}
    for tag, aliases in intents[domain].items():
        wanted={norm(a) for a in aliases}
        hits=[]
        for n in vars:
            candidates={norm(n.get('browse_name')),norm(n.get('display_name'))}
            # also consider the string portion of NodeId for servers that retain the PLC symbol there
            candidates.add(norm(n.get('nodeid')))
            if wanted & candidates or any(w and any(w in c for c in candidates) for w in wanted):
                hits.append(n)
        # de-duplicate on NodeId
        dedup={h['nodeid']:h for h in hits}
        hits=list(dedup.values())
        if len(hits)==1:
            h=hits[0]
            out[tag]={k:h.get(k) for k in ['nodeid','browse_name','display_name','data_type','status','source_timestamp','server_timestamp']}
        elif not hits:
            missing[tag]=aliases
        else:
            ambiguous[tag]=[{k:h.get(k) for k in ['nodeid','browse_name','display_name']} for h in hits]
    return out,missing,ambiguous

def telegraf_fragment(domain, endpoint, bindings):
    lines=[
        '[[inputs.opcua]]',
        f'  name = "{domain}_plc"',
        f'  endpoint = "{endpoint}"',
        '  timestamp = "source"',
        '',
        '  [[inputs.opcua.group]]',
        f'    name = "{domain}"',
        '    nodes = ['
    ]
    for tag,b in bindings.items():
        # Explicit nodeid mode keeps the discovered ns=...;s=... identity intact.
        nodeid=b['nodeid'].replace('"','\\"')
        lines.append(f'      {{name="{tag}", id="{nodeid}"}},')
    lines += ['    ]','']
    return '\n'.join(lines)

def markdown(domain, endpoint, bindings, missing, ambiguous):
    lines=[f'# {domain.title()} OPC UA Binding Plan','',f'Endpoint: `{endpoint}`','',
           '> Generated from live OPC UA discovery evidence. Resolve all missing/ambiguous tags before HMI/historian commissioning.','',
           '| Teaching tag | Discovered NodeId | Browse name | Data type |','|---|---|---|---|']
    for tag,b in bindings.items():
        lines.append(f"| `{tag}` | `{b['nodeid']}` | {b.get('browse_name') or ''} | {b.get('data_type') or ''} |")
    if missing:
        lines += ['','## Missing','']+[f"- `{k}`: expected one of {v}" for k,v in missing.items()]
    if ambiguous:
        lines += ['','## Ambiguous','']+[f"- `{k}` matched {len(v)} nodes; inspect discovery evidence manually." for k,v in ambiguous.items()]
    lines += ['','## Gate','',f"Resolved: **{len(bindings)}** · Missing: **{len(missing)}** · Ambiguous: **{len(ambiguous)}**",'']
    return '\n'.join(lines)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('domain',choices=['cargo','pms','propulsion'])
    ap.add_argument('--discovery',default=None)
    ap.add_argument('--outdir',default='/evidence/opcua')
    args=ap.parse_args()
    outdir=Path(args.outdir); outdir.mkdir(parents=True,exist_ok=True)
    disc=Path(args.discovery or outdir/f'{args.domain}-opcua-discovery.json')
    if not disc.exists(): raise SystemExit(f'Missing discovery evidence: {disc}. Run OPC UA discovery first.')
    discovery=json.loads(disc.read_text()); intents=json.loads(INTENT.read_text())
    bindings,missing,ambiguous=resolve(args.domain,discovery,intents)
    plan={'domain':args.domain,'endpoint':discovery['endpoint'],'bindings':bindings,'missing':missing,'ambiguous':ambiguous}
    (outdir/f'{args.domain}-binding-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (outdir/f'{args.domain}-binding-plan.md').write_text(markdown(args.domain,discovery['endpoint'],bindings,missing,ambiguous))
    (outdir/f'{args.domain}-telegraf-fragment.conf').write_text(telegraf_fragment(args.domain,discovery['endpoint'],bindings))
    print(json.dumps({'resolved':len(bindings),'missing':list(missing),'ambiguous':list(ambiguous),'output':str(outdir)},indent=2))
    raise SystemExit(3 if missing or ambiguous else 0)
