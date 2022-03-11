# Dockerfile with ROS Noetic and CUDA enabled
# Source ROS Noetic Docker: https://github.com/osrf/docker_images/blob/master/ros/noetic/ubuntu/focal/ros-core/Dockerfile
FROM nvidia/cuda:11.5.1-cudnn8-runtime-ubuntu20.04

# Setup timezone
RUN echo 'Etc/UTC' > /etc/timezone && \
    ln -s /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    apt-get update && \
    apt-get install -q -y --no-install-recommends \
        tzdata && \
    rm -rf /var/lib/apt/lists/*

# Install packages
RUN apt-get update && apt-get install -q -y --no-install-recommends \
    dirmngr \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Setup sources.list
RUN echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros1-latest.list

# Setup keys
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

# Setup environment
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

ENV ROS_DISTRO noetic

# Install ros packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ros-noetic-ros-base=1.5.0-1* \
        build-essential \    
        python3-rosdep \    
        python3-rosinstall \     
        python3-vcstools && \
    rosdep init && \
    rosdep update --rosdistro $ROS_DISTRO && \
    rm -rf /var/lib/apt/lists/*

# Setup entrypoint
COPY ./ros_entrypoint.sh /

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]