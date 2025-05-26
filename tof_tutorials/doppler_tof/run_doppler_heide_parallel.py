"""
Heavily modified from https://github.com/juhyeonkim95/Mitsuba3DopplerToF/blob/main/doppler_tutorials/src/main_animation.py
"""
import os
current_directory = os.getcwd()
print("current director: ", current_directory)
import subprocess
import shlex

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
    parser.add_argument('--config', required=True, is_config_file=True, help='config file path')
    parser.add_argument("--scene_name", help="scene name")
    parser.add_argument("--scenedir", type=str, default="./", help="scene directory")
    parser.add_argument("--outputdir", type=str, default="./", help="output directory")
    parser.add_argument("--exp_time", type=float, default=0.008, help="integration time in sec")
    parser.add_argument("--mod_freq", type=float, default = 24.0, help="modulation frequency in MHz")
    parser.add_argument("--max_depth", type=int, default=2, help='max path depth')
    parser.add_argument("--num_passes", type=int, default=1, help="number of render passes")
    parser.add_argument("--spp", type=int, default=1024, help='samples per pixel per render pass')
    parser.add_argument("--wave_function_type", type=str, default="sinusoidal", help="waveform")

    args = parser.parse_args()
    scene_name = args.scene_name
    scene_dir = args.scenedir
    outputdir = args.outputdir
    exposure_time = args.exp_time
    modulation_freq = args.mod_freq
    max_depth = args.max_depth
    wave_function_type = args.wave_function_type
    spp = args.spp
    scene_base_dir = os.path.join(scene_dir, "scenes", scene_name)

    # load the scene
    scene_filename = os.path.join(scene_base_dir, scene_name+".xml")
    scene_camera = os.path.join(scene_base_dir, scene_name+"_camera.xml")

    # change the shutter close time to match exposure time
    change_shutter_close(scene_camera, exposure_time)

    scene = mi.load_file(scene_filename) # load the scene xml file
    
    # Render GT radiance
    run_scene(
        scene, 
        'radiance',
        max_depth=max_depth,
        total_spp=spp,
        output_filename="{}_radiance".format(scene_name),
        output_path=outputdir,
        silent=True
        )
    print("Done rendering radiance")
    print("=================================")

    # Render GT radial velocity
    run_scene(
        scene, 
        'velocity',
        capture_time = exposure_time,
        total_spp=spp,
        output_filename="{}_velocity".format(scene_name),
        output_path=outputdir,
        silent=True
    )
    print("Done rendering velocity")
    print("=================================")

    # Render GT depth
    run_scene(
        scene, 
        'depth',
        total_spp=spp,
        output_filename="{}_depth".format(scene_name),
        output_path=outputdir,
        silent=True
        )
    print("Done rendering depth")
    print("=================================")    

    # do ToF rendering in parallel
    command_homodyne = shlex.split("python doppler_tof/homodyne_measurements_parallel.py --config doppler_tof/render_configs.txt")
    command_OFheterodyne = shlex.split("python doppler_tof/OFheterodyne_measurements_parallel.py --config doppler_tof/render_configs.txt")
    command_heterodyne =shlex.split( "python doppler_tof/heterodyne_measurements_parallel.py --config doppler_tof/render_configs.txt")

    hom = subprocess.Popen(command_homodyne)
    OFhet = subprocess.Popen(command_OFheterodyne)
    het = subprocess.Popen(command_heterodyne)

    hom.wait()
    OFhet.wait()
    het.wait()

    print("Experiments complete.")      

if __name__ == "__main__":
    main()