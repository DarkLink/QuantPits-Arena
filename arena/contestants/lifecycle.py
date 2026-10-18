"""Immutable local inputs and staged admission of research participants."""

import copy
import hashlib
import json
import pickle
import pickletools
import re
import shutil
from pathlib import Path

import pandas as pd
import yaml

from arena.config import REPO_ROOT, RUNS_DIR
from arena.state import atomic_pickle, atomic_write, operation_lock


def fingerprint(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode())


def generation_root(name, root=None):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}', str(name)):
        raise ValueError('Invalid generation identifier')
    return Path(root or REPO_ROOT) / 'artifacts/evaluations' / name


def candidate_registry(root):
    from arena.contestants.registry import ContestantRegistry
    private = Path(root) / 'staging/manifests/private'
    public = Path(root) / 'staging/manifests/public'
    return ContestantRegistry(private_dir=private, public_dir=public) if private.exists() else ContestantRegistry()


def candidate_cache(root, market):
    from arena.inference.cache import prediction_cache_path
    return Path(root) / 'staging/artifacts/predictions' / prediction_cache_path(market).name


def check_assets(manifest, root=None):
    base = Path(root or REPO_ROOT)
    for relative, expected in manifest.adapter_config.get('asset_hashes', {}).items():
        path = base / relative
        if path.is_absolute() and not path.resolve().is_relative_to(base.resolve()):
            raise ValueError('Inference input is outside the repository')
        if not path.is_file() or fingerprint(path) != expected:
            raise ValueError('Frozen inference input changed')


def import_assets(workspace, contestant_id, cutoff):
    """Import model-only records and dataset definitions; never invoke training."""
    if not re.fullmatch(r'CONTESTANT_[A-Z]+', contestant_id):
        raise ValueError('An anonymous participant identifier is required')
    pd.Timestamp(cutoff)
    workspace = Path(workspace).resolve()
    records = []
    datasets = []
    for path in sorted(workspace.rglob('*.json')):
        if path.stat().st_size > 2_000_000:
            continue
        try:
            document = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        if not isinstance(document, dict):
            continue
        found = document.get('model_records')
        if (document.get('anchor_date') == cutoff and isinstance(found, dict) and found
                and all(isinstance(v, dict) and v.get('operation') == 'train'
                        and v.get('status') in ('ready', 'success') for v in found.values())):
            records.append((path, found))
        config = document.get('post_fit_prediction_dataset_configs')
        if isinstance(config, dict) and config:
            datasets.append((path, config))
    if len(records) != 1 or len(datasets) != 1:
        raise ValueError('A unique training record and effective dataset definition are required')
    record_path, selected = records[0]
    config_path, configs = datasets[0]
    from scripts.audit_privacy import RE_PROD_STATE_KEYS
    planned = []
    for number, (key, record) in enumerate(selected.items(), 1):
        candidates = [v for k, v in configs.items() if k in key or k in record.get('model_name', '')]
        if len(candidates) != 1:
            raise ValueError('Effective member configuration is ambiguous')
        dataset = copy.deepcopy(candidates[0])
        if RE_PROD_STATE_KEYS.search(json.dumps(dataset)):
            raise ValueError('Dataset definition failed the content preflight')
        artifact = (workspace / record['artifact_path']).resolve()
        weight = artifact / 'model.pkl'
        if not weight.is_relative_to(workspace) or not weight.is_file():
            raise ValueError('Training weight is missing or outside the selected workspace')
        with weight.open('rb') as stream:
            for opcode, value, _ in pickletools.genops(stream):
                if isinstance(value, str) and RE_PROD_STATE_KEYS.search(value):
                    raise ValueError('Training artifact failed the content preflight')
        handler = dataset['kwargs']['handler']['kwargs']
        if str(handler.get('end_time', '')) > cutoff or str(handler.get('fit_end_time', '')) > cutoff:
            raise ValueError('Training configuration exceeds the authorized information cutoff')
        planned.append((number, weight, dataset, record))
    destination = REPO_ROOT / 'artifacts/models' / contestant_id.lower() / cutoff.replace('-', '')
    config_destination = REPO_ROOT / 'artifacts/configs' / contestant_id.lower() / cutoff.replace('-', '')
    members, hashes, provenance = [], {}, []
    for number, source, dataset, record in planned:
        weight = destination / f'member_{number}.pkl'
        config = config_destination / f'member_{number}.yaml'
        if weight.exists() and fingerprint(weight) != fingerprint(source):
            raise ValueError('An immutable destination already contains a different asset')
        weight.parent.mkdir(parents=True, exist_ok=True)
        if not weight.exists():
            shutil.copy2(source, weight)
        content = yaml.safe_dump({'task': {'dataset': dataset}}, sort_keys=False).encode()
        if config.exists() and config.read_bytes() != content:
            raise ValueError('An immutable dataset configuration changed')
        atomic_write(config, content)
        relative_weight = str(weight.relative_to(REPO_ROOT))
        relative_config = str(config.relative_to(REPO_ROOT))
        hashes[relative_weight] = fingerprint(weight)
        hashes[relative_config] = fingerprint(config)
        members.append(dict(name=f'member_{number}', artifact_path=relative_weight, workflow_yaml=relative_config))
        provenance.append(dict(member=f'member_{number}', source=str(source),
                               source_record=record, sha256=fingerprint(source)))
    private = REPO_ROOT / 'manifests/private'
    manifest = dict(contestant_id=contestant_id, display_name=contestant_id, family='Anonymous',
        artifact_date=cutoff, train_cutoff=cutoff, historical_role='Research participant',
        training_mode='registered', feature_set='Private', inference_adapter='registered',
        observation_start=cutoff, arena_eligible_from=cutoff, statistics_eligible=False,
        members=members, adapter_config=dict(information_cutoff=cutoff, asset_hashes=hashes,
            dataset_mode='frozen_processors', version_id=cutoff.replace('-', '')))
    path = private / f'{contestant_id.lower()}.yaml'
    if path.exists() and yaml.safe_load(path.read_text()) != manifest:
        raise ValueError('Private participant definition already exists with different inputs')
    atomic_write(path, yaml.safe_dump(manifest, sort_keys=False).encode())
    write_json(private / f'{contestant_id.lower()}_provenance.json', dict(
        source_workspace=str(workspace), source_records_sha256=fingerprint(record_path),
        source_configs_sha256=fingerprint(config_path), members=provenance,
        information_cutoff=cutoff, model_training_performed=False))
    print(f'[import] {contestant_id}: {len(members)} frozen assets verified; no model training', flush=True)
    return path


