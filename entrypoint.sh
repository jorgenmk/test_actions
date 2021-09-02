#!/bin/bash

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
mkdir ncs
cd ncs
git clone https://github.com/nrfconnect/sdk-nrf.git nrf
west init -l nrf
west update
cd nrf/applications/asset_tracker
mkdir b
cd b
cmake -DBOARD=nrf9160dk_nrf9160_ns -GNinja ..
ninja