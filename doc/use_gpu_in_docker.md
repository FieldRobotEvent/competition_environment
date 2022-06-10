# Use CUDA inside Docker
---
**NOTE**

To use CUDA capabilities with the provided docker-compose files, you need at least Docker Compose v1.28.0 and `nvidia-docker2`. [Download](https://docs.docker.com/compose/install/) or [upgrade](https://stackoverflow.com/questions/49839028/how-to-upgrade-docker-compose-to-latest-version) your Docker Compose if needed and install [`nvidia-docker2`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

---

If you have a computer with a (recent) NVIDIA GPU, you can speed up the simulation container and / or use CUDA in your robot container. You can test this by running `nvidia-smi`. To this end, we provide a seperate simulation image on [Dockerhub](https://hub.docker.com/r/fieldrobotevent/simulation-cuda) in which the GPU is enabled. Instead of using `GZWeb`, this simulation image automatically launches the Gazebo Client user interface and an evaluation window.

## Run the competition environment with CUDA
All docker compose files have two versions, one for use without CUDA and one for use with CUDA. The docker compose files in the folders ending with `_cuda` can be used with your GPU. As example, launch the navigation task:

```commandline
python3 scripts/copy_simulation_files.py
cd task_navigation_cuda
./start_simulation.sh
```

The bash script inside this folder is setting up `XAuthority` to be able to launch screens from the Docker in your computer and afterwards starts the simulation by `docker-compose up`. You can stop the simulation by pressing `ctrl+c` and stop the container by running `docker-compose down` in the terminal. 

## Use CUDA within your robot container

To use CUDA within your robot container, change the `FROM` argument to `fieldrobotevent/ros-noetic-cuda:latest` and add the `nvidia-container-runtime` environent variables in your `Dockerfile`:

```dockerfile
FROM fieldrobotevent/ros-noetic-cuda:latest

ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

# Rest of your Dockerfile
```
You can test if your robot workspace has CUDA capabilities by running `docker run --rm -it --gpus all robot_workspace nvidia-smi` after building your robot workspace image.
