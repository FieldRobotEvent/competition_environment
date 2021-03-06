#!/bin/bash

# A POSIX variable
OPTIND=1 # Reset in case getopts has been used previously in the shell.

TEAM_NAME=""

while getopts "h?n:" opt; do
    case "$opt" in
    h | \?)
        printf "Script to finish the simulation and backup files in the Field Robot Event.\nOptions:\n\n-n TEAM_NAME\n"
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
    printf "Script to finish the simulation and backup files in the Field Robot Event.\nOptions:\n\n-n TEAM_NAME\n"
    exit 0
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd 2>/dev/null)"
SIMULATION_FILES_DIR=$(readlink -f "${SCRIPT_DIR}/../simulation_files")
TEAM_FILES_DIR=$(readlink -f "${SCRIPT_DIR}/../competition_files/${TEAM_NAME}")

if [ ! -d "${TEAM_FILES_DIR}" ]; then
    echo "Could not load files of ${TEAM_NAME}. Are the files loaded?"
    exit 1
fi

if [ -d "${TEAM_FILES_DIR}/results" ]; then
    echo "Directory ${TEAM_FILES_DIR}/results already exists. Clearing folder now..."
    rm -r "${TEAM_FILES_DIR}/results"

    if [ $? -ne 0 ]; then
        echo "Failed to clear content of dir ${TEAM_FILES_DIR}/results!"
        exit 1
    fi
fi

mkdir -p "${TEAM_FILES_DIR}/results"
if [ $? -ne 0 ]; then
    echo "Failed to create dir ${TEAM_FILES_DIR}/results!"
    exit 1
fi

for file in "${SIMULATION_FILES_DIR}/map/pred_map.csv" "${SIMULATION_FILES_DIR}/gt/mapping_results.png" "${SIMULATION_FILES_DIR}/gt/stats.csv"; do
    if [ ! -f "${file}" ]; then
        echo "Could not find ${file}"
        continue
    fi

    # Fix permissions
    sudo chown ${USER} ${file}

    mv ${file} "${TEAM_FILES_DIR}/results"

    if [ $? -ne 0 ]; then
        echo "Failed to copy file ${file}!"
        exit 1
    fi
done

echo "All done."
