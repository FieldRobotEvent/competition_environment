# Competition environment
This repository contains the Dockerfiles and additional scripts needed to run a competition on your own computer. This competition uses two Docker containers (e.g. stand-alone software parts):

1. The simulation container which is provided by the organisation. This container will provide the Gazebo simulation and simulates all sensor data of your robot inside the virtual world.
2. The robot container which is made by you. This container should include all software needed to run your robot. An [example workspace](https://github.com/FieldRobotEvent/example_ws) containing a Dockerfile to build a robot container is provided.

## Usage
To run the competition environment, follow the steps below:
1. Create a Docker image of your robot workspace. This is explained in the [example workspace](https://github.com/FieldRobotEvent/example_ws).
2. Gather all files that are used for the simulation (meshes, textures, world files etc.):
```commandline
python3 scripts/gather_files_for_simulation.py
```
3. Start the competition environment:
```commandline
cd task_navigation
docker-compose up
```
This starts the competition environment by creating a simulation container and a robot container. The simulation container will be downloaded automatically. 
4. Open GZWeb in the browser by going to [`http://localhost:8080/`](http://localhost:8080/) and press the play button to start the simulation. This works best by using Google Chrome.

To stop the simulation, press `ctrl+c` in the terminal and execute `docker-compose down` stop both containers.

## Troubeshooting

| Error                                   | Cause                                                 | Solution              |
|-----------------------------------------|-------------------------------------------------------| ----------------------|
| `xvfb-run: error: Xvfb failed to start` | Another container is still running in the background. | `docker-compose down` |

If you have another error or the provided solution does not work, create a [new issue](https://github.com/FieldRobotEvent/competition_environment/issues). Help expanding this list by making a [pull request](https://github.com/FieldRobotEvent/competition_environment/pulls).

