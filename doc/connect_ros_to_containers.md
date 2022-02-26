# Connect your local ROS installation to the competition environment
To run additional (debugging) nodes on your computer, or watch the content of certain topics, you have to change the `ROS_MASTER_URI` (temporary) to the ip-address of the simulation container (which is running the `rosmaster`). The ip-address of the simulation container is set to `172.20.0.5`. 

In a terminal, change to `ROS_MASTER_URI` by:
```commandline
ROS_MASTER_URI=http://172.20.0.5:11311
```

In the same terminal, you can now check for the running topics by `rostopic list`, echo a specific topic by `rostopic echo <topic_name>` or start nodes like `rosrun rviz rviz`. When you close the terminal, the `ROS_MASTER_URI` is set to the default value.
