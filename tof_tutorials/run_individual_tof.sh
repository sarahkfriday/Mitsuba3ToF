#!/bin/bash

mitsuba ../scenes/moving_cubes/moving_cubes_radiance.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_radiance.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_depth.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_depth.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_velocity.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_velocity.exr"

mitsuba ../scenes/moving_cubes/moving_cubes_homodyne_phase0.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_homodyne_phase0.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_homodyne_phase90.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_homodyne_phase90.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_homodyne_phase180.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_homodyne_phase180.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_homodyne_phase270.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_homodyne_phase270.exr"

mitsuba ../scenes/moving_cubes/moving_cubes_OFheterodyne_phase0.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_OFheterodyne_phase0.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_OFheterodyne_phase90.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_OFheterodyne_phase90.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_OFheterodyne_phase180.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_OFheterodyne_phase180.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_OFheterodyne_phase270.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_OFheterodyne_phase270.exr"

mitsuba ../scenes/moving_cubes/moving_cubes_heterodyne_phase0.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_heterodyne_phase0.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_heterodyne_phase90.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_heterodyne_phase90.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_heterodyne_phase180.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_heterodyne_phase180.exr"
mitsuba ../scenes/moving_cubes/moving_cubes_heterodyne_phase270.xml -m "llvm_ad_rgb" -o "result/moving_cubes/point/noatten/240MHz/individual/moving_cubes_heterodyne_phase270.exr"