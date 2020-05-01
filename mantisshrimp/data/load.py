# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_data.load.ipynb (unless otherwise specified).

__all__ = ['Bucket', 'old_do_call', 'detect_batch_to_samples', 'DetectDataLoader', 'to_concat2', 'old_to_concat',
           'nested_reorder2']

# Cell
import fastai2
from fastai2.vision.all import *

# Cell
class Bucket:
    def __init__(self, items): self.items = items

    def __getitem__(self, idx): return self._get(idx) if is_indexer(idx) else Bucket(self._get(idx))
    def _get(self, i):
        if is_indexer(i) or isinstance(i,slice): return getattr(self.items,'iloc',self.items)[i]
        i = mask2idxs(i)
        return (self.items.iloc[list(i)] if hasattr(self.items,'iloc')
                else self.items.__array__()[(i,)] if hasattr(self.items,'__array__')
                else [self.items[i_] for i_ in i])

    def tolist(self): return list(self.items)
    def map(self, f): return type(self)(type(self.items)(f(o) for o in self.items))
    def to_device(self, device): return type(self)(to_device(self.items))
    @property
    def shape(self): return (len(self.items),) # Needed for find_bs

    def __eq__(self, other): return self.items == other
    def __len__(self): return len(self.items)
    def __repr__(self): return f'<{self.__class__.__name__}: {self.items.__repr__()}>'

# Cell
old_do_call = Transform._do_call
def _do_call(self, f, x, **kwargs):
    if isinstance(x, Bucket):
        _f = lambda o: retain_type(f(o, **kwargs), o, f.returns_none(o))
        return x if f is None else x.map(_f)
    return old_do_call(self, f, x, **kwargs)
Transform._do_call = _do_call

# Cell
def _bucket_collate(t): return Tuple(Bucket(o) for o in zip(*t))
def _bucket_convert(t): raise NotImplementedError

# Cell
def detect_batch_to_samples(b, max_n=10):
    zipped = []
    for i in range(min(len(b[0]), max_n)):
        zipped.append(Tuple([o[i] for o in b]))
    return zipped

# Cell
class DetectDataLoader(TfmdDL):
    def create_batch(self, b): return (_bucket_collate,_bucket_convert)[self.prebatched](b)

    def _decode_batch(self, b, max_n=9, full=True):
        f = self.after_item.decode
        f = compose(f, partial(getattr(self.dataset,'decode',noop), full = full))
        return L(detect_batch_to_samples(b, max_n=max_n)).map(f)

    def show_batch(self, b=None, max_n=9, ctxs=None, show=True, unique=False, **kwargs):
        if unique:
            old_get_idxs = self.get_idxs
            self.get_idxs = lambda: Inf.zeros
        if b is None: b = self.one_batch()
        if not show: return self._pre_show_batch(b, max_n=max_n)
        show = show_batch[type(b[0][0]), type(b[1][0])]
        pb = self._pre_show_batch(b, max_n=max_n)
        show(*pb, ctxs=ctxs, max_n=max_n, **kwargs)
        if unique: self.get_idxs = old_get_idxs

# Cell
old_to_concat = fastai2.torch_core.to_concat
def to_concat2(xs, dim=0):
    if isinstance(xs[0], Bucket): return type(xs[0])([to_concat2([x[i] for x in xs], dim=dim) for i in range_of(xs[0])])
    return old_to_concat(xs, dim=dim)
fastai2.torch_core.to_concat = to_concat2

# Cell
_old_nested_reorder = fastai2.torch_core.nested_reorder
def nested_reorder2(t, idxs):
    if isinstance(t, Bucket):
        return t[idxs]
    return _old_nested_reorder(t, idxs)
fastai2.torch_core.nested_reorder = nested_reorder2