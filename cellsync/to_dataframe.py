import os
import pandas as pd
import numpy as np

def to_df(indexes, sync, peak_value, d, metadata, save=False, path=''):

    Time = metadata['TimePoint']

    df = pd.DataFrame(index=range(1, len(d)+1),
                      columns=['Nbr of Peaks', 'Nbr of Sync Cells',
                               'Peak Position', 'Peak Value', 'Sync cells'])
    '''print(len(peak_value))
    print(len(sync))
    print(len(indexes))
    for x,y,z in zip(indexes,sync, peak_value):
        print(x[1])
        df.loc[x[1]]['Nbr of Peaks']=len(x[0])
        df.loc[x[1]]['Peak Position']=x[0]
        df.loc[x[1]]['Nbr of Sync Cells']=len(y)
        #df.loc[x[1]]['Sync cells']=np.asarray(y)[:,0].astype('int').tolist()
        df.loc[x[1]]['Sync cells']=y
        df.loc[z[1]]['Peak Value']=z[0]
    '''

    for x,y in zip(indexes, peak_value):
        df.loc[x[1]]['Nbr of Peaks']=len(x[0])
        df.loc[x[1]]['Peak Position']=x[0]
        df.loc[y[1]]['Peak Value']=y[0]

    for z in sync:
        df.loc[z[0]]['Nbr of Sync Cells']=len(z[1])
        df.loc[z[0]]['Sync cells']=z[1]

    df['Synchronicity']=df['Nbr of Sync Cells'].div(df['Nbr of Peaks'], axis=0)
    df = df.fillna(0)
    df = df.round({'Synchronicity':2})
    df1 = pd.DataFrame(d, index=range(1, len(d)+1),
                       columns=Time)
    if save:
        filename = 'result.xlsx'
        if os.path.isfile(path+filename):
            expand = 0
            while True:
                expand += 1
                new_filename = filename.split(".xlsx")[0] + "_" +str(expand) + ".xlsx"
                if os.path.isfile(path+new_filename):
                    continue
                else:
                    filename = new_filename
                    break
        writer = pd.ExcelWriter(path+"_"+filename)
        df.to_excel(writer,'Sheet1')
        df1.to_excel(writer,'Sheet2')
        writer.save()
    return(df, df1)
