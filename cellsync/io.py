import os
import xml.etree.ElementTree as ET
import glob
import numpy as np
from skimage import io

def metadata(directory):
    xml_file = glob.glob(directory + '/*xml')
    to_parse = ET.parse(xml_file[0])
    root = to_parse.getroot()

    metadata = {
        "sizeT" : 0,
        "sizeX" : 0,
        "sizeY" : 0,
        "dtype" : 0,
        "shapeX" : 0,
        "shapeY" : 0,
        "TimePoint" : [],
    }

    for child in root:
        if child.tag == "PVStateShard":
            for step_child in child:
                if step_child.attrib['key'] == 'bitDepth':
                    if int(step_child.attrib['value']) > 8:
                        metadata["dtype"]="uint16"
                    else:
                        metadata["dtype"]="uint8"
                elif step_child.attrib['key'] == "pixelsPerLine":
                    metadata["shapeX"]=int(step_child.attrib['value'])
                elif step_child.attrib['key'] == "linesPerFrame":
                    metadata["shapeY"]=int(step_child.attrib['value'])

                elif step_child.attrib['key'] == 'micronsPerPixel':
                    for step_step_child in step_child:
                        if step_step_child.attrib['index'] == 'XAxis':
                            metadata["sizeX"]=float(step_step_child.attrib['value'])
                        if step_step_child.attrib['index'] == 'YAxis':
                            metadata["sizeY"]=float(step_step_child.attrib['value'])

    for seq in root.iter('Frame'):
        metadata['TimePoint'].append(round(float(seq.attrib['relativeTime']), 1))

    metadata['sizeT'] = len(metadata['TimePoint'])

    return metadata

def open_file(directory, metadata, ch = '/channel_1'):
    #list_file = [filename for filename in os.listdir(directory) if filename.endswith(".tif")]
    m = metadata

    #list_file = glob.glob(directory + ch + '/*tif')
    #list_file.sort()
    list_file = io.ImageCollection(directory + ch + '/*tif')
    stack = np.empty([m['sizeT'], m['shapeY'], m['shapeX']]).astype(m['dtype'])
    for plane, img in enumerate(list_file):
        stack[plane] = img

    return(stack)
