import numpy as np
from tqdm import tqdm, trange
from utils.image_utils import *

import mitsuba as mi
mi.set_variant('llvm_ad_rgb')

c=3.0e8
pi = np.pi

def main():
    T = 0.0017
    result_subdir = '/point/noatten/'
    scene_name = 'moving_cubes'
    scene_base_dir = "/Users/sarahfriday/Documents/Mitsuba3ToF/scenes/{}".format(scene_name)
    result_base_dir = '/Users/sarahfriday/Documents/Mitsuba3ToF/tof_tutorials/result'

    scene_names = ['_depth', '_radiance', '_velocity',
                   '_homodyne_phase0', '_homodyne_phase90', '_homodyne_phase180', '_homodyne_phase270',
                   '_heide_phase0', '_heide_phase90', '_heide_phase180', '_heide_phase270',
                   '_hu_phase0', '_hu_phase90', '_hu_phase180', '_hu_phase270']
    
    result_names = ['_depth', '_radiance', '_velocity',
                   '_homodyne_phase0', '_homodyne_phase90', '_homodyne_phase180', '_homodyne_phase270',
                   '_OFheterodyne_phase0', '_OFheterodyne_phase90', '_OFheterodyne_phase180', '_OFheterodyne_phase270',
                   '_heterodyne_phase0', '_heterodyne_phase90', '_heterodyne_phase180', '_heterodyne_phase270']

    for i in trange(len(scene_names)):
        scene_filename = os.path.join(scene_base_dir, scene_name + scene_names[i] + ".xml")

        scene = mi.load_file(scene_filename) # load the scene xml file
        image = mi.render(scene, seed=0, spp=1024) # render
        if result_names[i]== '_depth' or result_names[i]=='_radiance' or result_names[i]=='_velocity':
            image = rgb2luminance(image)
            result_filename = os.path.join(result_base_dir, scene_name + '/' + result_names[i].replace('_', '') + '/' + scene_name +result_names[i]+ ".npy")
        else:
            image = rgb2luminance(image) * T
            result_filename = os.path.join(result_base_dir, scene_name + result_subdir + scene_name + result_names[i]+ ".npy")
        # print(result_filename)
        np.save(result_filename, image)

if __name__ == "__main__":
    main()