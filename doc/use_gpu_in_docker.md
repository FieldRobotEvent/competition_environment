# Use GPU for simulation inside Docker
---
**NOTE**

This probably works, but we still have to test this and provide an example Dockerfile for the robot workspace with CUDA enabled. This will be updated in the future.

---
If you have a computer with a (recent) NVIDIA GPU, you can use the GPU to speed up the simulation container. To this end, we provide a seperate simulation image on [Dockerhub](https://hub.docker.com/r/fieldrobotevent/simulation_nvidia) in which the GPU is enabled. Instead of using `GZWeb`, this simulation image automatically launches the Gazebo Client user interface and RVIZ.

Before you can use your GPU inside the Docker, you need to install the NVIDIA container toolkit and upgrade docker-compose to the newest version.

## Install NVIDIA container toolkit
Instructions below are from the [NVIDIA site](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

1. Setup the keys:
```commandline
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```

2. Install NVIDIA-docker2
```commandline
sudo apt-get update
sudo apt-get install -y nvidia-docker2
```

3. Restart Docker:
```commandline
sudo systemctl restart docker
```

You can test if the GPU works inside the docker by running `docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi`. This should return some details of your GPU.

## Upgrade docker-compose
Check the version of your docker-compose with `docker-compose -v`. If this version is lower than v1.28.0, upgrade using the steps below.

If you have an old version of docker-compose installed, remove it.
```commandline
sudo apt-get remove docker-compose     # if installed using apt-get
sudo rm /usr/local/bin/docker-compose  # if installed using curl
pip uninstall docker-compose           # if installed using pip
```

Install the newest version:
```commandline
VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*\d')
DESTINATION=/usr/bin/docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION
sudo chmod 755 $DESTINATION
```

## Use the simulation container with the GPU
All docker compose files have two versions, one for use without GPU and one for use with GPU. The docker compose files in the folders ending with `_nvidia` can be used with your GPU. 

```commandline
python3 scripts/copy_simulation_files.py
cd task_navigation_nvidia
./start_simulation.sh
```

The bash script inside this folder is setting up `XAuthority` to be able to launch screens from the Docker in your computer and afterwards starts the simulation by `docker-compose up`. You can stop the simulation by pressing `ctrl+c` and stop the container by running `docker-compose down` in the terminal. 
