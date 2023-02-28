# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/44_augmentation.ipynb.

# %% auto 0
__all__ = ['BatchAugmentationCB', 'UnNormalize', 'show_image_batch']

# %% ../nbs/44_augmentation.ipynb 4
from .utils import *
from .dataloaders import *
from .models import *
from .initialization import *
from .trainer import *
from .training import *
from .recording import *
from .visualization import *
from .cb_groups import *

from datetime import datetime, timedelta
import torchvision.transforms.functional as TF,torch.nn.functional as F
import math, time

import matplotlib.pyplot as plt
import matplotlib as mpl
import fastcore.all as fc
import torch
from torch import nn, Tensor
from datasets import load_dataset, Dataset
from torch.utils.data import DataLoader
import pandas as pd , numpy as np
from torcheval.metrics import MulticlassAccuracy,Mean
from torch.optim.lr_scheduler import ExponentialLR

import dill as pickle
from fastprogress.fastprogress import master_bar, progress_bar
import inspect
import torchinfo
from torchvision import transforms
from itertools import zip_longest

# %% ../nbs/44_augmentation.ipynb 10
class BatchAugmentationCB(Callback):
    def __init__(self,tfms): self.tfms = fc.L(tfms)
    def before_batch(self,trainer):
        '''applies tfms in tfms list to appropriate items in batch'''
        trainer.batch = fc.L(tfm(item) for tfm,item in zip_longest(self.tfms,trainer.batch,fillvalue=fc.noop))

# %% ../nbs/44_augmentation.ipynb 11
class UnNormalize:
    def __init__(self, mean, std): fc.store_attr()
    def __call__(self, tensor):
        for t, m, s in zip(tensor, self.mean, self.std): t.mul_(s).add_(m)
        return tensor

# %% ../nbs/44_augmentation.ipynb 12
@fc.patch
@fc.delegates(show_images)
def show_image_batch(self:Trainer, max_n=9, callbacks=None, **kwargs):
    self.fit(1, callbacks=[OneBatchCB()]+fc.L(callbacks))
    show_images(self.batch[0][:max_n], **kwargs)