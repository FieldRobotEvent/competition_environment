# Create a robot container from scratch
We have selected to use containers in order to allow you to be as creative as you can be as a competitor. In the example workspace we provide a [Dockerfile](https://github.com/FieldRobotEvent/example_ws/blob/main/Dockerfile) which should work for most robots. However, you are free to implement a robot container from scratch. This document provides you some hints.

To develop a container from scratch, please consider reading the [Dockerfile](https://github.com/FieldRobotEvent/example_ws/blob/main/Dockerfile) provided in the example workspace as a starting point. We would encourage you to do so using a Dockerfile, and then to compile your container using `docker build . -t robot_workspace` from it. This will allow you to more easily reproduce the work. We use ROS Noetic, however using another version of ROS or ROS2 should work as well.

## Hints for starting from scratch

* Be aware of the mounts we are going to use in the `docker-compose.yml` files found in each task. We will be using these mount points (and only these mount points), so make sure you expose those `VOLUME`s in your container for us to use. This probably won't look pretty if you're building from scratch, but you will have to deal with it.
* The simulation container runs a rosmaster at http://simulation:11311, as stated in the `ENV` field in the [Dockerfile](https://github.com/FieldRobotEvent/example_ws/blob/main/Dockerfile) in the example workspace. You will need to communicate to this port to interact with Gazebo.
* Make sure your `CMD` is set correctly - we do not plan on overriding this in the `docker-compose.yml` file we will use in competition mode.

Beyond that, you are free to completely rebuild the entire environment as you see fit.