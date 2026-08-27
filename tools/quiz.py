#!/usr/bin/env python3
"""Small retrieval-practice CLI for course explain-back.

Answers are intentionally hidden until the learner attempts retrieval.
"""
from __future__ import annotations
import argparse,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1]
DATA=json.loads((R/'learning/quizzes.json').read_text())

ap=argparse.ArgumentParser()
ap.add_argument('topic',choices=sorted(DATA))
ap.add_argument('--all',action='store_true',help='ask all questions instead of a short retrieval set')
ap.add_argument('--seed',type=int,default=None)
args=ap.parse_args()
qs=list(DATA[args.topic])
if args.seed is not None: random.seed(args.seed)
random.shuffle(qs)
if not args.all: qs=qs[:min(3,len(qs))]
print(f"RETRIEVAL PRACTICE — {args.topic.upper()}\n")
score=0
for i,item in enumerate(qs,1):
    print(f"Q{i}. {item['q']}")
    try: input("Think / explain aloud, then press Enter to reveal… ")
    except EOFError: pass
    print(f"A: {item['a']}\n")
print("Do not score by word matching. Score yourself by whether you explained the causal idea without looking at notes.")
