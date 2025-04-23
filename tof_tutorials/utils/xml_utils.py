import xml.etree.ElementTree as ET

def get_dimensions(filepath):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    width_element=root.find(".//sensor/film/integer[@name='width']") 
    height_element=root.find(".//sensor/film/integer[@name='height']")
    width = int(width_element.get('value'))
    height = int(height_element.get('value'))
    return [width, height]

def get_shutter_open(filepath):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    open_element=root.find(".//sensor/float[@name='shutter_open']") # get the correct element
    shutter_open = open_element.get('value', str(0.0))
    return float(shutter_open)

'''
    Change shutter_close
    does not change shutter_close if new value matches previous

    filepath - where to find the file
    new_val - new value for shutter_close
'''
def change_shutter_close(filepath, new_val):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    # get the correct element
    element=root.find(".//sensor/float[@name='shutter_close']")
    if element.get('value') != str(new_val):
        # set the new value
        element.set('value', str(new_val))
        # write out to file
        xml_file.write(filepath)

'''
    Change a parent element of xml scene file
    filepath - where to find the file
    parent_tag - string of parent tags id ex: ['sensor', 'emitter', 'bsdf']
    parent_new_vals - list of new values for that element
'''
def change_parent_scene_element(filepath, parent_tags, parent_new_vals):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    for i, p in enumerate(parent_tags):
        # get the correct element
        element=root.find(".//{}".format(p))
        # set the new value
        element.set('type', str(parent_new_vals[i]))
    # write out to file
    xml_file.write(filepath)

def reset_shutter(filepath, exposure_time, open=0.0):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    element=root.find(".//sensor/float[@name='shutter_open']") # get the correct element
    if open != 0.0:
        element.set('value', str(open))
    else:    
        element.set('value', str(0.0))

    element=root.find(".//sensor/float[@name='shutter_close']") # get the correct element
    element.set('value', str(open+exposure_time))
    
    # write out to file
    xml_file.write(filepath)


'''
    Change line offset for snapshot emulation
    filepath - where to find the file
    new_val - new value for line crop offset
    axis - x or y
'''
def iterate_shutter(filepath, exposure_time):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()

    open_element=root.find(".//sensor/float[@name='shutter_open']") # get the correct element
    close_element=root.find(".//sensor/float[@name='shutter_close']") # get the correct element
    
    prev_open = float(open_element.get('value', 0.0))
    prev_close = float(close_element.get('value', 0.0))
    # print('previous open: ', prev_open)
    # print('previous close: ', prev_close)

    # set the new value
    open_element.set('value', str(prev_close))
    close_element.set('value', str(prev_close+exposure_time))

    # write out to file
    xml_file.write(filepath)

def init_crop(filepath, var_axis):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    
    if var_axis == 'x':
        crop_element=root.find(".//sensor/film/integer[@name='crop_width']") # get the correct element
    else:
        crop_element=root.find(".//sensor/film/integer[@name='crop_height']") # get the correct element

    crop_element.set('value', str(1))
    
    # write out to file
    xml_file.write(filepath)


'''
    Change line offset for snapshot emulation
    filepath - where to find the file
    new_val - new value for line crop offset
    axis - x or y
'''
def iterate_crop(filepath, var_axis):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    
    if var_axis == 'x':
        crop_element=root.find(".//sensor/film/integer[@name='crop_offset_x']") # get the correct element
        crop_size = root.find(".//sensor/film/integer[@name='width']")
    else:
        crop_element=root.find(".//sensor/film/integer[@name='crop_offset_y']") # get the correct element
        crop_size = root.find(".//sensor/film/integer[@name='height']")

    max_crop_offset = int(crop_size.get('value'))
    prev_crop_offset = int(crop_element.get('value', 0.0))
    next_crop_offset = int(prev_crop_offset+1)
    
    if next_crop_offset < max_crop_offset:
        # iterate 1 line
        crop_element.set('value', str(next_crop_offset))

        # write out to file
        xml_file.write(filepath)

def reset_crop(filepath, var_axis):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    
    if var_axis == 'x':
        crop_offset_element=root.find(".//sensor/film/integer[@name='crop_offset_x']") # get the correct element
        crop_dim_element=root.find(".//sensor/film/integer[@name='crop_width']")
        crop_size = root.find(".//sensor/film/integer[@name='width']")
    else:
        crop_offset_element=root.find(".//sensor/film/integer[@name='crop_offset_y']") # get the correct element
        crop_dim_element=root.find(".//sensor/film/integer[@name='crop_height']")
        crop_size = root.find(".//sensor/film/integer[@name='height']")
    
    reset_val = crop_size.get('value')
    crop_offset_element.set('value', str(0))
    crop_dim_element.set('value', reset_val)

    # write out to file
    xml_file.write(filepath)