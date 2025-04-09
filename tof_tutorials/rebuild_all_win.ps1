param (
    [string]$buildMode
)
if (-not $buildMode) { $buildMode = "Release" } # default value

cd ../
cmake -G "Visual Studio 17 2022" -A x64 -B build

cd build
Write-Host "Changing mitsuba config..."
# set python default
(Get-Content "mitsuba.conf") -replace '"python-default": "",', '"python-default": "llvm_ad_rgb",' | Set-Content "mitsuba.conf"
cd ../
Write-Host "Done"

cmake --build build --config $buildMode
cd build/$buildMode
& ".\setpath.ps1"
cd ../../tof_tutorials/
$env:DRJIT_LIBLLVM_PATH="C:\Program Files\LLVM\bin\LLVM-C.dll"