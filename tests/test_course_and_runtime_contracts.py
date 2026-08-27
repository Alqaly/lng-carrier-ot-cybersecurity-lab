from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[1]

def _walk_nav(node):
    if isinstance(node,str): yield node
    elif isinstance(node,list):
        for x in node: yield from _walk_nav(x)
    elif isinstance(node,dict):
        for x in node.values(): yield from _walk_nav(x)

def test_mkdocs_nav_paths_exist():
    m=yaml.safe_load((R/'mkdocs.yml').read_text())
    missing=[]
    for rel in _walk_nav(m['nav']):
        if rel.startswith(('http://','https://')): continue
        if not (R/rel).exists(): missing.append(rel)
    assert not missing, missing

def test_course_has_exactly_ten_numbered_chapters():
    chapters=sorted((R/'docs/course').glob('[0-9][0-9]-*.md'))
    assert len(chapters)==10
    assert [p.name[:2] for p in chapters]==[f'{i:02d}' for i in range(1,11)]

def test_runtime_smoke_is_read_only():
    t=(R/'tools/runtime_smoke.py').read_text().lower()
    assert 'urlopen' in t
    assert 'post(' not in t and 'requests.post' not in t
    assert 'runtime smoke' in t

def test_server_acceptance_covers_persistence_and_experiments():
    t=(R/'docs/04-build/server-acceptance-test.md').read_text().lower()
    for phrase in ['openplc','opc ua','fuxa','experiments/manifest.json','reboot','backup','restore']:
        assert phrase in t

def test_post_commissioning_service_probe_is_exposed():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    labctl = (root / "labctl").read_text()
    probe = (root / "tools" / "service_probe.py")
    assert probe.exists()
    assert "runtime-verify" in labctl
    text = probe.read_text()
    for port in (5020, 5021, 5022, 4840, 4841, 4842, 8443, 8444, 8445):
        assert str(port) in text

def test_retrieval_practice_command_matches_course_claim():
    from pathlib import Path
    import json
    root = Path(__file__).resolve().parents[1]
    labctl=(root/'labctl').read_text()
    assert 'quiz)' in labctl
    quizzes=json.loads((root/'learning/quizzes.json').read_text())
    for topic in ('ot','modbus','cargo','pms','propulsion','opcua'):
        assert topic in quizzes and quizzes[topic]
