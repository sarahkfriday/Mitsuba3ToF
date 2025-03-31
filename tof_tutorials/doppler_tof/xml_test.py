import xml.etree.ElementTree as ET

def change_child_xml_element(filename, parent_tag, child_tags, child_names, child_new_vals):
    xml_file = ET.parse(filename)
    root = xml_file.getroot()
    for i, c in enumerate(child_tags):
        # get the correct element
        element=root.find(".//{}/{}[@name='{}']".format(parent_tag, c, child_names[i]))
        # set the new value
        element.set('value', str(child_new_vals[i]))
    # write out to file
    xml_file.write(filename)

def change_parent_xml_element(filename, parent_tags, parent_new_vals):
    xml_file = ET.parse(filename)
    root = xml_file.getroot()
    for i, p in enumerate(parent_tags):
        # get the correct element
        element=root.find(".//{}".format(p))
        # set the new value
        element.set('type', str(parent_new_vals[i]))
    # write out to file
    xml_file.write(filename)

def change_shutter_close(filepath, new_val):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    # get the correct element
    element=root.find(".//sensor/float[@name='shutter_close']")
    # set the new value
    element.set('value', str(new_val))
    # write out to file
    xml_file.write(filepath)

def set_line_dim(filepath, new_val, axis):
    xml_file = ET.parse(filepath)
    root = xml_file.getroot()
    if axis=='x':
        crop_name = 'crop_width'
    else:
        crop_name = 'crop_height'
    # get the correct element
    element=root.find(".//sensor/film/integer[@name='{}']".format(crop_name))
    # set the new value
    element.set('value', str(new_val))
    # write out to file
    xml_file.write(filepath)

def main():
    scene_filename = "/Users/sarahfriday/Documents/Mitsuba3ToF/scenes/moving_cubes/moving_cubes.xml"
    set_line_dim(scene_filename, 10, 'x')

if __name__ == "__main__":
    main()