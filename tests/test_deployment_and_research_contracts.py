from pathlib import Path
import json,yaml,re
R=Path(__file__).resolve().parents[1]

def compose(): return yaml.safe_load((R/'docker-compose.yml').read_text())

def test_explicit_dependency_pins_and_no_latest():
    c=compose()
    images=[svc.get('image','') for svc in c['services'].values() if svc.get('image')]
    assert images
    assert all(':latest' not in x for x in images)
    text=(R/'DEPENDENCIES.md').read_text()
    for name,version in [('OpenModelica','1.27.0'),('OpenPLC Runtime','4.1.9'),('FUXA','1.3.4'),('InfluxDB OSS','2.9.1'),('Telegraf','1.39.3'),('Grafana','13.2'),('Zeek','8.0.10'),('Containerlab','0.77.0')]:
        assert name in text and version in text

def test_reference_runtime_is_daemonized_and_loopback_only():
    c=compose()
    for name,svc in c['services'].items():
        if name=='modelica-builder' or 'profiles' in svc: continue
        assert svc.get('restart') in ('unless-stopped','always'), name
    for svc in c['services'].values():
        for p in svc.get('ports',[]) or []:
            if isinstance(p,str): assert p.startswith('127.0.0.1:'), p
    unit=(R/'deploy/systemd/lng-ot-lab.service').read_text()
    assert 'docker compose' in unit and 'compose.production.yml' in unit
    assert 'WantedBy=multi-user.target' in unit

def test_fixed_control_conduits_match_policy():
    c=compose(); policy=json.loads((R/'security/conduits.json').read_text())
    nets={s:cfg.get('networks',{}) for s,cfg in c['services'].items()}
    # expected fixed pairs in current reference topology
    expected={
      ('openplc-cargo','cargo-io',5020),
      ('openplc-pms','pms-io',5021),
      ('openplc-propulsion','propulsion-io',5022),
    }
    # Security ground truth stores endpoint IPs; verify those match the fixed Compose addresses.
    service_ip={}
    for service,network_map in nets.items():
        if not isinstance(network_map,dict):
            continue
        for net,cfg in network_map.items():
            if isinstance(cfg,dict) and cfg.get('ipv4_address'):
                service_ip[(service,net)]=cfg['ipv4_address']
    pair_meta={
      ('openplc-cargo','cargo-io',5020,'cargo_control'),
      ('openplc-pms','pms-io',5021,'pms_control'),
      ('openplc-propulsion','propulsion-io',5022,'propulsion_control'),
    }
    declared={(x['src'],x['dst'],x['port']) for x in policy['modbus']}
    for src,dst,port,net in pair_meta:
        assert (service_ip[(src,net)],service_ip[(dst,net)],port) in declared
        assert set(nets[src]) & set(nets[dst])
    fidelity=json.loads((R/'network/fidelity-contract.json').read_text())
    assert fidelity['status']=='design_accepted_runtime_unvalidated'
    assert fidelity['canonical_baseline']['runtime']=='Docker Compose v2 + systemd'
    assert fidelity['canonical_baseline']['compose_source']=='docker-compose.yml'
    assert fidelity['canonical_baseline']['conduit_ground_truth']=='security/conduits.json'
    assert fidelity['canonical_baseline']['must_remain_runnable_without_extension'] is True
    clab=fidelity['selected_extension']['topology_orchestrator']
    assert clab['name']=='Containerlab' and clab['reviewed_version']=='0.77.0'
    assert clab['integration_mode'].startswith('ext-container')
    assert fidelity['selected_extension']['routing']['dynamic_routing_suite']=='not selected'
    assert 'nftables' in fidelity['selected_extension']['policy_enforcement']['implementation']
    assert len(fidelity['runtime_acceptance_gates'])==7

def test_experiment_manifest_is_research_grade():
    m=json.loads((R/'experiments/manifest.json').read_text())['experiments']
    assert len(m)>=7
    ids=set()
    for e in m:
        assert e['id'] not in ids; ids.add(e['id'])
        assert e.get('hypothesis') and len(e['hypothesis'])>30
        assert e.get('metrics')
        assert e.get('required_evidence')

def test_visual_manifest_covers_first_ten_chapters():
    v=json.loads((R/'docs/09-research/visual-manifest.json').read_text())
    chapters=v['chapters']
    assert len(chapters)==10
    for ch,items in chapters.items():
        assert len(items)>=2, ch
        for item in items:
            for k in ['source','visual','license_or_reuse_status','what_to_notice','lab_mapping','limitation']:
                assert item.get(k), (ch,k)

def test_no_primary_public_doc_depends_on_custom_svg():
    public=[R/'README.md',R/'docs/index.md']+list((R/'docs').rglob('*.md'))
    offenders=[]
    for p in public:
        t=p.read_text(errors='ignore')
        if re.search(r'!\[[^\]]*\]\([^)]*assets/diagrams/[^)]*\.svg\)',t): offenders.append(str(p.relative_to(R)))
    assert not offenders, offenders

def test_faults_required_by_experiments_are_structurally_present():
    cargo=(R/'plant/modelica/CargoTransferPlant.mo').read_text()
    prop=(R/'plant/modelica/PropulsionPlant.mo').read_text()
    assert 'faultFlowPathBlocked' in cargo and 'blockedFlowFactor' in cargo
    assert 'faultCoolingFail' in prop and 'coolingFaultTempGain' in prop

def test_process_source_stale_is_not_mislabeled_opcua_stale():
    catalog=(R/'alarms/catalog.json').read_text()
    assert 'PROCESS_SOURCE_STALE' in catalog
    assert 'CARGO_DATA_STALE' not in catalog
    fresh=(R/'historian/freshness_check.py').read_text()
    assert 'Influx' in fresh or 'influx' in fresh.lower()

def test_deployment_scripts_are_present_and_executable():
    for rel in ['deploy/preflight.sh','deploy/check-secrets.sh','deploy/install-systemd.sh','deploy/backup.sh','deploy/restore.sh','labctl']:
        p=R/rel; assert p.exists(); assert p.stat().st_mode & 0o111
