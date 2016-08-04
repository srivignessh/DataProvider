#!/usr/bin/env python
__doc__ = """

Functions for data transformation.

Kisuk Lee <kisuklee@mit.edu>, 2016
"""

from collections import OrderedDict
import numpy as np
from utils import *
from vector import Vec3d, minimum, maximum

def transform_tensor(func, data, *args, **kwargs):
    """Apply func to each channel of data (4D tensor)."""
    data = check_tensor(data)
    arrs = list()
    f = globals()[func]
    for c in xrange(data.shape[0]):
        vol = f(data[c,...], *args, **kwargs)
        arrs.append(check_tensor(vol))
    return np.concatenate(arrs, axis=0)


class SampleFunction(object):
    """
    TODO(kisuk): Documentation.
    """

    def __getattr__(self, name):
        def transform_fn(sample, *args, **kwargs):
            return self._transform_sample(name, sample, *args, **kwargs)
        return transform_fn

    def _transform_sample(self, func, sample, *args, **kwargs):
        """Apply func to a sample."""
        ret = OrderedDict()
        for key, data in sample.iteritems():
            ret[key] = transform_tensor(func, data, *args, **kwargs)
        return ret


class TensorFunction(object):
    """
    TODO(kisuk): Documentation.
    """

    def __getattr__(self, func):
        def transform_fn(data, *args, **kwargs):
            return transform_tensor(func, data, *args, **kwargs)
        return transform_fn

    def evaluate(self, data, spec):
        d = dict(spec)
        func = d['type']
        del d['type']
        return transform_tensor(func, data, **d)


sample_func = SampleFunction()
tensor_func = TensorFunction()


def crop(img, offset=(0,0,0), size=None):
    """
    TODO(kisuk): Documentation.
    """
    img = check_volume(img)
    if size is None:
        size = tuple(Vec3d(img.shape) - Vec3d(offset))
    ret = np.zeros(size, dtype=img.dtype)
    v1  = Vec3d(offset)
    v2  = v1 + Vec3d(size)
    ret[:] = img[v1[0]:v2[0],v1[1]:v2[1],v1[2]:v2[2]]
    return ret

####################################################################
## Preprocessing
####################################################################

def mirror_border(img, fov):
    """
    TODO(kisuk) Documentation.
    """
    img = check_volume(img)

    # Validate FoV
    fov = np.asarray(fov)
    fov = Vec3d(fov.astype('uint32'))

    # Pad size
    top = fov / 2
    btm = fov - top - (1,1,1)
    pad_with = [(top[0],btm[0]),(top[1],btm[1]),(top[2],btm[2])]
    # TODO(kisuk): Should we force an odd-sized fov?

    # TODO(kisuk): 'symmetric' or 'reflect'?
    return np.pad(img, pad_with, mode='reflect')


def standardize(img, mode='2D', dtype='float32'):
    """Standard normalization (zero mean, unit standard deviation)."""
    img = check_volume(img)
    ret = np.zeros(img.shape, dtype=dtype)

    # Standardize function (zero mean & unit standard deviation).
    f = lambda x: (x - np.mean(x)) / np.std(x)

    if mode == '2D':
        for z in xrange(img.shape[0]):
            ret[z,:,:] = f(img[z,:,:])
    elif mode == '3D':
        ret[:] = f(img)
    else:
        raise RuntimeError("mode must be either '2D' or '3D'")

    return ret

####################################################################
## Data Augmentations
####################################################################

def flip(data, rule):
    """Flip data according to a specified rule.

    Args:
        data: 3D numpy array to be transformed.
        rule: Transform rule, specified as a Boolean array.
             [z reflection,
              y reflection,
              x reflection,
              xy transpose]

    Returns:
        data: Transformed data.
    """
    data = check_tensor(data)

    assert np.size(rule)==4

    # z reflection
    if rule[0]:
        data = data[:,::-1,:,:]
    # y reflection
    if rule[1]:
        data = data[:,:,::-1,:]
    # x reflection
    if rule[2]:
        data = data[:,:,:,::-1]
    # Transpose in xy.
    if rule[3]:
        data = data.transpose(0,1,3,2)

    return data

####################################################################
## Label Transformations
####################################################################

