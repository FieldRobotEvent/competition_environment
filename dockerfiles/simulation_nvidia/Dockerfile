FROM fieldrobotevent/simulation:latest

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

# Install RVIZ
RUN apt-get update && \
    apt-get -y --no-install-recommends install \
        ros-${ROS_DISTRO}-rviz && \
    rm -rf /var/lib/apt/lists/*

# Remove GZWeb + NVM to save some space
RUN echo "cd ${GZWEB_DIR} && shopt -s extglob && rm -rf '!(http)'" | bash && \
    echo "rm -rf ${NVM_DIR} ~/.npm ~/.bower" | bash

VOLUME ["/tmp/.X11-unix"]
VOLUME ["/tmp/.docker.xauth"] 

# Copy and create our entrypoint that sources both ROS and our workspace
COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# Start simulation
CMD roslaunch virtual_maize_field simulation.launch paused:=true gui:=true & rosrun rviz rviz