def clone_participant(state, source_id, target_id, asof):
    """Return an independent state preserving every economic field and queue."""
    if any(cid == target_id for cid, _ in state['engines']):
        raise ValueError('Participant is already present in the checkpoint')
    parents = {key: cp for key, cp in state['engines'].items() if key[0] == source_id}
    if not parents or any(cp.daily_valuations[-1].date != asof for cp in state['engines'].values()):
        raise ValueError('Every source engine must end at the exact admission date')
    if source_id not in state.get('signal_history', {}):
        raise ValueError('Source signal history is missing')
    result = copy.deepcopy(state)
    baselines = {}
    for (_, aid), checkpoint in parents.items():
        child = copy.deepcopy(checkpoint)
        child.contestant_id = target_id
        result['engines'][(target_id, aid)] = child
        baselines[aid] = {name: getattr(checkpoint, name) for name in (
            'buy_attempt_count', 'unaffordable_buy_count', 'unaffordable_event_days',
            'rebalance_days_with_buy')}
        baselines[aid].update(rejected_order_count=len(checkpoint.rejected_orders),
                              stale_mark_count=len(checkpoint.stale_marks))
    result['signal_history'][target_id] = copy.deepcopy(state['signal_history'][source_id])
    return result, baselines


def prepare_entry(spec_path, prepare=False):
    from arena.contestants.registry import ContestantRegistry
    from arena.contestants.manifest import load_manifest
    from arena.inference.cache import prediction_cache_path
    from arena.seasons import SeasonManager
    from arena.calendar import TradingCalendar
    spec = yaml.safe_load(Path(spec_path).read_text())
    root = generation_root(spec['generation'])
    source_registry = ContestantRegistry()
    source = source_registry.get_contestant(spec['source_participant'])
    target_file = REPO_ROOT / spec['private_manifest']
    target = load_manifest(target_file)
    if (root/'complete.json').exists() and (root/'entry.json').exists():
        receipt=json.loads((root/'entry.json').read_text())
        if (receipt['spec_sha256']!=fingerprint(spec_path)
            or receipt['private_manifest_sha256']!=fingerprint(target_file)):
            raise ValueError('Completed generation has different immutable inputs')
        installed=source_registry.get_contestant(target.contestant_id)
        if fingerprint(installed.source_file)!=receipt['private_manifest_sha256']:
            raise ValueError('Installed participant differs from its completed generation')
        check_assets(installed)
        print('[prepare] matching participant admission is already complete',flush=True)
        return root
    if target.contestant_id in [c.contestant_id for c in source_registry.list_contestants()]:
        raise ValueError('Target participant is already registered')
    if target.observation_start != spec['state_asof'] or target.arena_eligible_from != spec['first_signal_date']:
        raise ValueError('Admission and participant time boundaries disagree')
    check_assets(target)
    calendar = TradingCalendar()
    frozen = {}
    states = {}
    for sid in SeasonManager.SEASON_ORDER:
        cfg = SeasonManager.get_season_config(sid)
        checkpoint = RUNS_DIR / f'{sid}_run/checkpoints/latest_state.pkl'
        cache = prediction_cache_path(cfg.universe_code)
        with checkpoint.open('rb') as stream:
            state = pickle.load(stream)
        clone, baselines = clone_participant(state, source.contestant_id, target.contestant_id, spec['state_asof'])
        cycles = calendar.build_weekly_cycles(cfg.anchor_date, spec['end_date'])
        next_cycle = cycles[state['last_completed_cycle_idx'] + 1]
        if next_cycle.decision_date != spec['first_signal_date'] or next_cycle.trade_date != spec['first_trade_date']:
            raise ValueError('Admission does not match the authorized next decision and trade dates')
        if len(baselines) != 28:
            raise ValueError('Admission requires all 28 source policies')
        frozen[str(checkpoint.relative_to(REPO_ROOT))] = fingerprint(checkpoint)
        frozen[str(cache.relative_to(REPO_ROOT))] = fingerprint(cache)
        states[sid] = (clone, baselines, cfg.universe_code)
    receipt = dict(spec=spec, spec_sha256=fingerprint(spec_path), source_files=frozen,
                   target_id=target.contestant_id, source_id=source.contestant_id,
                   private_manifest_sha256=fingerprint(target_file), phase='prepared')
    if spec.get('reuse_prediction_generation'):
        previous_root=generation_root(spec['reuse_prediction_generation'])
        receipt['reused_prediction_files']={str(candidate_cache(previous_root,market).relative_to(REPO_ROOT)):
            fingerprint(candidate_cache(previous_root,market)) for _,_,market in states.values()}
    marker = root / 'entry.json'
    if marker.exists():
        saved = json.loads(marker.read_text())
        if {k:v for k,v in saved.items() if k != 'phase'} != {k:v for k,v in receipt.items() if k != 'phase'}:
            raise ValueError('Prepared generation has different immutable inputs')
        return root
    if not prepare:
        print(f'[preflight] {target.contestant_id}: five pools, 28 policies, admission dates verified', flush=True)
        return root
    with operation_lock(REPO_ROOT / 'artifacts/evaluations/refresh.lock'):
        for relative, expected in frozen.items():
            if fingerprint(REPO_ROOT / relative) != expected:
                raise ValueError('Source inputs changed during admission preparation')
        private = root / 'staging/manifests/private'
        public = root / 'staging/manifests/public'
        private.mkdir(parents=True, exist_ok=True)
        shutil.copytree(REPO_ROOT / 'manifests/public', public, dirs_exist_ok=True)
        mapping = yaml.safe_load(source_registry.alias_map_file.read_text())
        for item in mapping['mappings']:
            shutil.copy2(source_registry.private_dir / item['private_file'], private / item['private_file'])
        shutil.copy2(target_file, private / target_file.name)
        mapping['mappings'].append(dict(private_id=target.contestant_id, anonymous_id=target.contestant_id,
                                         private_file=target_file.name, public_file=target_file.name))
        atomic_write(private / 'alias_map.yaml', yaml.safe_dump(mapping, sort_keys=False).encode())
        public_manifest = dict(contestant_id=target.contestant_id, display_name=target.contestant_id,
            family='Anonymous', observation_start=target.observation_start,
            arena_eligible_from=target.arena_eligible_from, statistics_eligible=False,
            historical_role='Observation participant', integrity_class='OBSERVATION',
            notes='Performance is reported only from the stated observation anchor.')
        atomic_write(public / target_file.name, yaml.safe_dump(public_manifest, sort_keys=False).encode())
        for sid, (state, baselines, market) in states.items():
            source_run = RUNS_DIR / f'{sid}_run'
            staged = root / 'staging/runs' / source_run.name
            shutil.copytree(source_run, staged)
            atomic_pickle(staged / 'checkpoints/latest_state.pkl', state)
            entries = staged / 'private/participant_entries.json'
            previous = json.loads(entries.read_text()) if entries.exists() else {}
            previous[target.contestant_id] = dict(anchor=target.observation_start, baselines=baselines)
            write_json(entries, previous)
            with prediction_cache_path(market).open('rb') as stream:
                cache = pickle.load(stream)
            reuse_name = spec.get('reuse_prediction_generation')
            if reuse_name:
                previous_root = generation_root(reuse_name)
                old_receipt = json.loads((previous_root/'entry.json').read_text())
                if old_receipt['source_files'] != frozen:
                    raise ValueError('Reusable predictions have different source snapshots')
                with candidate_cache(previous_root, market).open('rb') as stream:
                    reusable = pickle.load(stream)
                for participant in source_registry.list_contestants():
                    cid = participant.contestant_id
                    alias = source_registry.get_anonymous_id(cid)
                    prior = reusable.get(cid, reusable.get(alias, {}))
                    original = cache.get(cid, cache.get(alias, {}))
                    if any(d not in prior or not v.equals(prior[d]) for d,v in original.items()):
                        raise ValueError('Reusable predictions changed the authoritative prefix')
                    for key in {cid,alias}:
                        cache[key] = copy.deepcopy(prior)
            parent = cache.get(source.contestant_id, cache.get(spec['source_participant']))
            cache[target.contestant_id] = {d:copy.deepcopy(v) for d,v in parent.items() if d < spec['first_signal_date']}
            atomic_pickle(candidate_cache(root, market), cache)
        write_json(marker, receipt)
    print(f'[prepare] {target.contestant_id}: five independent staged checkpoints ready', flush=True)
    return root


