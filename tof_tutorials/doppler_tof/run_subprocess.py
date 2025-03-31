import subprocess
import shlex
from tqdm import trange

# scene_list = ["../scenes/moving_cubes/moving_cubes_radiance.xml", 
#               "../scenes/moving_cubes/moving_cubes_depth.xml", 
#               "../scenes/moving_cubes/moving_cubes_velocity.xml",
#               "../scenes/moving_cubes/moving_cubes_homodyne_phase0.xml",
#               "../scenes/moving_cubes/moving_cubes_homodyne_phase90.xml",
#               "../scenes/moving_cubes/moving_cubes_homodyne_phase180.xml",
#               "../scenes/moving_cubes/moving_cubes_homodyne_phase270.xml",
#               "../scenes/moving_cubes/moving_cubes_heide_phase0.xml",
#               "../scenes/moving_cubes/moving_cubes_heide_phase90.xml",
#               "../scenes/moving_cubes/moving_cubes_heide_phase180.xml",
#               "../scenes/moving_cubes/moving_cubes_heide_phase270.xml",
#               "../scenes/moving_cubes/moving_cubes_hu_phase0.xml",
#               "../scenes/moving_cubes/moving_cubes_hu_phase90.xml",
#               "../scenes/moving_cubes/moving_cubes_hu_phase180.xml",
#               "../scenes/moving_cubes/moving_cubes_hu_phase270.xml"]

# output_list = ["result/moving_cubes/radiance/moving_cubes_radiance.exr",
#                "result/moving_cubes/depth/moving_cubes_depth.exr",
#                "result/moving_cubes/velocity/moving_cubes_velocity.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_homodyne_phase0.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_homodyne_phase90.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_homodyne_phase180.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_homodyne_phase270.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_OFheterodyne_phase0.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_OFheterodyne_phase90.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_OFheterodyne_phase180.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_OFheterodyne_phase270.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_heterodyne_phase0.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_heterodyne_phase90.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_heterodyne_phase180.exr",
#                "result/moving_cubes/point/noatten/moving_cubes_heterodyne_phase270.exr"]
scene_list = ["../scenes/moving_cubes/moving_cubes_velocity.xml"]
output_list = ["result/moving_cubes/velocity/moving_cubes_velocity.exr"]
for i in trange(len(scene_list)):
    command = "mitsuba " + scene_list[i] + " -m \"llvm_ad_rgb\" -o " + output_list[i]
    command_list = shlex.split(command)
    subprocess.run(command_list)