# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_utils.ipynb.

# %% auto 0
__all__ = ['inplace', 'mask2idxs']

# %% ../nbs/00_utils.ipynb 4
def inplace(f):
    def _f(b):
        f(b)
        return b
    return _f

# %% ../nbs/00_utils.ipynb 5
def mask2idxs(mask): return [i for i, e in enumerate(mask) if e == True]