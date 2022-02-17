#!/bin/bash
set -e

# Setup ROS environment + Gazebo + NVM
# Adapted from: https://github.com/osrf/docker_images/blob/master/ros/noetic/ubuntu/focal/ros-core/ros_entrypoint.sh
source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "/usr/share/gazebo/setup.sh"
source "${SIMULATION_WS}/devel/setup.bash"
source "${NVM_DIR}/nvm.sh"

exec "$@"