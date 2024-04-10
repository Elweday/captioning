FROM ubuntu:trusty

LABEL AUTHOR="Nasser"
LABEL DESCRIPTION="Studyio Docker Image for creating subtitles for videos. Based on dkarchmervue/moviepy"

ENV PYTHON_VERSION 3.10
ENV PYTHON_PIP_VERSION 21.3.1
ENV YASM_VERSION 1.3.0
ENV NUM_CORES 4

RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8 

# remove several traces of python
RUN apt-get purge -y python.*

# Add the following two dependencies if you want to use --enable-gnutls in FFPMEG: gnutls-bin
RUN echo deb http://archive.ubuntu.com/ubuntu trusty universe multiverse >> /etc/apt/sources.list; \
    apt-get update -qq && apt-get install -y --force-yes \
    ant \
    autoconf \
    automake \
    build-essential \
    curl \
    checkinstall \
    cmake \
    default-jdk \
    f2c \
    gfortran \
    git \
    g++ \
    imagemagick \
    libass-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libcnf-dev \
    libfaac-dev \
    libfreeimage-dev \
    libjpeg-dev \
    libjasper-dev \
    libgnutls-dev \
    liblapack3 \
    libmp3lame-dev \
    libpq-dev \
    libpng-dev \
    libsqlite3-dev \
    libssl-dev \
    libtheora-dev \
    libtiff4-dev \
    libtool \
    libxine-dev \
    libxvidcore-dev \
    libv4l-dev \
    libvorbis-dev \
    mercurial \
    openssl \
    pkg-config \
    postgresql-client \
    supervisor \
    wget \
    unzip; \
    apt-get clean

# gpg: key F73C700D: public key "Larry Hastings <larry@hastings.org>" imported
RUN gpg --keyserver ha.pool.sks-keyservers.net --recv-keys 97FC712E4C024BBEA48A61ED3A5CA953F73C700D

RUN set -x \
	&& mkdir -p /usr/src/python \
	&& curl -SL "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz \
	&& curl -SL "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz.asc" -o python.tar.xz.asc \
	&& gpg --verify python.tar.xz.asc \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz* \
	&& cd /usr/src/python \
	&& ./configure --enable-shared \
                       --enable-loadable-sqlite-extensions \
	&& make -j$(nproc) \
	&& make install \
	&& ldconfig \
	&& find /usr/local \
		\( -type d -a -name test -o -name tests \) \
		-o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		-exec rm -rf '{}' + \
	&& rm -rf /usr/src/python

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s easy_install-3.4 easy_install \
	&& ln -s idle3 idle \
	&& ln -s pip3 pip \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python-config3 python-config
    
RUN pip3 install --no-cache-dir --upgrade --ignore-installed pip==$PYTHON_PIP_VERSION

WORKDIR /usr/local/src

RUN curl -Os https://www.tortall.net/projects/yasm/releases/yasm-${YASM_VERSION}.tar.gz \
    && tar xzvf yasm-${YASM_VERSION}.tar.gz
                  

# Build YASM
# =================================
WORKDIR /usr/local/src/yasm-${YASM_VERSION}
RUN ./configure \
    && make -j ${NUM_CORES} \
    && make install
# =================================

# Remove all tmpfile and cleanup
# =================================
WORKDIR /usr/local/
RUN rm -rf /usr/local/src
RUN apt-get autoremove -y; apt-get clean -y
# =================================

# Setup a working directory to allow for
# docker run --rm -ti -v ${PWD}:/work ...
# =======================================
RUN mkdir /work
WORKDIR /work

#####################################################################
#
# A Docker image with everything needed to run Python/FFMPEG scripts
# 
# Image based on Ubuntu:14.04
#
#   with
#     - Latest Python 3.4
#     - Latest FFMPEG (built)
#     - ImageMagick
#
#   plus a bunch of build/web essentials
#
#####################################################################

ENV NUM_CORES 4

WORKDIR /usr/local/src

RUN git clone --depth 1 https://github.com/l-smash/l-smash \
    && git clone --depth 1 git://git.videolan.org/x264.git \
    && hg clone https://bitbucket.org/multicoreware/x265 \
    && git clone --depth 1 git://source.ffmpeg.org/ffmpeg \
    && git clone --depth 1 git://github.com/mstorsjo/fdk-aac.git \
    && git clone --depth 1 https://chromium.googlesource.com/webm/libvpx \
    && git clone https://git.xiph.org/opus.git \
    && git clone --depth 1 https://github.com/mulx/aacgain.git 
                  

# Build L-SMASH
# =================================
WORKDIR /usr/local/src/l-smash
RUN ./configure \
    && make -j ${NUM_CORES} \
    && make install
# =================================


# Build libx264
# =================================
WORKDIR /usr/local/src/x264
RUN ./configure --enable-static \
    && make -j ${NUM_CORES} \
    && make install
# =================================


# Build libx265
# =================================
WORKDIR  /usr/local/src/x265/build/linux
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DENABLE_SHARED:bool=off ../../

#####################################################################

# Installing Python packages

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install pip==19.1.1
RUN pip install -r requirements.txt

# Copy Python script
ADD app /code/app

# Entrypoint configuration
CMD           ["-h"]
ENTRYPOINT    ["python", "/code/app/main.py"]