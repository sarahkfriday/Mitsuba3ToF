import sys
sys.path.append('../')

import mitsuba as mi
# import os
# print('DrJit path: ', os.environ['DRJIT_LIBLLVM_PATH'])

import drjit as dr
import numpy as np
variant = "llvm_ad_rgb"
mi.set_variant(variant)
from tqdm import tqdm, trange
import matplotlib.pyplot as plt
import cv2
from utils.image_utils import *
import xml.etree.ElementTree as ET
from scipy.constants import c, pi

def run_scene(
    scene_name="back-plane",
    spp=4096,
    repeat = 1
):
    scene_file = "../../scenes/%s/scene_doppler_snapshot.xml" % (scene_name)

    # xml tree parsing
    xml_tree = ET.parse(scene_file)
    root = xml_tree.getroot()
    height = int(root[1].get('value'))
    width = int(root[2].get('value'))
    shutter_open = float(root[5][4].get('value'))
    shutter_close = float(root[5][5].get('value'))
    int_time = shutter_close - shutter_open
    crop_offset = root[5][3][4]

    all_frames = []
    final_composite = np.empty((height, width))

    for y in tqdm(range(height)):
        w_g = float(root[4][1].get('value'))
        w_s = root[4][2]
        k = ((pi/int_time) / (2.0*pi) * 1e-6)*y # freq offset at each line in MHz
        w_s.set('value', str(w_g + k))
        crop_offset.set('value', str(y))
        
        print('\nk = ', k)
        print('crop offset = ', y)
        print('(height, width) = ', height, width)
        print('integration time (sec): ', int_time)

        xml_tree.write(scene_file)
        
        scene = mi.load_file(scene_file)

        image = None
        image_i = mi.render(scene, spp=spp, seed=y)    
        image_i = np.asarray(image_i)
        if image is None:
            image = image_i
        else:
            image += image_i
        image *= int_time # exposure time
        image_lum = rgb2luminance(image)
        # all_frames.append(image_lum)
        final_composite[y,:] = image_lum
        # output_folder = "../result/doppler/%s" % (scene_name)
        # save_tof_image(image, output_folder, "doppler.png", vmin=-1e-6, vmax=1e-6)

    output_folder = "../result/doppler/%s" % (scene_name)
    np.save(output_folder + '_composite_100MHz_500us_262144spp_maxdepth2.npy', np.array(final_composite))
    # np.save(output_folder + 'final_composite.npy', final_composite)

if __name__ == "__main__":

    run_scene(
        scene_name="back-plane"
    )

