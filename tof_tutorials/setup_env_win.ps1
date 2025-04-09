param (
    [string]$buildMode
)
if (-not $buildMode) { $buildMode = "Release" } # default value

# Construct the full path
$TargetPath = Join-Path -Path "..\build\" -ChildPath $buildMode

# cd to build folder and setpath
cd $TargetPath
& ".\setpath.ps1"
cd "..\..\tof_tutorials"

# activate anaconda env
powershell -ExecutionPolicy ByPass -NoExit -Command "& 'C:\Users\f005cbs\AppData\Local\miniconda3\shell\condabin\conda-hook.ps1'"
conda activate mitsuba3tof
# set env variable
$env:DRJIT_LIBLLVM_PATH="C:\Program Files\LLVM\bin\LLVM-C.dll"