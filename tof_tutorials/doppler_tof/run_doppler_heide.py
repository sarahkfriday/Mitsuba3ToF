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
    parser.add_argument("--scene_name", help="your name")
    parser.add_argument("--scenedir", type=str, default="./", help="scene directory")
    parser.add_argument("--outputdir", type=str, default="./", help="output directory")
    parser.add_argument("--exp_time", type=float, default=0.008, help="integration time in sec")
    parser.add_argument("--mod_freq", type=float, default = 24.0, help="modulation frequency in MHz")
    parser.add_argument("--max_depth", type=int, default=2, help='max path depth')
    parser.add_argument("--spp", type=int, default=1024, help='samples per pixel')
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
    print("scene_filename: ", scene_filename)
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
        )
    print("Done rendering depth")
    print("=================================")    

    # define some common tof rendering configs
    tof_configs = {
        "w_g": modulation_freq,
        "exposure_time": exposure_time,
        "max_depth": max_depth,
        "path_correlation_depth": 2,
        "time_sampling_method": "antithetic",
        "antithetic_shift": 0.5,
        "total_spp": spp,
        "wave_function_type": wave_function_type,
        "low_frequency_component_only": True,
        "use_stratified_sampling_for_each_interval": True
    }

    # define heterodyne values to use during rendering
    hetero_offsets = [0.0, 0.25, 0.5, 0.75]  # phase offset [0,1] -> [0, 2pi]
    hetero_offsets_hu = [0.75, 0.0, 0.25, 0.5]
    hetero_freqs_hu = [0.5, 0.5, -0.5, -0.5] # pos, pos, neg, neg

    print("Rendering ToF...")
    print(f"{'Modulation Frequency (MHz):':<30}{modulation_freq}")
    print(f"{'Exposure Time (s):':<30}{exposure_time}")
    print(f"{'Phase shifts (deg):':<30}{np.array(hetero_offsets)*360}")
    print(f"{'Phase shifts Hu (deg):':<30}{np.array(hetero_offsets_hu)*360}")
    
    for i in trange(len(hetero_offsets)):
        phase = int(hetero_offsets[i]*360)
        homodyne_output_filename = "{}_homodyne_phase{}".format(scene_name, phase)
        OFheterodyne_output_filename = "{}_OFheterodyne_phase{}".format(scene_name, phase)
        heterodyne_output_filename = "{}_heterodyne_phase{}".format(scene_name, phase)

        # (1) Render homodyne (no variation is used for homodyne)
        homodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=0,
            hetero_offset=hetero_offsets[i],
            output_filename=homodyne_output_filename,
            output_path=outputdir, 
            **tof_configs
        )

        # (2) Render heterodyne heide et al's method, pure OF        
        OFheterodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=1.0,
            hetero_offset=hetero_offsets[i],
            output_filename=OFheterodyne_output_filename,
            output_path=outputdir, 
            **tof_configs
        )

        # (3) Render heterodyne hu et al's method, offset btw [0, 2pi/T]
        heterodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=hetero_freqs_hu[i],
            hetero_offset=hetero_offsets_hu[i],
            output_filename=heterodyne_output_filename,
            output_path=outputdir, 
            **tof_configs
        )

    print("Experiments complete.")      

if __name__ == "__main__":
    main()