def verify_entry_source(root):
    path = Path(root) / 'entry.json'
    if not path.exists():
        return
    receipt = json.loads(path.read_text())
    manifest=REPO_ROOT/receipt['spec']['private_manifest']
    candidate=Path(root)/'staging/manifests/private'/manifest.name
    if any(fingerprint(p)!=receipt['private_manifest_sha256'] for p in (manifest,candidate)):
        raise ValueError('Prepared participant definition changed')
    sources={**receipt['source_files'],**receipt.get('reused_prediction_files',{})}
    for relative, expected in sources.items():
        if fingerprint(REPO_ROOT / relative) != expected:
            raise ValueError('Live inputs changed since participant admission was prepared')


def verify_admission_predictions(root, markets):
    """Require a bound standalone first-decision check before admission execution."""
    receipt=json.loads((Path(root)/'entry.json').read_text())
    date=receipt['spec']['first_signal_date']
    registry=candidate_registry(root)
    target=registry.get_contestant(receipt['target_id'])
    check_assets(target)
    for market in markets:
        path=Path(root)/'verification'/f'{market}_{date}.json'
        if not path.exists():
            raise ValueError('Admission requires standalone first-decision verification for every pool')
        report=json.loads(path.read_text())
        checks=[c for c in report.get('checks',[]) if c['participant']==registry.get_anonymous_id(target.contestant_id)]
        if (not report.get('complete') or report.get('cache_sha256')!=fingerprint(candidate_cache(root,market))
            or len(checks)!=1 or checks[0].get('date')!=date
            or checks[0].get('manifest_sha256')!=fingerprint(target.source_file)
            or checks[0].get('max_score_difference',float('inf'))>1e-12):
            raise ValueError('Admission prediction verification is stale or incomplete')


def select_version(manifest, date):
    """Select an immutable private definition without changing historical routes."""
    from arena.contestants.manifest import load_manifest
    activations = manifest.adapter_config.get('versions', [])
    eligible = [a for a in activations if a['effective_decision'] <= date]
    if not eligible:
        return manifest
    selected = max(eligible, key=lambda a:a['effective_decision'])
    version = load_manifest(REPO_ROOT / selected['manifest'])
    if version.contestant_id != manifest.contestant_id:
        raise ValueError('Version belongs to a different participant')
    check_assets(version)
    return version
