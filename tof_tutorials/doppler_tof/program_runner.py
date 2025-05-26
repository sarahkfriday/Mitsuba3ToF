"""
Taken from https://github.com/juhyeonkim95/Mitsuba3DopplerToF/blob/main/doppler_tutorials/src/program_runner.py
"""

import os
import numpy as np
from utils.image_utils import *
from tqdm import tqdm, trange

import mitsuba as mi
mi.set_variant('llvm_ad_rgb')

def render_image_multi_pass(scene, integrator, single_pass_spp, total_pass, show_progress=False, silent=False):
    if not silent:
        print("Rendering {} passes".format(total_pass))
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

def get_integrator(type, **kwargs):
    if type == 'radiance':
        integrator_dict = {
        'type': 'path',
        'max_depth': kwargs.get('max_depth')
        }
    elif type == 'depth':
        integrator_dict = {
        'type': 'depth'
        }
    elif type == 'velocity':
        integrator_dict = {
        'type': 'velocity',
        'time': kwargs.get("capture_time", 0.0017)
        }
    elif type == 'dopplertofpath':
        integrator_dict = {
            'type': 'dopplertofpath',
            'is_doppler_integrator': True,
            'max_depth': kwargs.get('max_depth'), 
            'w_g': kwargs.get('w_g'),
            'time': kwargs.get('exposure_time'),
            'hetero_offset': kwargs.get('hetero_offset'),
            'antithetic_shift': kwargs.get('antithetic_shift'),
            'time_sampling_method': kwargs.get('time_sampling_method'),
            'path_correlation_depth': kwargs.get('max_depth'),
            'low_frequency_component_only': kwargs.get('low_frequency_component_only'),
            'wave_function_type': kwargs.get('wave_function_type'),
            'use_stratified_sampling_for_each_interval': kwargs.get('use_stratified_sampling_for_each_interval')
        }
        if kwargs.get('w_s') is not None:
            integrator_dict['w_s'] = kwargs.get('w_s')
        else:
            integrator_dict['hetero_frequency'] = kwargs.get('hetero_frequency')
            # if kwargs.get('hetero_frequency') == 0.5:
            #     integrator_dict['path_correlation_depth'] = 1
            #     print('path corr depth: ', integrator_dict['path_correlation_depth'])

    else:
        raise ValueError("Invalid integrator type. Options are radiance, depth, velocity, or dopplertofpath")
    return integrator_dict

def run_scene(scene, integrator, silent=False, **kwargs):
    # kwargs parsing
    total_spp = kwargs.get("total_spp", 1024)
    single_spp = kwargs.get("single_spp", 1024)
    output_path = kwargs.get("output_path")
    output_filename = kwargs.get("output_filename")
    show_progress = kwargs.get("show_progress", False)

    # define the integrator
    config_dict = get_integrator(integrator, **kwargs)
    # print(config_dict)
    integrator_radiance = mi.load_dict(config_dict)
    single_pass_spp = min(single_spp, total_spp)
    
    # render
    if integrator == 'dopplertofpath':
        img = render_image_multi_pass(scene, integrator_radiance, single_pass_spp, total_spp // single_pass_spp, show_progress=show_progress, silent=silent)
    else:
        img = render_image_multi_pass(scene, integrator_radiance, single_pass_spp, 1, show_progress=show_progress, silent=silent)

    img = rgb2luminance(img) # convert to grayscale

    # if its a doppler tof image, multiply by T
    if integrator == 'dopplertofpath':
        img *= kwargs.get('exposure_time')

    # either save out to file or return
    if output_filename is not None and output_path is not None:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        numpy_output_filename = os.path.join(output_path, "%s.npy" % output_filename)
        if not silent:
            print("Saving result as ", numpy_output_filename)
        np.save(numpy_output_filename, img)
    else:
        # print("Returning instead")
        return img 

def homodyne_wrapper(scene_name, scene_filename, hetero_offsets, common_configs):
    homodyne_quadratures(scene_name, scene_filename, hetero_offsets, **common_configs)

def OFheterodyne_wrapper(scene_name, scene_filename, hetero_offsets, common_configs):
    OFheterodyne_quadratures(scene_name, scene_filename, hetero_offsets, **common_configs)

def heterodyne_wrapper(scene_name, scene_filename, hetero_offsets, common_configs):
    heterodyne_quadratures(scene_name, scene_filename, hetero_offsets, **common_configs)

def homodyne_quadratures(scene_name, scene_filename, hetero_offsets, **kwargs):
    print("Starting homodyne")
    mi.set_variant('llvm_ad_rgb')
    print("homodyne: set variant")
    scene = mi.load_file(scene_filename) # load the scene xml file
    print("homodyne: loaded scene file")
    
    for i in range(len(hetero_offsets)):
        phase = int(hetero_offsets[i]*360)
        homodyne_output_filename = "{}_homodyne_phase{}".format(scene_name, phase)
        
        homodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=0,
            hetero_offset=hetero_offsets[i],
            output_filename=homodyne_output_filename,
            output_path=kwargs.get('outputdir'), 
            total_spp = kwargs.get('spp'),
            **kwargs
        )
    print("Done rendering homodyne")

def OFheterodyne_quadratures(scene_name, scene_filename, hetero_offsets, **kwargs):
    print("Starting OFheterodyne")
    mi.set_variant('llvm_ad_rgb')
    print("OFheterodyne: set variant")
    scene = mi.load_file(scene_filename) # load the scene xml file
    print("OFheterodyne: loaded scene file")

    for i in range(len(hetero_offsets)):
        phase = int(hetero_offsets[i]*360)
        OFheterodyne_output_filename = "{}_OFheterodyne_phase{}".format(scene_name, phase)
        
        OFheterodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=1.0,
            hetero_offset=hetero_offsets[i],
            output_filename=OFheterodyne_output_filename,
            output_path=kwargs.get('outputdir'), 
            total_spp = kwargs.get('spp'),
            **kwargs
        )
    print("Done rendering OFheterodyne")


def heterodyne_quadratures(scene_name, scene_filename, hetero_offsets, freq_offsets, **kwargs):
    print("Starting heterodyne")
    mi.set_variant('llvm_ad_rgb')
    print("heterodyne: set variant")
    scene = mi.load_file(scene_filename) # load the scene xml file
    print("heterodyne: loaded scene file")

    single_spp = int(kwargs.get('spp')*10)

    for i in range(len(hetero_offsets)):
        phase = int(hetero_offsets[i]*360)
        heterodyne_output_filename = "{}_heterodyne_phase{}".format(scene_name, phase)
        
        heterodyne_image = run_scene(
            scene, 
            'dopplertofpath',
            hetero_frequency=freq_offsets[i],
            hetero_offset=hetero_offsets[i],
            output_filename=heterodyne_output_filename,
            output_path=kwargs.get('outputdir'), 
            total_spp = int(single_spp*10),
            single_spp = single_spp,
            **kwargs
        )
    print("Done rendering heterodyne")
