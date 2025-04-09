param (
    [bool]$noatten = $false  # Parameter to check if we should replace "atten" with "noatten"
)

$scene_path = "..\scenes\moving_cubes\"
$filenames = @("moving_cubes_radiance.xml", "moving_cubes_depth.xml", "moving_cubes_velocity.xml", "moving_cubes_homodyne_phase0.xml", "moving_cubes_homodyne_phase90.xml", "moving_cubes_homodyne_phase180.xml", "moving_cubes_homodyne_phase270.xml", "moving_cubes_OFheterodyne_phase0.xml", "moving_cubes_OFheterodyne_phase90.xml", "moving_cubes_OFheterodyne_phase180.xml", "moving_cubes_OFheterodyne_phase270.xml", "moving_cubes_heterodyne_phase0.xml", "moving_cubes_heterodyne_phase90.xml", "moving_cubes_heterodyne_phase180.xml", "moving_cubes_heterodyne_phase270.xml")
$output_dir = ".\result\moving_cubes\point\atten\"
if ($noatten){
    $output_dir = $output_dir -replace "atten", "noatten"
}

foreach ($file in $filenames){
    $sceneFilePath = "$scene_path$file"
    $outputFilename = $file -replace "xml", "exr"
    $outputFilePath = "$output_dir$outputFilename"

    & "mitsuba" $sceneFilePath -m "llvm_ad_rgb" -o $outputFilePath
}