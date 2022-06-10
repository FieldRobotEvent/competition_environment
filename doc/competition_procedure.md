# Competition procedure
Every team hands in their Docker image and compressed `simulation_files` folder on a USB-drive. 

## Before the event
1. Generate a random world for the task that looks like the real field:
```
rosrun virtual_maize_field generate_world.py fre22_task_<task_name>_fast
```
2. Open the world and write down the number of the plants that fell down at the start of the simulation.
3. Open the `generated.world` file and remove the plant numbers that were written down.
4. Copy all relevant simulation files to the competition environment:
```
cd ~/competition_environment
python3 scripts/copy_simulation_files.py
```
5. For every team, load the Docker file and simulation files:
```
cd ~/competition_environment
./scripts/load_files.sh -i <path_to_robot_workspace.tgz> -s <path_to_simulation_files.zip> -n <team_name>
```

## During the event
For every team, repeat the following procedure:
1. Prepare the teams run:
```
cd ~/competition_environment
./scripts/prepare_run.sh -n <team_name>
```
2. Start the simulation:
```
cd ~/competition_environment/task_<task_name>_cuda
./start_simulation.sh
```
3. Start the simulation for half a second to have the robot stand on the ground.
4. Indicate the start of the simulation to person responsable for the DLG stream.
5. Run the simulation, use 3D mouse to follow the robot.
6. After 3 minutes, the simulation automatically stops. For task mapping, click on the `show map` button to create a map of the mapped objects.
7. Possible discussion with the jury about the results.
8. Shut down the simulation by `Ctrl+C`.
9. Stop Docker:
```
docker-compose down
```
10. Clear up the workspace and copy the results to the teams folder:
```
cd ~/competition_environment
./scripts/finish_run.sh -n <team_name>
```

All the results of the run are saved in the `competition_files` folder in the directory `~/competition_environment/competition_files/<team_name>/results`. This includes the generated map (`pred_map.csv` and `mapping_results.png`) and the `stats.csv` file containing the number of destroyed plants, distances etc. 