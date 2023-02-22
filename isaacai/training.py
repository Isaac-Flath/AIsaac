# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/41_training.ipynb.

# %% auto 0
__all__ = ['NBatchCB', 'BasicTrainCB', 'DeviceCB', 'MomentumTrainCB', 'BaseSchedulerCB', 'BatchSchedulerCB', 'EpochSchedulerCB',
           'OneCycleSchedulerCB']

# %% ../nbs/41_training.ipynb 4
from .utils import *
from .dataloaders import *
from .models import *
from .initialization import *
from .trainer import *

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
from accelerate import Accelerator

# %% ../nbs/41_training.ipynb 11
class NBatchCB(Callback):
    def __init__(self,n_batches=1): fc.store_attr()
    def before_batch(self,trainer):
        if trainer.batch_num >= self.n_batches: raise CancelEpochException

# %% ../nbs/41_training.ipynb 12
class BasicTrainCB(Callback):
    '''Callback for basic pytorch training loop'''
    def predict(self,trainer): trainer.preds = trainer.model(trainer.batch[0])
    def get_loss(self,trainer): trainer.loss = trainer.loss_func(trainer.preds,trainer.batch[1])
    def backward(self,trainer): trainer.loss.backward()
    def step(self,trainer): trainer.opt.step()
    def zero_grad(self,trainer): trainer.opt.zero_grad()

# %% ../nbs/41_training.ipynb 13
class DeviceCB(Callback):
    '''Callback to train on specific device'''
    def __init__(self, device=def_device): self.device=device
    def before_fit(self, trainer):
        '''Moves model to device'''
        if hasattr(trainer.model, 'to'): trainer.model.to(self.device)
    def before_batch(self, trainer): 
        '''moves batch to device'''
        trainer.batch = to_device(trainer.batch, device=self.device)

# %% ../nbs/41_training.ipynb 14
class MomentumTrainCB(BasicTrainCB):
    def __init__(self,momentum): self.momentum = momentum
    def zero_grad(self,trainer): 
        '''Multiply grads by momentum (instead of zero)'''
        with torch.no_grad():
            for p in trainer.model.parameters(): p.grad *= self.momentum

# %% ../nbs/41_training.ipynb 19
class BaseSchedulerCB(Callback):
    def __init__(self, scheduler_func): fc.store_attr()
    def before_fit(self, trainer): 
        '''Initializes scheduled with opt'''
        self.scheduler = self.scheduler_func(trainer.opt)
    def _step(self, trainer):
        if trainer.training: self.scheduler.step()

# %% ../nbs/41_training.ipynb 20
class BatchSchedulerCB(BaseSchedulerCB):
    '''Steps scheduler'''
    def after_batch(self, trainer): self._step(trainer) 
    
class EpochSchedulerCB(BaseSchedulerCB):
    '''Steps scheduler'''
    def after_epoch(self, trainer): self._step(trainer)   

# %% ../nbs/41_training.ipynb 21
class OneCycleSchedulerCB(BatchSchedulerCB):
    @fc.delegates(to=torch.optim.lr_scheduler.OneCycleLR,
                  but=['optimizer','max_lr','total_steps','steps_per_epoch','epochs'])
    def __init__(self,**kwargs):
        self.scheduler_kwargs = kwargs
        self.scheduler_func =  torch.optim.lr_scheduler.OneCycleLR
    
    def before_fit(self,trainer):
        '''Initializes Scheduler'''
        total_steps = trainer.n_epochs*len(trainer.dls.train)
        self.scheduler = self.scheduler_func(trainer.opt, max_lr=trainer.lr, total_steps=total_steps,**self.scheduler_kwargs)
