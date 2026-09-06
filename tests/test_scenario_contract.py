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
    assert {'cargo','pms','propulsion','vessel','cargo-fault','pms-trip','propulsion-lube','propulsion-cooling'} <= names


def test_labctl_help_matches_scenario_contract():
    text=Path('labctl').read_text()
    for name in ['cargo-fault','pms-trip','propulsion-lube','propulsion-cooling','vessel']:
        assert name in text

    scenario=Path('scenario/run.py').read_text()
    assert "c.write_coil(21,True,device_id=1)" in scenario
    assert scenario.count("c.write_coil(21,False,device_id=1)") >= 2
    assert "'highCoolantTemp': bool(di[2])" in scenario
    assert "pre_plc_commissioning_not_experiment_evidence" in scenario
