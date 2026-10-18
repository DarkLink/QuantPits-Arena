"""Inference state only observes outcomes matured by the requested date."""
import numpy as np
import pandas as pd

from arena.inference.registered import predict_asof


class DatedDataset:
    def __init__(self):
        self.dates=['2026-09-30','2026-10-08','2026-10-09','2026-10-12','2026-10-13']
        self._memory=np.zeros((5,1))
        self._label=np.array([.1,.2,.3,.4,.5])
        self.horizon=1
        self.segments={'test':['2026-09-30','2026-10-13']}

    def restore_index(self,positions):
        return pd.MultiIndex.from_product([pd.to_datetime(self.dates),['STOCK_01']],names=['datetime','instrument'])[positions]

    def clear_memory(self):
        self._memory[:]=0


class DatedPredictor:
    def __init__(self):self.seen=[]

    def predict(self,dataset):
        end=dataset.segments['test'][1]
        assert not dataset._memory.any()
        self.seen.append((end,dataset._label.copy()))
        value=float(np.nansum(dataset._label))
        index=dataset.restore_index(np.arange(5))
        return pd.Series(value,index=index).loc[:end]


def test_dated_inference_uses_real_trading_sessions_and_preserves_prefix():
    model=DatedPredictor()
    full=predict_asof(model,DatedDataset(),'2026-10-09','2026-10-13')
    first=predict_asof(DatedPredictor(),DatedDataset(),'2026-10-09','2026-10-09')
    assert model.seen[0][1].tolist()[:2]==[.1,.2]
    assert np.isnan(model.seen[0][1][2:]).all()
    assert full.loc[pd.Timestamp('2026-10-09')].iloc[0]==first.iloc[0]
    assert full.loc[pd.Timestamp('2026-10-13')].iloc[0]==1.0
