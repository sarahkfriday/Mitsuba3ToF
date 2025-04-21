"""
Heavily modified from https://github.com/juhyeonkim95/Mitsuba3DopplerToF/blob/main/doppler_tutorials/src/main_animation.py
"""
import os
current_directory = os.getcwd()
print("current director: ", current_directory)

# os.system("source ../build/setpath.sh")
# os.system("export DRJIT_LIBLLVM_PATH=/Users/sarahfriday/anaconda3/pkgs/libllvm12-12.0.0-h12f7ac0_4/lib/libLLVM-12.dylib")

from program_runner import *

import numpy as np
from tqdm import tqdm, trange

from utils.image_utils import *
import configargparse
from utils.common_configs import *

c=3.0e8
pi = np.pi

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

def main():
    parser = configargparse.ArgumentParser()
    parser.add_argument("--scene_name", help="scene name")
    parser.add_argument("--var_axis", type=str, default='y', help="axis on which to vary the freq")
    parser.add_argument("--wave_function_type", type=str, default="sinusoidal", help="waveform")
    parser.add_argument("--scenedir", type=str, default="./", help="scene directory")
    parser.add_argument("--outputdir", type=str, default="./", help="output directory")
    parser.add_argument("--exp_time", type=float, default=0.008, help="integration time per frame in sec")
    parser.add_argument("--mod_freq", type=float, default = 24.0, help="modulation frequency in MHz")

    args = parser.parse_args()
    scene_name = args.scene_name
    wave_function_type = args.wave_function_type
    exposure_time = args.exp_time
    modulation_freq = args.mod_freq
    outputdir = args.outputdir
    var_axis = args.var_axis

    # w_o = pi / exposure_time
    # w_of = (2.0*pi) / exposure_time
    # f_o = 1.0/(2.0*exposure_time) * 1e-6 # in MHz because mod freq is in MHz
    # f_of = 1.0 / (exposure_time) * 1e-6 # in MHz because mod freq is in MHz
    
    # get scene_config
    scene_configs = get_animation_scene_configs()
    if not scene_name in scene_configs:
        print("scene name not found")
        return
    scene_config = scene_configs[scene_name]
    # get the dimensions of the images from config
    img_width = scene_config.get('resx')
    img_height = scene_config.get('resy')

    scene_base_dir = os.path.join(args.scenedir, "scenes", scene_name)

    hetero_offsets_hu = [0.75, 0.0, 0.25, 0.5]

    # set up the spatially varying freq offset
    if var_axis == 'x':
        snapshot_freq = np.linspace(0, 0.5, img_width)
        num_lines = img_width
    else:
        snapshot_freq = np.linspace(0, 0.5, img_height)
        num_lines = img_height
   
    # load the scene
    scene_filename = os.path.join(scene_base_dir, scene_name+".xml")
    scene_camera = os.path.join(scene_base_dir, scene_name+"_camera.xml")
    
    # change the crop dimension depending on if varying on x or y axis
    init_crop(scene_camera, var_axis)
    
    exit_if_file_exists = False

    # common_configs = {
    #     "time_sampling_method": "antithetic",
    #     "scene_name": scene_name,
    #     "wave_function_type": wave_function_type,
    #     "low_frequency_component_only": True,
    #     "scene": scene,
    #     "w_g": modulation_freq,
    #     "exposure_time": exposure_time,
    #     "max_depth": scene_config.get("max_depth"),
    #     "exit_if_file_exists": exit_if_file_exists,
    #     "show_progress": False
    # }
    if var_axis == 'x':
        dummy_line = np.ones((1, img_height))
    else:
        dummy_line = np.ones((img_width, 1))
    snapshot_img = []
    for i in trange(num_lines):
        scene = mi.load_file(scene_filename) # load the scene xml file

        # Render GT radiance
        # line = i * dummy_line
        line = run_scene_radiance(
            scene, 
            scene_name,
            output_file_name=None,
            exit_if_file_exists=exit_if_file_exists
        )
        snapshot_img.append(line)

        iterate_shutter(scene_camera, exposure_time)
        iterate_crop(scene_camera, var_axis)
        # (3) Render heterodyne hu et al's method, offset btw [0, 2pi/T]
        # heterodyne_image = run_scene_doppler_tof(
        #     hetero_frequency = hetero_freqs_hu[i], 
        #     hetero_offset=hetero_offsets_hu[i],
        #     output_path=outputdir,
        #     expname=heterodyne_output_file_name,
        #     **common_configs
        # )
    snapshot_img = np.squeeze(np.array(snapshot_img))
    print('snapshot_img size:', snapshot_img.shape)
    output_filename = 'snapshot_{}MHz_{}us.npy'.format(modulation_freq, exposure_time)
    output_path = os.path.join(outputdir, output_filename)
    print("Saving snapshot at ", output_path)
    np.save(output_path, snapshot_img)

    reset_shutter(scene_camera, exposure_time)
    reset_crop(scene_camera, var_axis)
    print("Experiments complete.")      

if __name__ == "__main__":
    main()