import numpy as np
from scipy.ndimage.filters import correlate

def correlations(Arr, neighbors = 8):
    """Computes the correlation image for the input dataset"""

    Arr = Arr.astype('float32')
    Arr -= np.mean(Arr, axis=0)
    Arr_std = np.std(Arr, axis=0)
    Arr_std[Arr_std == 0] = np.inf
    Arr /= Arr_std

    sz = np.ones((3, 3), dtype='float32')
    sz[1, 1] = 0

    if neighbors == 4:
        sz = np.array([[0,1,0],[1,0,1],[0,1,0]])

    Arr_corr = correlate(Arr, sz[np.newaxis, :], mode='constant')
    MASK = correlate(
           np.ones(Arr.shape[1:], dtype='float32'), sz, mode='constant')

    Corr = np.mean(Arr_corr * Arr, axis=0) / MASK
    return Corr
