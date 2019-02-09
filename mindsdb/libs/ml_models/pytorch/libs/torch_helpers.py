import torch
import torch.nn as nn
import uuid
import os
from mindsdb.config import CONFIG
from torch.autograd import Variable
from torch.nn import functional
from torch.nn import MSELoss
import numpy as np


def array_to_float_variable(arr):
    if CONFIG.USE_CUDA:
        ret = Variable(torch.FloatTensor(arr))
        ret = ret.cuda()
        return ret
    else:
        return Variable(torch.FloatTensor(arr))

def variable_to_array(var_to_convert):
    return np.array(var_to_convert.data.tolist())

def store_torch_object(object, id = None, path = CONFIG.MINDSDB_STORAGE_PATH):

    if id is None:
        # generate a random uuid
        id = str(uuid.uuid1())

    # create if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)
    # tmp files
    tmp_file = path + '/{id}.pt'.format(id=id)

    if not os.path.exists(path):
        os.makedirs(path)

    torch.save(object, tmp_file)

    return id, tmp_file

def get_stored_torch_object(id, path):

    # tmp files
    tmp_file = path + '/{id}.pt'.format(id=id)

    obj = torch.load(tmp_file)

    return obj


class RMSELoss(nn.Module):

    def __init__(self):
        super(RMSELoss, self).__init__()
        self.loss =  torch.nn.MSELoss()

    def forward(self, input, target):
        return torch.sqrt(self.loss(input, target))


def log_loss(input, target, size_average=None, reduce=None, reduction='elementwise_mean'):
    r"""mse_loss(input, target, size_average=None, reduce=None, reduction='elementwise_mean') -> Tensor

    Measures the element-wise mean squared error.

    See :class:`~torch.nn.MSELoss` for details.
    """
    if size_average is not None or reduce is not None:
        reduction = functional._Reduction.legacy_get_enum(size_average, reduce)
    else:
        reduction = functional._Reduction.get_enum(reduction)
    l = lambda a, b: (torch.log(a)/torch.log(b)-1) ** 2

    return functional._pointwise_loss(l, l, input, target, reduction)


class LogLoss(MSELoss):

    def __init__(self):
        super(LogLoss, self).__init__()
        self.loss = torch.nn.MSELoss()
        self.loss2 = torch.nn.MSELoss()


    def forward(self, input, target):

        tgt = torch.atan(target)
        inp = torch.atan(input)

        loss = torch.sqrt(self.loss(inp, tgt))
        return loss
