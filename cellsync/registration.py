import numpy as np
from skimage.measure import LineModelND, ransac
from scipy.interpolate import interp1d
from skimage.feature import register_translation
from scipy.ndimage.interpolation import shift

def list_shift(img):

    if len(img)%200!=0:
        size = len(img)-len(img)%200
        split = len(img[0:size])/200
        l = np.split(img[0:size], split)
        l.append(img[size:len(img)])
    else:
        split = len(img)/200
        l = np.split(img, split)

    values = [100,200]

    shifts = np.zeros(2)
    add=0
    for im in l:
        i=0
        for val in values:
            if i%4==0:
                add = shifts[-1]
            try:
                shift, _, _ = register_translation(im[0], im[val], 100)
                shift = shift+add
            except IndexError:
                shift, _, _ = register_translation(im[0], im[val-1], 100)
                shift = shift+add
                shifts = np.vstack((shifts, shift))
                break
            shifts = np.vstack((shifts, shift))
            i+=1


    return(shifts)

def registration(img, shifts):
    #Find outliers
    _, inliers = ransac(shifts, LineModelND, min_samples=2,
                               residual_threshold=1, max_trials=1000)

    x = np.linspace(0, len(img), num=len(shifts[inliers]), endpoint=True)
    xnew = np.linspace(0, 1000, num=1000, endpoint=True)
    x_x = shifts[inliers,0]
    x_y = shifts[inliers,1]

    f_x = interp1d(x, x_x, kind='linear')
    f_y = interp1d(x, x_y, kind='linear')

    #plt.figure()
    #plt.plot(x, x_x, 'o', xnew, f_x(xnew), '-')

    registered_img = np.empty_like(img)

    for plane, image in enumerate(img):
        registered_img[plane] = shift(image, (float(f_x(plane)), float(f_y(plane))))
    return(registered_img)
