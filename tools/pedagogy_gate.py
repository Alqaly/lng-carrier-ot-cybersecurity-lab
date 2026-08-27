#!/usr/bin/env python3
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
course=sorted((R/'docs/course').glob('[0-9][0-9]-*.md'))
problems=[]
if len(course)!=10: problems.append(f'expected 10 course chapters, found {len(course)}')
for p in course:
    t=p.read_text(errors='ignore')
    lower=t.lower()
    for concept,patterns in {
      'why':['why this matters'],
      'visual':['visual tour','visual reference'],
      'memory':['memory hook'],
      'practice':['worked example','lab action','experiment'],
      'explain-back':['explain it in 60 seconds'],
      'source':['http://','https://'],
    }.items():
        if not any(x in lower for x in patterns): problems.append(f'{p.name}: missing {concept}')
    if len(re.findall(r'\b\w+\b',t)) < 280: problems.append(f'{p.name}: too shallow')
if problems:
    print('PEDAGOGY GATE\nFAIL'); [print(' -',x) for x in problems]; raise SystemExit(1)
print('PEDAGOGY GATE\nPASS')
print(' - 10/10 chapters have why + real visual source + memory hook + practice + explain-back')
print(' - each chapter meets minimum teaching depth')
