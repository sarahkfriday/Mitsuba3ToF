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

def main():
    parser = configargparse.ArgumentParser()
    parser.add_argument('--config', is_config_file=True, help='config file path')
    parser.add_argument("--scene_name", help="your name")
    parser.add_argument("--wave_function_type", type=str, default="sinusoidal", help="waveform")
    parser.add_argument("--scenedir", type=str, default="./", help="scene directory")
    parser.add_argument("--outputdir", type=str, default="./", help="output directory")
    parser.add_argument("--exp_time", type=float, default=0.008, help="integration time in sec")
    parser.add_argument("--mod_freq", type=float, default = 24.0, help="modulation frequency in MHz")
    parser.add_argument("--corr_depth", type=int, default=2, help="path correlation depth")

    args = parser.parse_args()
    scene_name = args.scene_name
    wave_function_type = args.wave_function_type
    exposure_time = args.exp_time
    modulation_freq = args.mod_freq
    correlation_depth = args.corr_depth
    outputdir = args.outputdir

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
    scene_base_dir = os.path.join(args.scenedir, "scenes", scene_name)

    hetero_offsets = [0.0, 0.25, 0.5, 0.75]  # phase offset [0,1] -> [0, 2pi]
    hetero_offsets_hu = [0.75, 0.0, 0.25, 0.5]
    hetero_freqs_hu = [0.5, 0.5, -0.5, -0.5] # pos, pos, neg, neg

    # load the scene
    scene_filename = os.path.join(scene_base_dir, scene_name+".xml")
    # change the shutter close time to match exposure time
    # change_shutter_close(scene_filename, exposure_time)
    scene = mi.load_file(scene_filename) # load the scene xml file
    
    exit_if_file_exists = False

    # Render GT radiance
    run_scene_radiance(
        scene, 
        scene_name,
        output_file_name="{}_radiance".format(scene_name),
        output_path=outputdir,
        exit_if_file_exists=exit_if_file_exists
    )
    print("Done rendering radiance")
    print("=================================")

    # Render GT radial velocity
    run_scene_velocity(
        scene, 
        scene_name,
        output_file_name="{}_velocity".format(scene_name),
        output_path=outputdir,
        exit_if_file_exists=exit_if_file_exists,
        **scene_config
    )
    print("Done rendering velocity")
    print("=================================")

    # Render scene depth
    run_scene_depth(
        scene, 
        scene_name,
        output_file_name="{}_depth".format(scene_name),
        output_path=outputdir, 
        exit_if_file_exists=exit_if_file_exists
    )
    print("Done rendering depth")
    print("=================================")    

    common_configs = {
        "time_sampling_method": "antithetic",
        "scene_name": scene_name,
        "wave_function_type": wave_function_type,
        "low_frequency_component_only": True,
        "scene": scene,
        "w_g": modulation_freq,
        "exposure_time": exposure_time,
        "max_depth": scene_config.get("max_depth"),
        "exit_if_file_exists": exit_if_file_exists,
        "show_progress": False
    }

    print("Rendering ToF...")
    print(f"{'Modulation Frequency (MHz):':<30}{modulation_freq}")
    print(f"{'Exposure Time (s):':<30}{exposure_time}")
    print(f"{'Phase shifts (deg):':<30}{np.array(hetero_offsets)*360}")
    print(f"{'Phase shifts Hu (deg):':<30}{np.array(hetero_offsets_hu)*360}")
    
    for i in trange(len(hetero_offsets)):
        phase = int(hetero_offsets[i]*360)
        homodyne_output_file_name = "{}_homodyne_phase{}".format(scene_name, phase)
        OF_heterodyne_output_file_name = "{}_OFheterodyne_phase{}".format(scene_name, phase)
        heterodyne_output_file_name = "{}_heterodyne_phase{}".format(scene_name, phase)

        # (1) Render homodyne (no variation is used for homodyne)
        homodyne_image = run_scene_doppler_tof(
            hetero_offset=hetero_offsets[i],
            hetero_frequency=0.0,
            output_path=outputdir,
            expname=homodyne_output_file_name,
            **common_configs
        )

        # (2) Render heterodyne heide et al's method, pure OF        
        OFheterodyne_image = run_scene_doppler_tof(
            hetero_frequency=1.0,  
            hetero_offset=hetero_offsets[i],
            output_path=outputdir,
            expname=OF_heterodyne_output_file_name,
            **common_configs
        )

        # (3) Render heterodyne hu et al's method, offset btw [0, 2pi/T]
        heterodyne_image = run_scene_doppler_tof(
            hetero_frequency = hetero_freqs_hu[i], 
            hetero_offset=hetero_offsets_hu[i],
            output_path=outputdir,
            expname=heterodyne_output_file_name,
            **common_configs
        )
    
    print("Experiments complete.")      

if __name__ == "__main__":
    main()