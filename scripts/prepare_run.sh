#!/bin/bash

# A POSIX variable
OPTIND=1 # Reset in case getopts has been used previously in the shell.

TEAM_NAME=""

while getopts "h?n:" opt; do
    case "$opt" in
    h | \?)
        printf "Script to prepare docker images and simulation files from teams in the Field Robot Event.\nOptions:\n\n-n TEAM_NAME\n"
        exit 0
        ;;
    n)
        TEAM_NAME=$OPTARG
        ;;
    esac
done

shift $((OPTIND - 1))

[ "${1:-}" = "--" ] && shift

if [[ -z "${TEAM_NAME}" ]]; then
    printf "Script to prepare docker images and simulation files from teams in the Field Robot Event.\nOptions:\n\n-n TEAM_NAME\n"
    exit 0
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd 2>/dev/null)"
SIMULATION_FILES_DIR=$(readlink -f "${SCRIPT_DIR}/../simulation_files")
TEAM_FILES_DIR=$(readlink -f "${SCRIPT_DIR}/../competition_files/${TEAM_NAME}")

if [ ! -d "${TEAM_FILES_DIR}" ]; then
    echo "Could not load files of ${TEAM_NAME}. Are the files loaded?"
    exit 1
fi

echo "Copying simulation files..."
for folder in robot_packages rviz; do
    rm -rf "${SIMULATION_FILES_DIR}/${folder}"

    if [ $? -ne 0 ]; then
        echo "Failed to remove dir ${SIMULATION_FILES_DIR}/${folder}!"
        exit 1
    fi

    cp -r "${TEAM_FILES_DIR}/${folder}" ${SIMULATION_FILES_DIR}

    if [ $? -ne 0 ]; then
        echo "Failed to copy dir ${TEAM_FILES_DIR}/${folder}!"
        exit 1
    fi
done

echo "Removing generated files..."
for file in "${SIMULATION_FILES_DIR}/map/pred_map.csv" "${SIMULATION_FILES_DIR}/gt/mapping_results.png" "${SIMULATION_FILES_DIR}/gt/stats.csv"; do
    rm -f ${file}

    if [ $? -ne 0 ]; then
        echo "Failed to remove file ${file}!"
        exit 1
    fi
done

echo "Retagging Docker image from ${TEAM_NAME}/robot_workspace to robot_workspace"
docker tag "${TEAM_NAME}/robot_workspace" "robot_workspace"

if [ $? -ne 0 ]; then
    echo "Could not retag Docker image from ${TEAM_NAME}/robot_workspace to robot_workspace! Does the Docker image exists?"
    exit 1
fi

echo "All done."
