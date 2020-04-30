# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_data.core.ipynb (unless otherwise specified).

__all__ = ['Annotation', 'encodes', 'area', 'from_mask', 'PILMaskBinary', 'TensorMaskBinary', 'encodes']

# Cell
from fastai2.vision.all import *

# Cell
# Might be better to custom dispatch annotation, because of recursive tuple problem
# TODO: Dispatch transforms... Can this class inherit from tuple?
# Does it needed to be converted to TensorAnnotation?
# Why is area being converted to BBox??
class Annotation:
    keys = 'labels,boxes,area,masks,iscrowd'.split(',') # TODO: Auto insert key in create and d
#     @classmethod
    def __init__(self, labels=None, boxes=None, masks=None, iscrowd=0, area=None):
        area = boxes.area if (boxes is not None and area is None) else area
        self.d = dict(labels=labels,boxes=boxes,area=area,masks=masks,iscrowd=iscrowd)
#     @property
#     def d(self): return {k:v for k,v in zip(self.keys,self)}
    def __getitem__(self, name): return self.d.__getitem__(name)
    def __setitem__(self, n, v): return self.d.__setitem__(n, v)
    def __contains__(self, k): return k in self.d
    def __repr__(self): return self.d.__repr__()
    def to_tensor(self): return type(self)(**{k:ToTensor()(v) for k,v in self.d.items()})
    def to_device(self, device): return type(self)(**{k:to_device(v) for k,v in self.d.items()})
    def show(self, ctx, **kwargs):
        for o in self.d.values(): ctx = getattr(o,'show',noop)(ctx, **kwargs)
        return ctx

# Cell
@ToTensor
def encodes(self, o:Annotation): return o.to_tensor()

# Cell
@patch_property
def area(self:TensorBBox):
    assert len(self.shape) == 2
    b = self
    return ((b[:,3]-b[:,1])*(b[:,2]-b[:,0])).data

# Cell
@patch_to(TensorBBox, cls_method=True)
def from_mask(cls:TensorBBox, mask):
    boxes = []
    for m in mask:
        xs,ys = m.nonzero().T
        boxes.append([min(ys),min(xs),max(ys),max(xs)])
    return cls(boxes)

# Cell
class PILMaskBinary(PILMask):
    @classmethod
    def create(cls, fn): return cls(super().create(fn))

# Cell
class TensorMaskBinary(TensorMask):
    def show(self, ctx=None, **kwargs):
        mask = (self * torch.arange(1,len(self)+1).to(self.device).view(-1,1,1)).sum(0)
        return TensorMask(mask).show(ctx, **kwargs)

# Cell
@ToTensor
def encodes(self, o:PILMaskBinary):
    mask_arr = np.array(o)
    obj_ids = np.unique(mask_arr)[1:] # TODO: Hardcoded removal
    return TensorMaskBinary(mask_arr==obj_ids[:,None,None])

# Cell
@typedispatch
def show_batch(x:TensorImage, y:Annotation, samples, ctxs=None, max_n=10, nrows=None, ncols=None, figsize=None, **kwargs):
    if ctxs is None: ctxs = get_grid(min(len(samples), max_n), nrows=nrows, ncols=ncols, figsize=figsize)
    for i,ctx in enumerate(ctxs):
        for s in samples[i]: ctx = s.show(ctx, **kwargs)
    return ctxs