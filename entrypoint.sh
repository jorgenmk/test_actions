#!/bin/bash

ls
pwd
ls /gnuarmemb
ls /ncs
ls /ncs/zephyr

cd /ncs/nrf/applications/asset_tracker
mkdir b
echo ""
echo $GNUARMEMB_TOOLCHAIN_PATH
cd b
source /ncs/zephyr/zephyr-env.sh && cmake -DBOARD=nrf9160dk_nrf9160_ns -GNinja .. && ninja