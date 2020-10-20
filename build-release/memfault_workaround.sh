#!/bin/bash

FILE=ncs/nrf/samples/nrf9160/memfault/config/memfault_platform_config.h
MEMFAULT_PATCH="#define MEMFAULT_HTTP_CHUNKS_API_HOST \"chunks-nrf91.memfault.com\""

if [ -f "$FILE" ]; then
    echo "Patching $FILE"
    echo "Using nrf91 compatible https endpoint."
    echo "/* Patch applied by CI */" >> $FILE
    echo $MEMFAULT_PATCH >> $FILE
    echo "/* End patch */" >> $FILE
else 
    echo "$FILE does not exist."
    echo "Memfault nrf91 patch not applied."
fi


