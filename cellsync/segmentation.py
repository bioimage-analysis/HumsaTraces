
import numpy as np
from skimage import segmentation
from skimage.measure import regionprops
from skimage.measure import label

def slic_segment(registered_img, strength = 200):
    img_split = np.split(registered_img, 50)

    img_split_median = np.median(np.stack(img_split), axis=1)

    to_seg = np.median(img_split_median,axis=0)
    segments_slic = segmentation.slic(to_seg, n_segments=750, compactness=300, sigma=0, multichannel=False)

    labeled = label(segments_slic, background=0)
    regions = regionprops(labeled, to_seg)

    intensity=[np.median(prop.intensity_image) for prop in regions]

    cleaned = np.copy(labeled)
    for intens, region in zip(intensity, regions):
        if intens<strength:
            cleaned[tuple(region.coords.T)] = 0
    cleaned = label(cleaned, background=0)


    return cleaned, to_seg
