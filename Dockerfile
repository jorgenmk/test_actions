# Container image that runs your code
FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Oslo
ENV ZEPHYR_BASE=/ncs/zephyr
ENV ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb
ENV GNUARMEMB_TOOLCHAIN_PATH=/gnuarmemb/gcc-arm-none-eabi-9-2019-q4-major

RUN apt-get update && apt-get install -y --no-install-recommends \
  wget \
  git \
  make \
  unzip \
  ninja-build \
  cmake \
  python3 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/master/scripts/requirements.txt

RUN wget --no-verbose https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 \
    && mkdir /gnuarmemb \
    && tar xf gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 -C /gnuarmemb \
    && rm gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2

RUN mkdir ncs \
  && cd ncs \
  && git clone https://github.com/nrfconnect/sdk-nrf.git nrf \
  && west init -l nrf \
  && west update

COPY entrypoint.sh /entrypoint.sh
COPY bsec_1-4-8-0_generic_release.zip .
COPY build-release /build-release
RUN mkdir bsec \
  && cd bsec \
  && unzip ../bsec_1-4-8-0_generic_release.zip \
  && cd .. \
  && rm bsec_1-4-8-0_generic_release.zip

RUN pip3 install tabulate

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]