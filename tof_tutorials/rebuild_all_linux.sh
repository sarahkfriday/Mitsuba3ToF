#!/bin/bash

mkdir ../build
cd ../build
cmake -GNinja ..
sed -i '' '94s/""/"llvm_ad_rgb"/' mitsuba.conf
ninja

