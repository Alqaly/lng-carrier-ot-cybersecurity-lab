from pathlib import Path
import importlib.util,json,os,stat,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
def load(name,rel):
 spec=importlib.util.spec_from_file_location(name,R/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def pcap(path): path.write_bytes(b'\xd4\xc3\xb2\xa1'+b'\x00'*24)
def test_boolean_run_flags_cannot_satisfy_evidence(tmp_path):
 ev=load('evaluate_bool','experiments/evaluate.py'); d=tmp_path/'r'; d.mkdir(); (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-CARGO-NORMAL','evidence':{'cargo_modbus_pcap':True,'cargo_state_timeline':True,'alarm_timeline':True}}))
 out=ev.evaluate(d); assert out['pass'] is False and out['evidence_completeness']==0
def test_blocked_flow_requires_real_process_contradiction_and_hashes(tmp_path):
 ev=load('evaluate_block','experiments/evaluate.py'); vr=load('verify_block','experiments/verify_run.py'); d=tmp_path/'r'; d.mkdir();
 (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-CARGO-BLOCKED-FLOW'})); pcap(d/'cargo-modbus.pcap')
 (d/'cargo-state.jsonl').write_text(json.dumps({'state':{'pumpFeedback':True,'valveFeedback':True,'flowMeasured':0.01}})+'\n')
 (d/'alarm-timeline.jsonl').write_text(json.dumps({'alarm_id':'CARGO_NO_FLOW','transition':'ACTIVE_UNACK'})+'\n')
 out=ev.evaluate(d); assert out['pass'] and len(out['artifacts'])==3 and all(x['sha256'] for x in out['artifacts'].values()); assert (d/'evidence-index.json').exists(); assert vr.verify(d)['pass']
 (d/'cargo-state.jsonl').write_text('{}\n'); assert vr.verify(d)['pass'] is False
def test_unexpected_modbus_classification_is_semantic_and_metric_accounted(tmp_path):
 ev=load('evaluate_sem','experiments/evaluate.py')
 d=tmp_path/'m'; d.mkdir(); (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-UNEXPECTED-MODBUS-SOURCE'})); (d/'conn.log').write_text('#fields\tuid\nX\n'); (d/'conduit-classification.json').write_text(json.dumps([{'classification':'EXPECTED'}])); assert not ev.evaluate(d)['pass']; (d/'conduit-classification.json').write_text(json.dumps([{'classification':'UNEXPECTED'}])); out=ev.evaluate(d); assert out['pass']; assert out['metrics']['classification_accuracy']['status']=='measured'
def test_new_run_captures_repository_provenance(tmp_path,monkeypatch):
 text=(R/'experiments/new_run.py').read_text(); assert "rev-parse','HEAD" in text and 'release_manifest_sha256' in text and 'tree_dirty' in text
def test_secrets_fail_closed_and_are_not_in_grafana_source():
 compose=(R/'docker-compose.yml').read_text(); assert 'INFLUX_TOKEN:?set INFLUX_TOKEN' in compose and 'GRAFANA_ADMIN_PASSWORD:?set GRAFANA_ADMIN_PASSWORD' in compose; assert ':-replace-this-' not in compose
 g=(R/'grafana/provisioning/datasources/influx.yml').read_text(); assert 'replace-this-token' not in g and '$INFLUX_TOKEN' in g
 unit=(R/'deploy/systemd/lng-ot-lab.service').read_text(); assert 'EnvironmentFile=-' not in unit
 check=(R/'deploy/check-secrets.sh').read_text(); assert '0600 or 0400' in check and 'replace-this-' in check; assert 'secrets-check' in (R/'labctl').read_text()
def test_restore_is_checksum_gated_and_destructive_overwrite_is_explicit():
 b=(R/'deploy/backup.sh').read_text(); rs=(R/'deploy/restore.sh').read_text(); assert 'sha256sum *.tgz' in b and 'docker compose stop' in b; assert 'sha256sum -c SHA256SUMS' in rs and '--verify' in rs and '--force' in rs and 'non-empty' in rs
def test_readiness_covers_every_compose_service_and_resource_profiler_never_sets_limits():
 import yaml
 c=yaml.safe_load((R/'docker-compose.yml').read_text()); rc=json.loads((R/'config/readiness-contract.json').read_text()); assert set(rc['service_coverage'])==set(c['services']); assert [x['id'] for x in rc['levels']]==['process_alive','reachable','commissioned','semantic_ready']
 rp=(R/'tools/resource_profile.py').read_text(); assert "docker','stats','--no-stream" in rp and 'no automatic resource limits' in rp; assert 'mem_limit' not in rp
def test_github_ci_is_read_only_sha_pinned_and_direct_dependencies_exact():
 wf=(R/'.github/workflows/quality.yml').read_text(); assert 'contents: read' in wf and 'ubuntu-24.04' in wf and 'persist-credentials: false' in wf; assert 'actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803' in wf; assert 'actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1' in wf
 assert (R/'requirements-ci.txt').read_text().splitlines()==['PyYAML==6.0.3','pytest==9.1.1','-r portal/requirements.txt']; assert (R/'requirements-docs.txt').read_text().strip()=='mkdocs-material==9.7.7'; assert (R/'.github/dependabot.yml').exists() and (R/'.github/CODEOWNERS').read_text().strip()=='* @Alqaly'

def test_secret_validator_accepts_private_values_and_rejects_placeholder(tmp_path):
    good=tmp_path/'good.env'; good.write_text('INFLUX_TOKEN=real-token-123\nINFLUX_PASSWORD=real-password-123\nGRAFANA_ADMIN_PASSWORD=real-grafana-123\n'); good.chmod(0o600)
    cp=subprocess.run([str(R/'deploy/check-secrets.sh'),str(good)],capture_output=True,text=True); assert cp.returncode==0,cp.stderr
    bad=tmp_path/'bad.env'; bad.write_text('INFLUX_TOKEN=replace-this-token\nINFLUX_PASSWORD=x\nGRAFANA_ADMIN_PASSWORD=y\n'); bad.chmod(0o600)
    cp=subprocess.run([str(R/'deploy/check-secrets.sh'),str(bad)],capture_output=True,text=True); assert cp.returncode!=0 and 'placeholder' in cp.stderr

def test_sensor_bias_requires_residual_anomaly(tmp_path):
    ev=load('evaluate_bias','experiments/evaluate.py'); d=tmp_path/'r'; d.mkdir(); (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-CARGO-SENSOR-BIAS'}));
    (d/'cargo-state.csv').write_text('time_s,levelSource,flowMeasured\n0,10,1\n1,9.9992,1\n'); pcap(d/'cargo-modbus.pcap')
    (d/'process-residual.json').write_text(json.dumps({'results':[{'anomaly':False,'residual_pct':1.0}]})); assert not ev.evaluate(d)['pass']
    (d/'process-residual.json').write_text(json.dumps({'results':[{'anomaly':True,'residual_pct':35.0}]})); assert ev.evaluate(d)['pass']

def test_resource_profiler_writes_repository_linked_metadata(tmp_path,monkeypatch):
    rp=load('resource_profile_test','tools/resource_profile.py')
    monkeypatch.setattr(rp,'run',lambda *args: json.dumps({'Name':'cargo-plant','CPUPerc':'1.2%','MemUsage':'10MiB / 1GiB'}))
    monkeypatch.setattr(rp,'git',lambda arg:'abc123')
    monkeypatch.setattr(rp,'manifest_sha',lambda :'deadbeef')
    out=rp.collect(1,0,tmp_path); assert out['git_commit']=='abc123' and out['release_manifest_sha256']=='deadbeef' and out['rows']==1
    assert (tmp_path/'docker-stats.jsonl').exists()

def test_publication_control_names_canonical_repo_and_ci_builds_docs_strictly():
    pub=(R/'docs/09-research/github-publication-control.md').read_text(); wf=(R/'.github/workflows/quality.yml').read_text()
    assert 'https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab' in pub
    assert 'mkdocs build --strict' in wf and 'release_gate.py' in wf


def test_normal_cargo_requires_causal_response_and_accounts_for_metrics(tmp_path):
    ev=load('evaluate_normal_v3','experiments/evaluate.py'); d=tmp_path/'normal'; d.mkdir()
    (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-CARGO-NORMAL'})); pcap(d/'cargo-modbus.pcap')
    rows=[
        {'event_epoch':100.0,'source_time_s':0.0,'state':{'pumpCmd':False,'valveCommand':0.0,'pumpFeedback':False,'valveFeedback':False,'flowMeasured':0.0}},
        {'event_epoch':101.0,'source_time_s':1.0,'state':{'pumpCmd':True,'valveCommand':1.0,'pumpFeedback':False,'valveFeedback':False,'flowMeasured':0.0}},
        {'event_epoch':102.0,'source_time_s':2.0,'state':{'pumpCmd':True,'valveCommand':1.0,'pumpFeedback':True,'valveFeedback':True,'flowMeasured':0.4}},
    ]
    (d/'cargo-state.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n'); (d/'alarm-timeline.jsonl').write_text('')
    out=ev.evaluate(d); assert out['pass']; assert out['schema_version']==3
    assert out['metrics']['process_response_time_s']['status']=='measured' and out['metrics']['process_response_time_s']['value']==1.0
    assert out['metrics']['event_order_accuracy']['status']=='unavailable'


def test_pms_generator_trip_requires_full_causal_sequence_and_cross_system_consequence(tmp_path):
    ev=load('evaluate_pms_v3','experiments/evaluate.py'); d=tmp_path/'pms'; d.mkdir(); (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-PMS-GEN-TRIP'})); pcap(d/'pms-modbus.pcap')
    pms=[
      {'event_epoch':100.0,'source_time_s':0.0,'state':{'faultGen1Trip':False,'gen1BreakerFB':True,'frequencyHz':60.0,'underFrequency':False,'blackout':False,'shedCargo':False,'shedHotel':False}},
      {'event_epoch':101.0,'source_time_s':1.0,'state':{'faultGen1Trip':True,'gen1BreakerFB':True,'frequencyHz':59.8,'underFrequency':False,'blackout':False,'shedCargo':False,'shedHotel':False}},
      {'event_epoch':102.0,'source_time_s':2.0,'state':{'faultGen1Trip':True,'gen1BreakerFB':False,'frequencyHz':59.0,'underFrequency':False,'blackout':False,'shedCargo':False,'shedHotel':False}},
      {'event_epoch':103.0,'source_time_s':3.0,'state':{'faultGen1Trip':True,'gen1BreakerFB':False,'frequencyHz':57.4,'underFrequency':True,'blackout':False,'shedCargo':False,'shedHotel':False}},
      {'event_epoch':104.0,'source_time_s':4.0,'state':{'faultGen1Trip':True,'gen1BreakerFB':False,'frequencyHz':56.9,'underFrequency':True,'blackout':False,'shedCargo':True,'shedHotel':False}},
    ]
    vessel=[{'event_epoch':100.5,'state':{'links':{'cargoPowerAvailable':True,'propulsionAuxPowerAvailable':True}}},{'event_epoch':105.0,'state':{'links':{'cargoPowerAvailable':False,'propulsionAuxPowerAvailable':True}}}]
    (d/'pms-state.jsonl').write_text('\n'.join(json.dumps(x) for x in pms)+'\n'); (d/'vessel-state.jsonl').write_text('\n'.join(json.dumps(x) for x in vessel)+'\n')
    (d/'alarm-timeline.jsonl').write_text(json.dumps({'event_epoch':103.5,'alarm_id':'PMS_UNDER_FREQUENCY','transition':'ACTIVE_UNACK'})+'\n')
    out=ev.evaluate(d); assert out['pass']; assert all(x['pass'] for x in out['semantic_checks'])
    assert out['metrics']['frequency_nadir_hz']['value']==56.9; assert out['metrics']['load_shed_latency_s']['value']==3.0; assert out['metrics']['event_order_accuracy']['value']==1.0
    pms[1]['state']['faultGen1Trip']=False; pms[2]['state']['faultGen1Trip']=False; pms[3]['state']['faultGen1Trip']=False; pms[4]['state']['faultGen1Trip']=False
    (d/'pms-state.jsonl').write_text('\n'.join(json.dumps(x) for x in pms)+'\n'); assert not ev.evaluate(d)['pass']


def test_propulsion_cooling_fault_requires_protective_inhibit_and_alarm(tmp_path):
    ev=load('evaluate_prop_v3','experiments/evaluate.py'); d=tmp_path/'prop'; d.mkdir(); (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-PROP-COOLING-FAULT'})); pcap(d/'propulsion-modbus.pcap')
    rows=[
      {'event_epoch':200.0,'source_time_s':0.0,'state':{'engineRunning':True,'engineEnable':True,'faultCoolingFail':False,'highCoolantTemp':False,'coolantTempC':80.0}},
      {'event_epoch':201.0,'source_time_s':1.0,'state':{'engineRunning':True,'engineEnable':True,'faultCoolingFail':True,'highCoolantTemp':False,'coolantTempC':92.0}},
      {'event_epoch':202.0,'source_time_s':2.0,'state':{'engineRunning':True,'engineEnable':True,'faultCoolingFail':True,'highCoolantTemp':True,'coolantTempC':101.0}},
      {'event_epoch':203.0,'source_time_s':3.0,'state':{'engineRunning':False,'engineEnable':False,'faultCoolingFail':True,'highCoolantTemp':True,'coolantTempC':105.0}},
    ]
    (d/'propulsion-state.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n'); (d/'alarm-timeline.jsonl').write_text(json.dumps({'event_epoch':202.5,'alarm_id':'PROP_HIGH_COOLANT','transition':'ACTIVE_UNACK'})+'\n')
    out=ev.evaluate(d); assert out['pass']; assert out['metrics']['trip_latency_s']['value']==1.0; assert out['metrics']['peak_temperature_c']['value']==105.0
    rows[-1]['state']['engineEnable']=True; (d/'propulsion-state.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n'); assert not ev.evaluate(d)['pass']


def test_opcua_outage_requires_run_ground_truth_and_modbus_transaction_inside_window(tmp_path):
    ev=load('evaluate_opc_v3','experiments/evaluate.py'); d=tmp_path/'opc'; (d/'zeek').mkdir(parents=True); (d/'run.json').write_text(json.dumps({'experiment_id':'EXP-OPCUA-STALE-CARGO'})); pcap(d/'cargo-modbus.pcap')
    (d/'freshness-before.json').write_text(json.dumps({'fresh':True,'checked_epoch':100.0})); (d/'freshness-after.json').write_text(json.dumps({'fresh':False,'checked_epoch':103.0}))
    (d/'opcua-outage.json').write_text(json.dumps({'domain':'cargo','control_preserved':True,'started_at':'1970-01-01T00:01:41+00:00','restored_at':'1970-01-01T00:01:44+00:00'}))
    (d/'zeek/modbus.log').write_text('#fields\tts\tuid\n101.5\tC1\n')
    out=ev.evaluate(d); assert out['pass']; assert out['metrics']['historian_stale_detection_latency_s']['value']==2.0
    (d/'zeek/modbus.log').write_text('#fields\tts\tuid\n99.0\tC1\n'); assert not ev.evaluate(d)['pass']


def test_every_experiment_has_semantic_evaluator_and_metric_accounting_contract():
    manifest=json.loads((R/'experiments/manifest.json').read_text())['experiments']; text=(R/'experiments/evaluate.py').read_text()
    assert len(manifest)==7
    for exp in manifest:
        assert exp['metrics'] and exp['required_evidence']; assert exp['id'] in text
    assert 'semantic_checks' in text and 'status": "unavailable"' in text and 'status": "measured"' in text


def test_opcua_outage_supports_run_scoped_evidence_record():
    outage=load('opcua_outage_scoped','tools/opcua_outage.py'); p=outage.state_path('cargo','evidence/runs/test/opcua-outage.json')
    assert p == (R/'evidence/runs/test/opcua-outage.json').resolve()
    try: outage.state_path('cargo','../outside.json')
    except ValueError: pass
    else: raise AssertionError('outage evidence path escaped evidence/')
    text=(R/'labctl').read_text(); assert 'opcua-outage <domain> start|restore [--out evidence/run/opcua-outage.json]' in text


def test_capture_supports_deterministic_run_scoped_duration():
    labctl=(R/'labctl').read_text()
    assert 'dest="" duration=""' in labctl and '${domain}-${kind}.pcap' in labctl
    assert '--duration' in labctl and 'timeout -s INT ${duration} tcpdump' in labctl
    assert 'Capture output is missing or empty' in labctl
