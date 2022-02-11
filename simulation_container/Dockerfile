FROM ros:noetic

LABEL org.opencontainers.image.authors="Field Robot Event Team <fieldrobot.events@wur.nl>"

ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update && \
  # Instal curl first
  apt-get -y --no-install-recommends install curl && \
  curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
  apt-get update && \
  apt-get -y --no-install-recommends install \
    # Ubuntu packages
    xvfb \
    git \
    python3-pip \
    # ROS packages
    ros-${ROS_DISTRO}-gazebo-ros-pkgs \
    ros-${ROS_DISTRO}-gazebo-ros-control \
    ros-${ROS_DISTRO}-pointgrey-camera-description \
    ros-${ROS_DISTRO}-robot-localization \
    ros-${ROS_DISTRO}-twist-mux \
    ros-${ROS_DISTRO}-interactive-marker-twist-server \
    ros-${ROS_DISTRO}-ros-controllers \
    ros-${ROS_DISTRO}-four-wheel-steering-controller \
    ros-${ROS_DISTRO}-urdf-geometry-parser \
    ros-${ROS_DISTRO}-hector-gazebo-plugins \
    # GZWeb dependencies
    libjansson-dev \
    libboost-dev \
    imagemagick \
    libtinyxml-dev \ 
    mercurial \
    cmake \
    build-essential && \
  rm -rf /var/lib/apt/lists/* && \
  # Install NVM
  curl -s -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash 

# Install NODE
ENV NVM_DIR /root/.nvm
ENV NODE_VERSION 11
ENV NODE_PATH ${NVM_DIR}/${NODE_VERSION}/lib/node_modules
ENV PATH ${NVM_DIR}/versions/node/${NODE_VERSION}/bin:$PATH
RUN echo "source ${NVM_DIR}/nvm.sh && \
    nvm install ${NODE_VERSION} && \
    nvm alias default ${NODE_VERSION} && \
    nvm use default" | bash 
    
# Clone the GZweb code from Github and build
ENV GZWEB_DIR /gzweb
RUN git clone https://github.com/osrf/gzweb ${GZWEB_DIR}
RUN echo "source /usr/share/gazebo/setup.sh && \
    source ${NVM_DIR}/nvm.sh && \
    cd ${GZWEB_DIR} && \
    xvfb-run -s '-screen 0 1280x1024x24' npm run deploy ---" | bash 

# Clone the simulation code from Github and catkin_make
ENV SIMULATION_WS /simulation_ws
RUN mkdir -p ${SIMULATION_WS}/src && \
  git clone https://github.com/FieldRobotEvent/virtual_maize_field ${SIMULATION_WS}/src/virtual_maize_field && \
  echo "source /opt/ros/${ROS_DISTRO}/setup.bash && \
  cd ${SIMULATION_WS}/ && \
  catkin_make" | bash
  
# Install the dependencies of the repository
RUN apt-get update && \
  rosdep install -y --from-paths ${SIMULATION_WS} --ignore-src && \
  rm -rf /var/lib/apt/lists/* 

# Cleanup image
RUN apt-get -y remove curl

# Create volumes to access files outside the docker container
VOLUME ["${SIMULATION_WS}/src/virtual_maize_field/map"]
VOLUME ["${SIMULATION_WS}/src/virtual_maize_field/Media"]
VOLUME ["${SIMULATION_WS}/src/virtual_maize_field/worlds"]
VOLUME ["${SIMULATION_WS}/src/virtual_maize_field/launch"]
VOLUME ["${SIMULATION_WS}/src/robot_packages"]
VOLUME ["${GZWEB_DIR}/http/client/assets"]

# Make GZWeb and ROS master accessable from localhost
EXPOSE 8080 11345

# Copy and create our entrypoint that sources both ROS, our workspace and NPM
COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# Start simulation and GZWeb, only show non-standard output for GZWeb
CMD xvfb-run -s '-screen 0 1280x1024x24' roslaunch virtual_maize_field simulation.launch paused:=true gui:=false & \
  echo "npm start --prefix ${GZWEB_DIR} 1> /dev/null" | bash
