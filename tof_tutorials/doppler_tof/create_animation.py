"""
Heavily modified from https://github.com/juhyeonkim95/Mitsuba3DopplerToF/blob/main/doppler_tutorials/src/main_animation.py
"""
import os
current_directory = os.getcwd()
print("current director: ", current_directory)

from program_runner import *

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm, trange
from pprint import pprint
from scipy.constants import c, pi
import xml.etree.ElementTree as ET

from utils.image_utils import *
import configargparse
import gc
from utils.common_configs import *


def main():
    parser = configargparse.ArgumentParser()
    parser.add_argument('--config', is_config_file=True, help='config file path')
    parser.add_argument("--scene_name", help="your name")
    parser.add_argument("--num_frames", type=int, default=1, help="number of frames to render")
    parser.add_argument("--basedir", type=str, default="./", help="base directory")
    parser.add_argument("--exp_time", type=float, default=0.0008, help="integration time in sec")

    args = parser.parse_args()
    scene_name = args.scene_name
    num_frames = args.num_frames
    exposure_time = args.exp_time

    # get scene_config
    scene_configs = get_animation_scene_configs()
    if not scene_name in scene_configs:
        print("scene name not found")
        return
    scene_config = scene_configs[scene_name]

    scene_base_dir = os.path.join(args.basedir, "scenes", scene_name)
    
    # render 
    scene_filename = os.path.join(scene_base_dir, scene_name+"_animation.xml")
    
    exit_if_file_exists = False

    output_base_dir =  "result"

    xml_tree = ET.parse(scene_filename)
    root = xml_tree.getroot()
    shutter_open = root[5][0]
    shutter_close = root[5][1]

    for n in trange(num_frames):
        sh_open = exposure_time * n
        sh_close = exposure_time * (n+1)

        shutter_open.set("value", str(sh_open))
        shutter_close.set("value", str(sh_close))
        
        xml_tree.write(scene_filename)

        scene = mi.load_file(scene_filename) # load the scene xml file
        # Render scene radiance (standard rendering)
        run_scene_radiance(
            scene, 
            scene_name,
            base_dir=output_base_dir,
            output_file_name="{}_radiance_frame{}".format(scene_name, n),
            exit_if_file_exists=exit_if_file_exists,
        )

    # print("Done")

                        
if __name__ == "__main__":
    main()