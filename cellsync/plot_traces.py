import os
import numpy as np
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
from skimage.measure import regionprops
from skimage import segmentation

def _dff(mean_int_over_time, window=40, percentile=20):
    traceBL = [np.percentile(mean_int_over_time[i:i + window], percentile)
                       for i in range(1, len(mean_int_over_time) - window)]
    missing = np.percentile(mean_int_over_time[-window:], percentile)
    missing = np.repeat(missing, window + 1)

    traceBL = np.concatenate((traceBL, missing))

    return np.divide((mean_int_over_time-traceBL), traceBL)

def create_traces(ch2_reg,seg_ch1):

    regions_ch2 = [regionprops(seg_ch1, ch2) for ch2 in ch2_reg]
    cell_position = [regions_ch2[0][i]['centroid'] for i in range(len(regions_ch2[0]))]
    labels = [regions_ch2[0][i]['label'] for i in range(len(regions_ch2[0]))]

    list_intensity =[]
    for i in range(len(regions_ch2[0])):
        list_intensity.append(np.asarray([regions[i]['mean_intensity'] for regions in regions_ch2]))

    list_dff=[]
    for mean_int in list_intensity:
        list_dff.append(_dff(mean_int))
    d=np.asarray(list_dff)
    data = np.transpose(d, (1,0))

    return d, data, cell_position, labels, regions_ch2

def plot_traces(corr, metadata, data, cleaned_ch1, cell_position, labels, save=False, path=''):

    t=np.asarray(metadata['TimePoint'])
    plt.figure()

    fig, (ax1,ax2) = plt.subplots(2,1, figsize=(8,16))

    #ls = LightSource(azdeg=315, altdeg=45)
    #ax.imshow(ls.hillshade(tv, vert_exag=1.5), cmap='gray', vmin=0.5, vmax = 0.8)
    ax1.imshow(corr, cmap='viridis', alpha = 0.7, vmin = 0, vmax=0.9)
    ax1.contour(segmentation.find_boundaries(cleaned_ch1, mode="outer"), linewidths=2, colors = "red", alpha=0.2)
    for lab, coord in zip(labels, cell_position):
        ax1.annotate(str(lab), coord[::-1], color='white', fontsize=14,weight ='bold')
    ax1.set_title('Correlation image and contour plots of cells')


    numSamples, numRows = data.shape


    # Plot the EEG
    ticklocs = []
    #ax2 = fig.add_subplot(1, 1, 1)
    ax2.set_xlim(0, t.max())
    #ax2.set_xticks(np.arange(40))
    dmin = data.min()
    dmax = data.max()
    dr = (dmax - dmin) * 0.7  # Crowd them a bit.
    y0 = dmin
    y1 = (numRows - 1) * dr + dmax
    ax2.set_ylim(y0, y1)

    segs = []
    for i in range(numRows):
        segs.append(np.hstack((t[:, np.newaxis], data[:, i, np.newaxis])))
        ticklocs.append(i * dr)

    offsets = np.zeros((numRows, 2), dtype=float)
    offsets[:, 1] = ticklocs

    cmap=plt.cm.viridis
    colors = cmap(np.linspace(0, 1, data.shape[1]))

    lines = LineCollection(segs, offsets=offsets, transOffset=None, colors = colors)
    ax2.add_collection(lines)

    # Set the yticks to use axes coordinates on the y axis
    ax2.set_yticks(ticklocs)
    ax2.set_yticklabels(labels)

    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('cell')
    ax2.set_title('Fluorescence traces - DF/F')

    plt.tight_layout()
    if save:
        filename = 'plot_traces.png'
        if os.path.isfile(path+filename):
            expand = 0
            while True:
                expand += 1
                new_filename = filename.split(".png")[0] + "_" +str(expand) + ".png"
                if os.path.isfile(path+new_filename):
                    continue
                else:
                    filename = new_filename
                    break
        plt.savefig(path+filename)
