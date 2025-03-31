import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

os.system("export OPENCV_IO_ENABLE_OPENEXR=1") # make sure that this env variable is set
   
image = cv2.imread("/Users/sarahfriday/Documents/Mitsuba3ToF/scenes/cornell-box-2/cornell-box-2.exr",  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
image = image * 0.0015
plt.imshow(image[:, :, 0], vmin=-1e-6, vmax=1e-6)
plt.show()

result_path = '/Users/sarahfriday/Documents/Mitsuba3ToF/tof_tutorials/result/cornell-box-2/'
np.save(result_path + "cornell-box-2-homodyne.npy", image)