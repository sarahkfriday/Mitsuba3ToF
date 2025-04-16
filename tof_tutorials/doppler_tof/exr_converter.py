import cv2
import numpy as np
import os
import configargparse
from utils.image_utils import rgb2luminance

# os.system("export OPENCV_IO_ENABLE_OPENEXR=1") # make sure that this env variable is set

def convert_exr_npy(input_filepath, filename, T, output_filepath=None, tof=False):  
    print('Loading ', input_filepath+filename) 
    image = cv2.imread(input_filepath + filename,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    if tof:
        image = rgb2luminance(image) * T
    else:
        image = rgb2luminance(image)
    new_filename = filename.replace("exr", "npy")
    if output_filepath is None:
        output_filepath=input_filepath
    np.save(output_filepath + new_filename, image)

parser = configargparse.ArgumentParser()
parser.add_argument('--noatten', type=bool, default=True, help='using no geometric attenuation')
args = parser.parse_args()
noatten =args.noatten
if noatten:
    emit_mode = "noatten"
else:
    emit_mode = "atten"

# convert tof images from exr to numpy
phases = [0, 90, 180, 270]
freq_modes = ['homodyne', 'OFheterodyne', 'heterodyne']

result_filepath = "./result/moving_cubes/"
out_filepath = "/home/sarah/Documents/GitHub/Mitsuba3ToF/tof_tutorials/result/moving_cubes/point/noatten/individual/240MHz/"
# out_filepath = "C:\\Users\\f005cbs\\Dartmouth College Dropbox\\Sarah Friday\\Snapshot-Doppler\\snapshot-cp-doppler\\data\\moving_cubes\\point\\{}\\windows\\individual\\".format(emit_mode)
convert_exr_npy(result_filepath + "point/{}/individual/240MHz/".format(emit_mode), "moving_cubes_depth.exr", 0.0017, output_filepath=out_filepath)
convert_exr_npy(result_filepath + "point/{}/individual/240MHz/".format(emit_mode), "moving_cubes_radiance.exr", 0.0017, output_filepath=out_filepath)
convert_exr_npy(result_filepath + "point/{}/individual/240MHz/".format(emit_mode), "moving_cubes_velocity.exr", 0.0017, output_filepath=out_filepath)

for p in phases:
    convert_exr_npy(result_filepath + "point/{}/individual/240MHz/".format(emit_mode), "moving_cubes_homodyne_phase{}.exr".format(str(p)), 0.0017, output_filepath=out_filepath, tof=True)
    convert_exr_npy(result_filepath + "point/{}/individual/240MHz/".format(emit_mode), "moving_cubes_OFheterodyne_phase{}.exr".format(str(p)), 0.0017, output_filepath=out_filepath, tof=True)
    convert_exr_npy(result_filepath + "point/{}/individual/240MHz/".format(emit_mode), "moving_cubes_heterodyne_phase{}.exr".format(str(p)), 0.0017, output_filepath=out_filepath, tof=True)

