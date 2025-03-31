import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
from utils.image_utils import rgb2luminance

# os.system("export OPENCV_IO_ENABLE_OPENEXR=1") # make sure that this env variable is set

def convert_exr_npy(filepath, filename, T, tof=False):  
    print('Loading ', filepath+filename) 
    image = cv2.imread(filepath + filename,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    if tof:
        image = rgb2luminance(image) * T
    else:
        image = rgb2luminance(image)
    new_filename = filename.replace("exr", "npy")
    np.save(filepath + new_filename, image)

# convert tof images from exr to numpy
phases = [0, 90, 180, 270]
freq_modes = ['homodyne', 'OFheterodyne', 'heterodyne']

result_filepath = "./result/moving_cubes/"
convert_exr_npy(result_filepath + "depth/", "moving_cubes_depth.exr", 0.0017)
convert_exr_npy(result_filepath + "radiance/", "moving_cubes_radiance.exr", 0.0017)
convert_exr_npy(result_filepath + "velocity/", "moving_cubes_velocity.exr", 0.0017)

for p in phases:
    convert_exr_npy(result_filepath + "point/noatten/", "moving_cubes_homodyne_phase{}.exr".format(str(p)), 0.0017, tof=True)
    convert_exr_npy(result_filepath + "point/noatten/", "moving_cubes_OFheterodyne_phase{}.exr".format(str(p)), 0.0017, tof=True)
    convert_exr_npy(result_filepath + "point/noatten/", "moving_cubes_heterodyne_phase{}.exr".format(str(p)), 0.0017, tof=True)

