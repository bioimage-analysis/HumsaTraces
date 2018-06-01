import os
import numpy as np
import matplotlib.pyplot as plt
from cellsync.detect_peaks import *
import itertools
import matplotlib.colors as colors
import matplotlib.cm as cmx
from mpl_toolkits.axes_grid1 import make_axes_locatable


def find_sync(d, metadata, corr,regions_ch2, labels, cell_position, sync_time=1, show=False, sea_peak = None, save=False, path=''):
    tt = np.asarray(metadata['TimePoint'])
    window = tt[sync_time]
    indexes = []
    for count, traces in enumerate(d):
        label = count+1
        if sea_peak is not None and label == sea_peak:
            ind = detect_peaks(traces, mph=0.75, mpd=25, valley=False, show=True)
        else:
            ind = detect_peaks(traces, mph=0.75, mpd=25, valley=False, show=False)
        if ind.size>0:
            indexes.append((tt[ind].tolist(), label))

    sync = []
    for a1, b1 in indexes:
        for a2 in a1:
            sync_a = []
            for a3, b in indexes:
                if np.any(np.isclose(a2, a3, atol = window)):
                    sync_a.append((b,a2))
        sync.append(sync_a)

    label_coord = [(prop.label, prop.centroid) for prop in regions_ch2[0]]

    coord_network = []
    ind_network=[]
    for label in sync:
        coord_net = []
        net_ind = []
        for i in label:
            for coord in label_coord:
                if coord[0] == int(i[0]):
                    coord_net.append(coord[1])
                    net_ind.append(i[1])

        coord_network.append(coord_net)
        ind_network.append(net_ind)

    list_option=[]
    for coord in coord_network:
        list_beta =[]
        for x in itertools.permutations(coord, 2):
            list_beta.append(x)
        list_option.append(list_beta)

    numb_peak = []
    for ind in indexes:
        for coord in label_coord:
            if coord[0] == int(ind[1]):
                numb_peak.append((coord[1], len(ind[0])))

    if show:
        _plot(tt, corr, numb_peak, labels, cell_position, ind_network, list_option, save=save, path=path)

    return indexes, sync

def _plot(tt, corr, numb_peak, labels, cell_position, ind_network, list_option, save=False, path=''):

    values = range(int(tt.max()))
    jet = cm = plt.get_cmap('jet')
    cNorm  = colors.Normalize(vmin=0, vmax=tt.max())
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    values2 = range(np.max(np.asarray(numb_peak)[:,1])+1)
    jet2 = cm = plt.get_cmap('jet')
    cNorm2  = colors.Normalize(vmin=0, vmax=np.max(np.asarray(numb_peak)[:,1]))
    scalarMap2 = cmx.ScalarMappable(norm=cNorm2, cmap=jet2)

    plt.figure(figsize=(16,16))
    ax = plt.gca()

    im = ax.imshow(corr, cmap="gray", alpha=0.8)
    plt.axis('off')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cax2 = divider.append_axes("top", size="5%", pad=0.1)

    scalarMap2.set_array(im)
    cb2 = plt.colorbar(scalarMap2, cax=cax2, orientation='horizontal', label='Number of calcium peaks', ticks=[range(20)])
    cb2.ax.xaxis.set_label_position('top')
    cb2.ax.xaxis.set_ticks_position('top')

    scalarMap.set_array(im)
    plt.colorbar(scalarMap, cax=cax, label='time point of the synchronic firing')

    i=0
    for lab, coord in zip(labels, cell_position):
        ax.annotate(str(lab),tuple(x+5 for x in coord[::-1]), color='white', fontsize=14,weight ='bold', alpha = 0.5)
        colorVal3 = scalarMap2.to_rgba(values2[0])
        ax.scatter(coord[::-1][0], coord[::-1][1], color=colorVal3, s=100)

    for ind, net, peak in zip(ind_network, list_option, numb_peak):
        arr = np.asarray(net)
        colorVal2 = scalarMap2.to_rgba(values2[peak[1]])
        sc = ax.scatter(peak[0][1],peak[0][0], color=colorVal2, s=100)


        if arr.shape[0]>0:
            colorVal = scalarMap.to_rgba(values[int(np.mean(ind))])

            i+=1
            arr_s = np.vstack(arr)

            ax.plot(arr_s[:,1],arr_s[:,0], color=colorVal)

    if save:
        filename = 'plot_correlation.png'
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
