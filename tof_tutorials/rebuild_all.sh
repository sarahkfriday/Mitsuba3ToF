#!/bin/zsh

mkdir ../build
cd ../build
export DRJIT_LIBLLVM_PATH=/Users/sarahfriday/anaconda3/pkgs/libllvm12-12.0.0-h12f7ac0_4/lib/libLLVM-12.dylib
cmake -GNinja ..
sed -i '' '94s/""/"llvm_ad_rgb"/' mitsuba.conf
ninja
cd ../tof_tutorials/
source ./../build/setpath.sh
export DRJIT_LIBLLVM_PATH=/Users/sarahfriday/anaconda3/pkgs/libllvm12-12.0.0-h12f7ac0_4/lib/libLLVM-12.dylib