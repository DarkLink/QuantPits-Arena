"""Verified disk round trips for complete frozen decision intents."""
import hashlib
import pickle
from arena.state import atomic_pickle


def save_commitment(path, orders, cycle, policy_signature):
    payload=pickle.dumps(dict(orders=orders,cycle_idx=cycle.cycle_idx,
        decision_date=cycle.decision_date,trade_date=cycle.trade_date,
        policy_signature=policy_signature),protocol=pickle.HIGHEST_PROTOCOL)
    digest=hashlib.sha256(payload).hexdigest()
    atomic_pickle(path,dict(payload=payload,sha256=digest))
    return digest


def load_commitment(path, cycle, policy_signature):
    with open(path,'rb') as stream: envelope=pickle.load(stream)
    if hashlib.sha256(envelope['payload']).hexdigest()!=envelope['sha256']:
        raise ValueError('Frozen commitment hash mismatch')
    value=pickle.loads(envelope['payload'])
    if (value['cycle_idx'],value['decision_date'],value['trade_date'],value['policy_signature']) != (cycle.cycle_idx,cycle.decision_date,cycle.trade_date,policy_signature):
        raise ValueError('Frozen commitment context mismatch')
    return value['orders']
