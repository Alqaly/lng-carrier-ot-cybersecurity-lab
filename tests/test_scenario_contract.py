import ast
from pathlib import Path


def test_scenario_cli_exposes_documented_exercises():
    tree=ast.parse(Path('scenario/run.py').read_text())
    names=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id=='SCENARIOS' and isinstance(node.value,ast.Dict):
                    for key in node.value.keys:
                        if isinstance(key,ast.Constant): names.add(key.value)
    assert {'cargo','pms','propulsion','vessel','cargo-fault','pms-trip','propulsion-lube'} <= names


def test_labctl_help_matches_scenario_contract():
    text=Path('labctl').read_text()
    for name in ['cargo-fault','pms-trip','propulsion-lube','vessel']:
        assert name in text
