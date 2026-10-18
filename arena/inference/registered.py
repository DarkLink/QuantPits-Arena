"""Inference for registered immutable assets, without model fitting."""

import copy
import gc
import io
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from arena.config import REPO_ROOT, QLIB_DATA_URI
from arena.contestants.lifecycle import check_assets, fingerprint, select_version
from arena.state import atomic_pickle


def load_portable_model(path):
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    class LocalUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == 'torch.storage' and name == '_load_from_bytes':
                return lambda value: torch.load(io.BytesIO(value), map_location=device, weights_only=False)
            return super().find_class(module, name)

    with Path(path).open('rb') as stream:
        model = LocalUnpickler(stream).load()
    visited = set()

    def move(value, depth=0):
        if id(value) in visited or depth > 3:
            return
        visited.add(id(value))
        if isinstance(value, torch.Tensor):
            return
        if isinstance(value, torch.nn.Module):
            value.to(device)
            for child in value.modules():
                if hasattr(child, 'device'):
                    child.device = device
        if hasattr(value, 'device'):
            value.device = device
        if hasattr(value, '__dict__'):
            for child in vars(value).values():
                if isinstance(child, torch.nn.Module) or hasattr(child, 'device'):
                    move(child, depth + 1)

    move(model)
    return model


def frozen_dataset(member, market, start, end, cutoff):
    """Reconstruct fitted transforms on the original training universe once."""
    from qlib.utils import init_instance_by_config
    from qlib.data.dataset.handler import DataHandlerLP
    config = yaml.safe_load((REPO_ROOT / member.workflow_yaml).read_text())['task']['dataset']
    config = copy.deepcopy(config)
    original = copy.deepcopy(config['kwargs']['handler'])
    cache_key = fingerprint(REPO_ROOT / member.workflow_yaml)
    processor_file = (REPO_ROOT / member.artifact_path).with_suffix('.processors.pkl')
    if processor_file.exists():
        with processor_file.open('rb') as stream:
            saved = pickle.load(stream)
        if saved['config_sha256'] != cache_key:
            raise ValueError('Frozen processor configuration changed')
    else:
        original['kwargs']['end_time'] = cutoff
        fitted = init_instance_by_config(original)
        saved = dict(config_sha256=cache_key,
                     infer_processors=fitted.infer_processors,
                     shared_processors=fitted.shared_processors,
                     learn_processors=[p for p in fitted.learn_processors if p.__class__.__name__ != 'DropnaLabel'])
        atomic_pickle(processor_file, saved)
        del fitted
        gc.collect()
    handler = config['kwargs']['handler']
    handler['kwargs'].update(instruments=market, end_time=end,
                             infer_processors=copy.deepcopy(saved['infer_processors']),
                             shared_processors=copy.deepcopy(saved['shared_processors']),
                             learn_processors=copy.deepcopy(saved['learn_processors']),
                             init_data=False)
    inference_handler = init_instance_by_config(handler)
    inference_handler.setup_data(init_type=DataHandlerLP.IT_LS)
    config['kwargs']['handler'] = inference_handler
    context_start = min(start, str(config['kwargs']['segments']['test'][0]))
    config['kwargs']['segments']['test'] = [context_start, end]
    return init_instance_by_config(config)


def prediction_scores(prediction):
    if isinstance(prediction, pd.DataFrame):
        prediction = prediction['score'] if 'score' in prediction else prediction.iloc[:, 0]
    if not isinstance(prediction, pd.Series) or prediction.empty:
        raise ValueError('Registered member returned no predictions')
    return prediction


def predict_asof(model, dataset, start, end):
    """Only matured historical outcomes may populate dated inference state."""
    memory = getattr(dataset, '_memory', None)
    if memory is None or not memory.shape[-1]:
        return prediction_scores(model.predict(dataset))
    from arena.calendar import TradingCalendar
    calendar = TradingCalendar()
    horizon = int(dataset.horizon)
    if horizon <= 0:
        raise ValueError('Dated inference state requires an explicit positive observation horizon')
    labels = dataset._label.copy()
    label_dates = dataset.restore_index(np.arange(len(labels))).get_level_values('datetime')
    context_start = dataset.segments['test'][0]
    pieces = []
    for date in calendar.get_trading_days(start, end):
        position = calendar.day_to_idx[date]-horizon
        if position < 0:
            raise ValueError('Inference history does not cover the observation horizon')
        last_observed = calendar.all_days[position]
        dataset._label = labels.copy()
        dataset._label[label_dates > pd.Timestamp(last_observed)] = np.nan
        dataset.clear_memory()
        dataset.segments['test'] = [context_start, date]
        prediction = prediction_scores(model.predict(dataset))
        day = prediction.index.get_level_values('datetime') == pd.Timestamp(date)
        pieces.append(prediction.loc[day])
    return pd.concat(pieces).sort_index()


def infer_registered(manifest, market, start, end):
    """Keep member semantics in private configuration and freeze each date route."""
    import qlib
    from arena.inference.batch_infer import fuse_dict, to_date_dict
    qlib.init(provider_uri=str(QLIB_DATA_URI), region='cn')
    version = select_version(manifest, start)
    if select_version(manifest, end).adapter_config.get('version_id') != version.adapter_config.get('version_id'):
        raise ValueError('Inference range crosses an asset activation; split by version')
    check_assets(version)
    cutoff = version.adapter_config['information_cutoff']
    scores = {}
    for number, member in enumerate(version.members, 1):
        print(f'[inference] {manifest.contestant_id}: member_{number} on {market}', flush=True)
        model = load_portable_model(REPO_ROOT / member.artifact_path)
        dataset = frozen_dataset(member, market, start, end, cutoff)
        prediction = predict_asof(model, dataset, start, end)
        scores[f'member_{number}'] = prediction
        del model, dataset
        gc.collect()
    if len(scores) != len(version.members) or not scores:
        raise ValueError('Registered inference requires every frozen member')
    result = {d:v for d,v in to_date_dict(fuse_dict(scores)).items() if start <= d <= end}
    if any(not np.isfinite(v.to_numpy()).all() or not v.index.is_unique for v in result.values()):
        raise ValueError('Registered inference produced an invalid score slice')
    return result


def verify_asof(generation, market, date):
    from arena.contestants.lifecycle import generation_root, candidate_registry, candidate_cache, write_json
    root=generation_root(generation)
    registry=candidate_registry(root)
    with candidate_cache(root,market).open('rb') as stream:
        cache=pickle.load(stream)
    checks=[]
    for manifest in registry.list_contestants():
        if not manifest.observation_start or date<manifest.observation_start:
            continue
        expected=cache[manifest.contestant_id][date]
        actual=infer_registered(manifest,market,date,date)[date]
        if not expected.index.equals(actual.index):
            raise ValueError('Dated inference index differs from its extended window')
        maximum=float(np.max(np.abs(expected.to_numpy()-actual.to_numpy())))
        if maximum>1e-12:
            raise ValueError('Dated inference differs when later observations are removed')
        checks.append(dict(participant=registry.get_anonymous_id(manifest.contestant_id),date=date,
                           instruments=len(actual),max_score_difference=maximum,
                           manifest_sha256=fingerprint(manifest.source_file)))
    if not checks:
        raise ValueError('No observation participant covers the verification date')
    write_json(root/'verification'/f'{market}_{date}.json',dict(
        complete=True, checks=checks, cache_sha256=fingerprint(candidate_cache(root,market))))
    print(f'[verify] {market}: standalone decision agrees with the extended window',flush=True)