def binarize(img, dtype='float32'):
    """Binarize image.

    Normally used to turn a ground truth segmentation into a ground truth
    boundary map, binary representation for each voxel being neuronal boundary
    or not.

    Args:
        img: 3D indexed image, with each index corresponding to each segment.

    Returns:
        ret: Binarized image.
    """
    img = check_volume(img)
    ret = np.zeros(img.shape, dtype=dtype)
    ret[:] = (img>0).astype(dtype)
    return ret


def multiclass_expansion(img, N, dtype='float32'):
    """
    TODO(kisuk): Semantic segmentation.
    """
    img = check_volume(img)
    ret = np.zeros((N,) + img.shape, dtype=dtype)
    for l in range(N):
        ret[l,...] = (img == l)
    return ret


def binary_class(img, dtype='float32'):
    """
    TODO(kisuk): Documentation.
    """
    img = check_volume(img)
    img = binarize(img, dtype=dtype)
    return multiclass_expansion(img, N=2, dtype=dtype)


def affinitize(img, dtype='float32'):
    """
    Transform segmentation to 3D affinity graph.

    Args:
        img: 3D indexed image, with each index corresponding to each segment.

    Returns:
        ret: 3D affinity graph (4D tensor), 3 channels for z, y, x direction.
    """
    img = check_volume(img)
    ret = np.zeros((3,) + img.shape, dtype=dtype)

    ret[2,1:,:,:] = (img[1:,:,:]==img[:-1,:,:]) & (img[1:,:,:]>0)  # z affinity
    ret[1,:,1:,:] = (img[:,1:,:]==img[:,:-1,:]) & (img[:,1:,:]>0)  # y affinity
    ret[0,:,:,1:] = (img[:,:,1:]==img[:,:,:-1]) & (img[:,:,1:]>0)  # x affinity

    return ret

####################################################################
## Mask Transformations
####################################################################

def affinitize_mask(msk, dtype='float32'):
    """
    Transform binary mask to affinity mask.

    Args:
        msk: 3D binary mask.

    Returns:
        ret: 3D affinity mask (4D tensor), 3 channels for z, y, x direction.
    """
    msk = check_volume(msk)
    ret = np.zeros((3,) + msk.shape, dtype=dtype)

    ret[2,1:,:,:] = (msk[1:,:,:]>0) | (msk[:-1,:,:]>0)  # z affinity
    ret[1,:,1:,:] = (msk[:,1:,:]>0) | (msk[:,:-1,:]>0)  # y affinity
    ret[0,:,:,1:] = (msk[:,:,1:]>0) | (msk[:,:,:-1]>0)  # x affinity

    return ret

####################################################################
## Rebalancing
####################################################################

def rebalance_class(img, dtype='float32'):
    """
    TODO(kisuk): Documentation.
    """
    img = check_volume(img)
    ret = np.zeros(img.shape, dtype=dtype)

    num_lbls = list()
    unique_lbl = np.unique(img)
    for lbl in unique_lbl:
        num_lbl = np.count_nonzero(img==lbl)
        num_lbls.append(num_lbl)
    assert(len(num_lbls)>0)

    if len(num_lbls)==1:
        # TODO(kisuk):
        #   This is to make rebalancing exactly the same as in ZNNv1 and v4,
        #   but not sure about how reasonable this value (0.5) is, and about
        #   if this can also be applied to multiclass case (e.g. semantic
        #   segmentation).
        ret[:] = 0.5
    else:
        weights = 1.0/np.asarray(num_lbls)
        weights = weights/np.sum(weights)
        for idx, lbl in enumerate(unique_lbl):
            ret[img==lbl] = weights[idx]

    return ret

########################################################################
## Unit Testing
########################################################################
if __name__ == "__main__":

    import unittest

    ####################################################################
    class UnitTestTransform(unittest.TestCase):

        def setup(self):
            pass

        def testCrop(self):
            img = np.random.rand(4,4,4)
            a = crop(img, (3,3,3))
            b = img[:-1,:-1,:-1]
            self.assertTrue(np.array_equal(a,b))
            a = crop(img, (3,3,3), (1,1,1))
            b = img[1:,1:,1:]
            self.assertTrue(np.array_equal(a,b))

    ####################################################################
    unittest.main()

    ####################################################################
