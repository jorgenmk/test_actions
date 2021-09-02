# Container image that runs your code
FROM ubuntu:latest

# Copies your code file from your action repository to the filesystem path `/` of the container

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Oslo

RUN apt-get update && apt-get install -y --no-install-recommends \
  wget \
  git \
  make \
  ninja-build \
  cmake \
  python3 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/master/scripts/requirements.txt

RUN wget --no-verbose https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 \
    && mkdir /gnuarmemb \
    && tar xf gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 -C /gnuarmemb

ENV ZEPHYR_BASE=/ncs/zephyr
ENV ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb
ENV GNUARMEMB_TOOLCHAIN_PATH=/gnuarmemb

#RUN wget --no-verbose https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.13.0/zephyr-sdk-0.13.0-linux-x86_64-setup.run \
#    && chmod +x zephyr-sdk-0.13.0-linux-x86_64-setup.run \
#    && ./zephyr-sdk-0.13.0-linux-x86_64-setup.run 

COPY entrypoint.sh /entrypoint.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]