import os
import numpy as np
from utils.image_utils import *
from tqdm import tqdm, trange
from program_runner import run_scene
import configargparse

import mitsuba as mi
mi.set_variant('llvm_ad_rgb')

def main():
    print(f'{"homodyne PID: ":<25}{os.getpid():>10}')

    parser = configargparse.ArgumentParser()
    parser.add_argument('--config', required=True, is_config_file=True, help='config file path')
    parser.add_argument("--scene_name", help="scene name")
    parser.add_argument("--scenedir", type=str, default="./", help="scene directory")
    parser.add_argument("--outputdir", type=str, default="./", help="output directory")
    parser.add_argument("--exp_time", type=float, default=0.008, help="integration time in sec")
    parser.add_argument("--mod_freq", type=float, default = 24.0, help="modulation frequency in MHz")
    parser.add_argument("--max_depth", type=int, default=2, help='max path depth')
    parser.add_argument("--spp", type=int, default=1024, help='samples per pixel per render pass')
    parser.add_argument("--num_passes", type=int, default=1, help="number of render passes")
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
    num_passes = args.num_passes
    scene_base_dir = os.path.join(scene_dir, "scenes", scene_name)

    # load the scene
    scene_filename = os.path.join(scene_base_dir, scene_name+".xml")
    
    # define heterodyne values to use during rendering
    hetero_offsets = [0.0, 0.25, 0.5, 0.75]  # phase offset [0,1] -> [0, 2pi]
    
    tof_configs = {
    "w_g": modulation_freq,
    "exposure_time": exposure_time,
    "max_depth": max_depth,
    "path_correlation_depth": 2,
    "time_sampling_method": "antithetic",
    "antithetic_shift": 0.5,
    "wave_function_type": wave_function_type,
    "low_frequency_component_only": True,
    "use_stratified_sampling_for_each_interval": True
    }
    
    scene = mi.load_file(scene_filename) # load the scene xml file
    
    for i in range(len(hetero_offsets)):
        phase = int(hetero_offsets[i]*360)
        homodyne_output_filename = "{}_homodyne_phase{}".format(scene_name, phase)
        
        homodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=0,
            hetero_offset=hetero_offsets[i],
            output_filename=homodyne_output_filename,
            output_path=outputdir, 
            total_spp = int(num_passes*spp),
            silent=True,
            **tof_configs
        )

    print("Done rendering homodyne")

if __name__ == "__main__":
    main()