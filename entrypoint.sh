#!/bin/bash

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
ls gnuarmemb
ls ncs
ls ncs/zephyr
#export GNUARMEMB_TOOLCHAIN_PATH=/gnuarmemb/gcc-arm-none-eabi-9-2019-q4-major
cd ncs/nrf/applications/asset_tracker
mkdir b
echo ""
echo $GNUARMEMB_TOOLCHAIN_PATH
cd b
source /ncs/zephyr/zephyr-env.sh && cmake -DBOARD=nrf9160dk_nrf9160_ns -GNinja .. && ninja