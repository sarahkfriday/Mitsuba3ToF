"""
Taken from https://github.com/juhyeonkim95/Mitsuba3DopplerToF/blob/main/doppler_tutorials/src/program_runner.py
"""

import mitsuba as mi
mi.set_variant('llvm_ad_rgb')
import os
import numpy as np
from utils.image_utils import *
from tqdm import tqdm, trange

def render_image_multi_pass(scene, integrator, single_pass_spp, total_pass, show_progress=False):
    img_sum = None
    if show_progress:
        for i in trange(total_pass):
            img_i = integrator.render(scene, seed=i, spp=single_pass_spp)
            if i == 0:
                img_sum = img_i
            else:
                img_sum += img_i
    else:
        img_i_old = 0
        for i in range(total_pass):
            img_i = integrator.render(scene, seed=i, spp=single_pass_spp)
            if i == 0:
                img_sum = img_i
            else:
                img_sum += img_i
            img_i_old = img_i

    img = img_sum / total_pass
    return img

def run_scene_velocity(scene, scene_name, **kwargs):
    velocity_rendering_config_dict = {
        'type': 'velocity',
        'time': kwargs.get("exposure_time", 0.0017)
    }
    total_spp = kwargs.get("total_spp", 1024)

    output_path = kwargs.get("output_path")
    # output_path = os.path.join(kwargs.get("base_dir"), scene_name, "velocity")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_file_name = kwargs.get("output_file_name")
    numpy_output_file_name = os.path.join(output_path, "%s.npy" % output_file_name)

    if os.path.exists(numpy_output_file_name) and kwargs.get("exit_if_file_exists", False):
       print("File already exists!")
       return

    integrator_velocity = mi.load_dict(velocity_rendering_config_dict)
    single_pass_spp = min(1024, total_spp)
    show_progress = kwargs.get("show_progress", False)
    img_velocity = render_image_multi_pass(scene, integrator_velocity, single_pass_spp, total_spp // single_pass_spp, show_progress=show_progress)
    
    img_velocity = rgb2luminance(img_velocity)
    print("Saving result as ", numpy_output_file_name)
    np.save(numpy_output_file_name, img_velocity)
    
def run_scene_depth(scene, scene_name, **kwargs):
    config_dict = {
        'type': 'depth'    }
    total_spp = kwargs.get("total_spp", 1024)

    output_path = kwargs.get("output_path")
    # output_path = os.path.join(kwargs.get("base_dir"), scene_name, "depth")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_file_name = kwargs.get("output_file_name")
    numpy_output_file_name = os.path.join(output_path, "%s.npy" % output_file_name)

    if os.path.exists(numpy_output_file_name) and kwargs.get("exit_if_file_exists", False):
       print("File already exists!")
       return

    integrator_depth = mi.load_dict(config_dict)
    single_pass_spp = min(1024, total_spp)
    
    show_progress = kwargs.get("show_progress", False)
    img = render_image_multi_pass(scene, integrator_depth, single_pass_spp, total_spp // single_pass_spp, show_progress=show_progress)
    
    img = rgb2luminance(img)
    print("Saving result as ", numpy_output_file_name)
    np.save(numpy_output_file_name, img)


def run_scene_radiance(scene, scene_name, **kwargs):
    config_dict = {
        'type': 'path',
        'max_depth': kwargs.get("max_depth", 2), 
    }
    total_spp = kwargs.get("total_spp", 1024)

    output_path = kwargs.get("output_path")
    # output_path = os.path.join(kwargs.get("base_dir"), scene_name, "radiance")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_file_name = kwargs.get("output_file_name")
    numpy_output_file_name = os.path.join(output_path, "%s.npy" % output_file_name)

    if os.path.exists(numpy_output_file_name) and kwargs.get("exit_if_file_exists", False):
       print("File already exists!")
       return

    integrator_radiance = mi.load_dict(config_dict)
    single_pass_spp = min(1024, total_spp)
    
    show_progress = kwargs.get("show_progress", False)
    img = render_image_multi_pass(scene, integrator_radiance, single_pass_spp, total_spp // single_pass_spp, show_progress=show_progress)
    
    img = rgb2luminance(img)
    print("Saving result as ", numpy_output_file_name)
    np.save(numpy_output_file_name, img)

def run_scene_doppler_tof(
    scene_name="cornell-box",
    wave_function_type="sinusoidal",
    low_frequency_component_only=True,
    hetero_frequency=1.0, hetero_offset=0.0,
    time_sampling_method="antithetic",
    antithetic_shift=None, 
    path_correlation_depth=2,
    exposure_time=0.0017,
    w_g=240,
    w_s=24, 
    max_depth=2,
    use_stratified_sampling_for_each_interval=True,
    exit_if_file_exists=False,
    expname=None,
    scene=None,
    scene_xml=None,
    total_spp=1024,
    output_path=None,
    **kwargs
):

    output_file = os.path.join(output_path, "%s.npy" % expname)

    # check file already exists
    if os.path.exists(output_file) and exit_if_file_exists:
        print("File already exists: returning existing file")
        return np.load(output_file)
    else:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
    
    if antithetic_shift is None:
        if time_sampling_method == "antithetic":
            antithetic_shift = 0.5
        else:
            antithetic_shift = 0.0

    if scene is None:
        scene = mi.load_file(scene_xml)

    # define integrator
    if hetero_frequency is not None:
        integrator_config_dict = {
            'type': 'dopplertofpath',
            'is_doppler_integrator': True,
            'max_depth': max_depth, 
            'w_g': w_g,
            'time': exposure_time,
            'hetero_frequency': hetero_frequency,
            'hetero_offset': hetero_offset,
            'antithetic_shift': antithetic_shift,
            'time_sampling_method': time_sampling_method,
            'path_correlation_depth': max_depth,
            'low_frequency_component_only': low_frequency_component_only,
            'wave_function_type': wave_function_type,
            'use_stratified_sampling_for_each_interval': use_stratified_sampling_for_each_interval
        }
    else:
        # print("Using w_s = {} instead".format(w_s))
        integrator_config_dict = {
            'type': 'dopplertofpath',
            'is_doppler_integrator': True,
            'max_depth': max_depth, 
            'w_g': w_g,
            'w_s': w_s,
            'time': exposure_time,
            'hetero_offset': hetero_offset,
            'antithetic_shift': antithetic_shift,
            'time_sampling_method': time_sampling_method,
            'path_correlation_depth': max_depth,
            'low_frequency_component_only': low_frequency_component_only,
            'wave_function_type': wave_function_type,
            'use_stratified_sampling_for_each_interval': use_stratified_sampling_for_each_interval
        }

    integrator_doppler = mi.load_dict(integrator_config_dict)
    print('integrator dict: ', integrator_config_dict)
    # render pass
    single_pass_spp = min(1024, total_spp)
    show_progress = kwargs.get("show_progress", False)
    img_dop = render_image_multi_pass(scene, integrator_doppler, single_pass_spp, total_spp // single_pass_spp, show_progress=show_progress)
    
    img_dop = to_tof_image(img_dop, exposure_time)
    print("Saving result as ", output_file)
    np.save(output_file, img_dop)

    return img_dop