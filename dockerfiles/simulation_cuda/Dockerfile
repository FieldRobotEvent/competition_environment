FROM fieldrobotevent/ros-noetic-cuda:latest

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

# Install packages
RUN apt-get update && \
  # Instal curl first
  apt-get -y --no-install-recommends install curl && \
  curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
  apt-get update && \
  apt-get -y --no-install-recommends install \
    # Ubuntu packages
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
    ros-${ROS_DISTRO}-rviz && \
  rm -rf /var/lib/apt/lists/*

# Clone the simulation code from Github and catkin_make
ENV SIMULATION_WS /simulation_ws
RUN mkdir -p ${SIMULATION_WS}/src && \
  git clone https://github.com/FieldRobotEvent/virtual_maize_field ${SIMULATION_WS}/src/virtual_maize_field && \
  git clone https://github.com/FieldRobotEvent/hector_gazebo_plugins ${SIMULATION_WS}/src/hector_gazebo_plugins && \
  git clone https://github.com/pal-robotics/realsense_gazebo_plugin/ ${SIMULATION_WS}/src/realsense_gazebo_plugin && \
  git clone https://github.com/FieldRobotEvent/evaluation_nodes ${SIMULATION_WS}/src/evaluation_nodes && \
  echo "source /opt/ros/${ROS_DISTRO}/setup.bash && \
  source /usr/share/gazebo/setup.sh && \
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
VOLUME ["${SIMULATION_WS}/src/virtual_maize_field/rviz"]
VOLUME ["${SIMULATION_WS}/src/robot_packages"]
VOLUME ["/tmp/.X11-unix"]
VOLUME ["/tmp/.docker.xauth"] 

# Make ROS master accessable from localhost
EXPOSE 11345

# Copy and create our entrypoint that sources both ROS and our workspace
COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# Create task ENV (will be overrided in docker-compose)
ENV TASK=navigation

# Start simulation
CMD roslaunch virtual_maize_field simulation.launch paused:=true gui:=true & roslaunch evaluation_nodes evaluation.launch task:=${TASK}