"""
Taken from https://github.com/juhyeonkim95/Mitsuba3DopplerToF/blob/main/doppler_tutorials/src/utils/common_configs.py

, "spinner-hu" : {
            "max_depth": 4,
            "total_spp": 1024 * 4,
            "animation_length": 150,
            "intervals": 1,
            "w_g": 24
        }


        sensor_config_dict = {
            "type": "perspective",
            "shutter_open": sh_open,
            "shutter_close": sh_close,
            "fov_axis": "x",
            "fov": 28.072487,
            "to_world": mi.ScalarTransform4F.look_at(origin=[0, 2.730000, -8.0000], target=[1, 1, 1], up=[0, 0, 1]),
            "sampler": {
                "type": "correlated",
                "sample_count": scene_config.get("total_spp")
            },
            "film": {
                "type": "hdrfilm",
                "width": scene_config.get("resx"),
                "height": scene_config.get("resy")
            }
        }
"""

def get_animation_scene_configs():
    scene_configs = {
        "spinner" : {
            "max_depth": 2,
            "total_spp": 1024,
            "intervals": 1,
            "exposure_time": 0.002,
            "resx": 320,
            "resy": 240
        },
        "moving_cubes" : {
            "max_depth": 2,
            "total_spp": 1024,
            "intervals": 1,
            "exposure_time": 0.0017,
            "resx": 320,
            "resy": 240
        },
        "cornell-box-2":{
            "max_depth": 4,
            "total_spp": 1024,
            "intervals": 1,
            "exposure_time": 0.0015,
            "resx": 320,
            "resy": 240
        }
    }

    return scene_configs
