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
from utils.xml_utils import *
import configargparse
from utils.common_configs import *

c=3.0e8
pi = np.pi


def main():
    parser = configargparse.ArgumentParser()
    parser.add_argument("--scene_name", help="scene name")
    parser.add_argument("--scenedir", type=str, default="./", help="scene directory")
    parser.add_argument("--outputdir", type=str, default="./", help="output directory")
    parser.add_argument("--var_axis", type=str, default='y', help="axis on which to vary the freq")
    parser.add_argument("--exp_time", type=float, default=0.008, help="integration time per frame in sec")
    parser.add_argument("--mod_freq", type=float, default = 24.0, help="modulation frequency in MHz")
    parser.add_argument("--max_depth", type=int, default=2, help='max path depth')
    parser.add_argument("--spp", type=int, default=1024, help='samples per pixel')
    parser.add_argument("--wave_function_type", type=str, default="sinusoidal", help="waveform")

    args = parser.parse_args()
    scene_name = args.scene_name
    wave_function_type = args.wave_function_type
    exposure_time = args.exp_time
    modulation_freq = args.mod_freq
    outputdir = args.outputdir
    var_axis = args.var_axis
    max_depth = args.max_depth
    spp = args.spp

    # w_o = pi / exposure_time
    # w_of = (2.0*pi) / exposure_time
    # f_o = 1.0/(2.0*exposure_time) * 1e-6 # in MHz because mod freq is in MHz
    # f_of = 1.0 / (exposure_time) * 1e-6 # in MHz because mod freq is in MHz

    scene_base_dir = os.path.join(args.scenedir, "scenes", scene_name)
    # load the scene
    scene_filename = os.path.join(scene_base_dir, scene_name+".xml")
    scene_camera = os.path.join(scene_base_dir, scene_name+"_camera.xml")
    
    # get the dimensions of the images
    img_width, img_height = get_dimensions(scene_camera)
    
    # set up the spatially varying freq offset
    omega = 2.0*pi*modulation_freq
    k = (1.0/(2*exposure_time)) * 1e-6
    if var_axis == 'x':
        snapshot_freq = np.linspace(0, 1.0, img_width)
        num_lines = img_width
        line_exposure = exposure_time / img_width

    else:
        snapshot_freq = np.linspace(0, 1.0, img_height)
        num_lines = img_height
        line_exposure = exposure_time / img_height

    print('exposure time per line (sec): ', line_exposure)
    
    # change the shutter close time to match line exposure time
    reset_shutter(scene_camera, line_exposure)

    # change the crop dimension depending on if varying on x or y axis
    init_crop(scene_camera, var_axis)

    # define some common tof rendering configs
    tof_configs = {
        "w_g": modulation_freq,
        "exposure_time": line_exposure,
        "max_depth": max_depth,
        "path_correlation_depth": 2,
        "time_sampling_method": "antithetic",
        "antithetic_shift": 0.5,
        "total_spp": spp,
        "wave_function_type": wave_function_type,
        "low_frequency_component_only": True,
        "use_stratified_sampling_for_each_interval": True
    }

    snapshot_img = []
    for i in trange(num_lines):
        scene = mi.load_file(scene_filename) # load the scene xml file

        # Render heterodyne hu et al's method, offset btw [0, 2pi/T]
        line = run_scene(
            scene,
            'dopplertofpath',
            hetero_frequency = snapshot_freq[i], 
            hetero_offset=0,
            output_path=None,
            expname=None,
            **tof_configs
        )
        snapshot_img.append(line)

        iterate_shutter(scene_camera, line_exposure)
        iterate_crop(scene_camera, var_axis)

    output_filename = 'snapshot_{}MHz_{}us.npy'.format(modulation_freq, exposure_time)
    output_path = os.path.join(outputdir, output_filename)
    
    snapshot_img = np.squeeze(np.array(snapshot_img)) # get rid of extra 1 dimension
    
    # if varying along the x direction, the final snapshot needs to be transposed because dimensions get flipped
    if var_axis == 'x':
        snapshot_img = snapshot_img.T

    print('snapshot_img size:', snapshot_img.shape)
    print("Saving snapshot at ", output_path)
    np.save(output_path, snapshot_img)

    # reset all of the camera params and finish
    reset_shutter(scene_camera, exposure_time)
    reset_crop(scene_camera, var_axis)
    print("Experiments complete.")      

if __name__ == "__main__":
    main()