import os
import numpy as np
import matplotlib.pyplot as plt
from cellsync.detect_peaks import *
import itertools
import matplotlib.colors as colors
import matplotlib.cm as cmx
from mpl_toolkits.axes_grid1 import make_axes_locatable


def find_sync(d, metadata, corr,regions_ch2, labels, cell_position, sync_time=1,
              roi = False, tmin = 2000, tmax = 3000, dmin = 39, dmax = 48,
              show=False, sea_peak = None, save=False, path=''):
    tt = np.asarray(metadata['TimePoint'])
    dmin = dmin-1
    if roi == True:
        tt = tt[tmin:tmax]
        regions_ch2 = regions_ch2[tmin:tmax]
        d = d[dmin:dmax, tmin:tmax]
    window = tt[sync_time]
    indexes = []
    peak_value = []
    if roi == False:
        dmin = 0
    for count, traces in enumerate(d):
        label = count+1+dmin
        if sea_peak is not None and label == sea_peak:
            ind, spike = detect_peaks(traces, mph=0.3, mpd=40,
                                       title = sea_peak,
                                       valley=False,
                                       show=True, save = save, path=path)
        else:
            ind, spike = detect_peaks(traces, mph=0.3, mpd=40, valley=False, show=False)
        if ind.size>0:
            indexes.append((tt[np.rint(spike).astype(int)].tolist(), label))
        peak_value.append((np.around(traces[ind], decimals=2), label))
    '''
    sync = []
    for a1, b1 in indexes:
        for a2 in a1:
            sync_a = []
            for a3, b in indexes:
                if np.any(np.isclose(a2, a3, atol = window)):
                    sync_a.append((b,a2))
        sync.append(sync_a)
    '''

    import itertools
    sync = []
    sync_df = []
    for a, b in itertools.permutations(indexes, 2):
        for num in a[0]:
            for num2 in b[0]:
                if num-window <= num2 <= num+window:
                    sync_a = (b[1], num2)
                    sync.append(((a[1], num), sync_a))
                    sync_df.append((a[1],b[1]))
    from operator import itemgetter
    sync_to_df = [(k, list(set(list(zip(*g))[1]))) for k, g in itertools.groupby(sync_df, itemgetter(0))]

    if roi == True:
        label_coord = [(prop.label, prop.centroid) for prop in regions_ch2[0][dmin:dmax]]
    else:
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

    '''
    list_option=[]
    for coord in coord_network:
        list_beta =[]
        for x in itertools.permutations(coord, 2):
            list_beta.append(x)
        list_option.append(list_beta)

    '''
    numb_peak = []
    for ind in indexes:
        for coord in label_coord:
            if coord[0] == int(ind[1]):
                numb_peak.append((coord[1], len(ind[0])))

    if show:
        _plot(tt, corr, numb_peak, labels, cell_position, ind_network, coord_network, save=save, path=path)

    return indexes, sync_to_df, peak_value

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
        ax.annotate(str(lab),tuple(x+5 for x in coord[::-1]), color='red', fontsize=14,weight ='bold', alpha = 0.5)
        colorVal3 = scalarMap2.to_rgba(values2[0])
        ax.scatter(coord[::-1][0], coord[::-1][1], color=colorVal3, s=100)

    for peak in numb_peak:
        colorVal2 = scalarMap2.to_rgba(values2[peak[1]])
        sc = ax.scatter(peak[0][1],peak[0][0], color=colorVal2, s=100)

    for ind, net in zip(ind_network, list_option):
        arr = np.asarray(net)
        if arr.shape[0]>0:
            colorVal = scalarMap.to_rgba(values[int(np.mean(ind))])

            i+=1
            arr_s = np.vstack(arr)

            ax.plot(arr_s[:,1],arr_s[:,0], color=colorVal)

    if save:
        filename = 'plot_correlation.pdf'
        if os.path.isfile(path+filename):
            expand = 0
            while True:
                expand += 1
                new_filename = filename.split(".pdf")[0] + "_" +str(expand) + ".pdf"
                if os.path.isfile(path+new_filename):
                    continue
                else:
                    filename = new_filename
                    break
        plt.savefig(path+"_"+filename, transparent=True)
