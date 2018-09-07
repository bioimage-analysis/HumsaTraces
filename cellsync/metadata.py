import os

def log_file(**kwargs):
    path = kwargs['path']
    save = kwargs['save']
    filename_roi = kwargs['filename_roi']
    strength = kwargs['strength']
    window_deltaF = kwargs['window_deltaF']
    to_remove = kwargs['to_remove']
    if save:
        path_name = path.replace("/","_")
        filename = path_name+'_lof_file'+filename_roi+'.txt'
        if os.path.isfile(path+'/'+filename):
            expand = 0
            while True:
                expand += 1
                new_filename = filename.split(".txt")[0] + "_" +str(expand) + ".txt"
                if os.path.isfile(path+new_filename):
                    continue
                else:
                    filename = new_filename
                    break
        with open(path+'/'+filename,'w') as file:
            file.write('Intensity threshold for segmentation strength : {}\n'\
                       'Size of the window used to create Delta F/F0 traces: {}\n'\
                       'Cell {} was removed from the analysis'\
                       .format(str(strength),str(window_deltaF), str(to_remove)))
