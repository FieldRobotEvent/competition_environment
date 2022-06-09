#!/bin/bash

# A POSIX variable
OPTIND=1 # Reset in case getopts has been used previously in the shell.

IMAGE_FILE=""
SIMULATION_FILES=""
TEAM_NAME=""

while getopts "h?i:s:n:" opt; do
  case "$opt" in
  h | \?)
    printf "Script to load docker images and simulation files from teams in the Field Robot Event.\nOptions: \n\n-i IMAGE_NAME\n-s SIMULATION_FILES\n-n TEAM_NAME\n"
    exit 0
    ;;
  i)
    IMAGE_FILE=$OPTARG
    ;;
  s)
    SIMULATION_FILES=$OPTARG
    ;;
  n)
    TEAM_NAME=$OPTARG
    ;;
  esac
done

shift $((OPTIND - 1))

[ "${1:-}" = "--" ] && shift

if [[ -z ${IMAGE_FILE} || -z "${SIMULATION_FILES}" || -z "${TEAM_NAME}" ]]; then
  printf "Script to load docker images and simulation files from teams in the Field Robot Event.\nOptions: \n\n-i IMAGE_NAME\n-s SIMULATION_FILES\n-n TEAM_NAME\n"
  exit 0
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd 2>/dev/null)"
TEAM_FILES_DIR="${SCRIPT_DIR}/../competition_files/${TEAM_NAME}"

if [ -d ${TEAM_FILES_DIR} ]; then
  echo "Directory ${TEAM_FILES_DIR} already exists. Clearing folder now..."
  rm -r "${TEAM_FILES_DIR}"

  if [ $? -ne 0 ]; then
    echo "Failed to clear content of dir ${TEAM_FILES_DIR}!"
    exit 1
  fi
fi

mkdir -p "${TEAM_FILES_DIR}"
if [ $? -ne 0 ]; then
  echo "Failed to create dir ${TEAM_FILES_DIR}!"
  exit 1
fi

echo "Unzipping simulation files..."
unzip -qq ${SIMULATION_FILES} -d ${TEAM_FILES_DIR}

# Put files folder higher if placed in simulation_files subfolder
if [ -d "${TEAM_FILES_DIR}/simulation_files" ]; then
  pushd ${TEAM_FILES_DIR}
  mv simulation_files/* .
  rm -r simulation_files

  if [ $? -ne 0 ]; then
    echo "Failed to move dir ${TEAM_FILES_DIR}/simulation_files!"
    exit 1
  fi
  popd
fi

# Remove unneeded folders
for dir in ${TEAM_FILES_DIR}/*; do
  [ "$dir" = "${TEAM_FILES_DIR}/robot_packages" ] && continue
  [ "$dir" = "${TEAM_FILES_DIR}/rviz" ] && continue
  rm -rf "$dir"

  if [ $? -ne 0 ]; then
    echo "Failed to move dir ${TEAM_FILES_DIR}/${dir}!"
    exit 1
  fi
done

# Source: https://gist.github.com/stefanvangastel/d6b5b38e8716ea102b651c67c100225f
echo "Loading Docker image..."
LOAD_RESULT=$(docker load -i ${IMAGE_FILE})
echo ${LOAD_RESULT}

LOAD_IMAGE_NAME=${LOAD_RESULT#*: }

echo "Retagging Docker image from ${LOAD_IMAGE_NAME} to ${TEAM_NAME}/robot_workspace"
docker tag ${LOAD_IMAGE_NAME} "${TEAM_NAME}/robot_workspace"

echo "All done."
