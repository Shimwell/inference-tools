# docker build -t inference .

FROM ubuntu:18.04

# Python and OpenMC installation

RUN apt-get --yes update && apt-get --yes upgrade

RUN apt-get -y install locales
RUN locale-gen en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# Install Packages Required
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get --yes install gfortran 
RUN apt-get --yes install g++ 
RUN apt-get --yes install cmake 
RUN apt-get --yes install libhdf5-dev 
RUN apt-get --yes install git
RUN apt-get update

RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y ipython3
RUN apt-get update
RUN apt-get install -y python3-tk

RUN apt-get -y install git
# RUN git clone https://github.com/C-bowman/inference-tools.git
# RUN cd inference-tools && python3 setup.py install

RUN pip3 install matplotlib
RUN pip3 install scipy
RUN pip3 install numpy


#TODO
# make dockerhub account
# build docker image
# upload to docker hub

# make circleci account
# link to github repo


