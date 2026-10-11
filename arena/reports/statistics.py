"""Full-precision finite Monte Carlo diagnostics and declared-family corrections."""
import numpy as np
from scipy.stats import beta


def empirical(target, values):
    values=np.asarray(values,dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError('Finite, nonempty null distribution required')
    n=len(values); k=int(np.count_nonzero(values>=target))
    p=(k+1)/(n+1)
    lower=0.0 if k==0 else float(beta.ppf(.025,k,n-k+1))
    upper=1.0 if k==n else float(beta.ppf(.975,k+1,n-k))
    return dict(exceedance_count=k,monkey_count=n,empirical_p_value=p,
                p_resolution=1/(n+1),percentile_rank=100*float(np.count_nonzero(values<target))/(n+1),
                mc_tail_lower_95=lower,mc_tail_upper_95=upper,
                significant_95pct=p<.05)


def adjust(values):
    p=np.asarray(values,dtype=float); m=len(p)
    order=np.argsort(p,kind='stable'); ranked=p[order]; ranks=np.arange(1,m+1)
    result={'bonferroni':np.minimum(1,m*p)}
    for name,scale in [('bh',1.),('by',float(np.sum(1/ranks)))]:
        sorted_adj=np.minimum.accumulate((ranked*m*scale/ranks)[::-1])[::-1]
        out=np.empty(m);out[order]=np.minimum(1,sorted_adj);result[name]=out
    out=np.empty(m);out[order]=np.minimum(1,np.maximum.accumulate(ranked*(m-ranks+1)))
    result['holm']=out
    return result
