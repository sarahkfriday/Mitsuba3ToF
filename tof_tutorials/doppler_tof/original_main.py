import sys
sys.path.append('../')
import os

# make sure to source the right path, and set drjit llvm path var
# os.system("source ./../../build/setpath.sh")
# os.system("export DRJIT_LIBLLVM_PATH=/Users/sarahfriday/anaconda3/pkgs/libllvm12-12.0.0-h12f7ac0_4/lib/libLLVM-12.dylib")

print('DrJit path: ', os.environ['DRJIT_LIBLLVM_PATH'])

import numpy as np
from tqdm import tqdm, trange
import matplotlib.pyplot as plt
import cv2
from utils.image_utils import *

import mitsuba as mi
variant = "llvm_ad_rgb"
mi.set_variant(variant)

def run_scene(
    scene_name="cornell-box-2",
    spp=1024,
    repeat = 1
):
    scene = mi.load_file("../scenes/%s/%s.xml" % (scene_name, scene_name))
    image = None
    for i in trange(repeat):
        image_i = mi.render(scene, spp=spp, seed=i)    
        image_i = np.asarray(image_i)
        if image is None:
            image = image_i
        else:
            image += image_i
    image /= repeat
    exposure_time = 0.0015
    image *= exposure_time # exposure time
    
    output_folder = "result/%s" % (scene_name)
    filename = 'cornell-box-2-homodyne'
    np.save(output_folder + '/' + filename + '.npy', rgb2luminance(image))

if __name__ == "__main__":
    run_scene(
        scene_name="cornell-box-2"
    )