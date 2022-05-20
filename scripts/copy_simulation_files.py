#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import shutil

from rospkg import RosPack
from rospkg.common import ResourceNotFound
from validator import validator
from workspace import Workspace

SIMULATION_ASSETS_FOLDER = pathlib.Path(__file__).parents[1] / "simulation_files"
VMF_FOLDERS_TO_COPY = (
    "Media",
    "map",
    "worlds",
    "launch",
    "rviz",
    "models",
)  # Folders that are needed by the simulation container
GZWEB_VMF_FOLDERS_TO_COPY = (
    "models",
    "Media/models",
)  # Folders that are needed for GZWeb in the simulation container
GZWEB_EXTENSIONS_TO_KEEP = (
    ".stl",
    ".dae",
    ".sdf",
    ".config",
    ".material",
    ".png",
    ".jpg",
    ".tiff",
    ".jpeg",
    ".gazebo",
)  # File extensions that are needed by GZWeb

GAZEBO_EXTENSIONS_TO_KEEP = (
    ".stl",
    ".dae",
    ".sdf",
    ".config",
    ".material",
    ".png",
    ".jpg",
    ".tiff",
    ".jpeg",
    ".gazebo",
    ".xml",
)  # File extensions that are needed by Gazebo in the simulation container


rpack = RosPack()


def copytree(
    src: pathlib.Path | str,
    dst: pathlib.Path | str,
    symlinks: bool = False,
    ignore: list[str] | None = None,
) -> None:
    """
    Source: https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    """
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def remove_empty_directories(path: pathlib.Path | str, remove_root: bool = True) -> None:
    """
    Source: https://jacobtomlinson.dev/posts/2014/python-script-recursively-remove-empty-folders/directories/
    """
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                remove_empty_directories(full_path)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and remove_root:
        os.rmdir(path)


def gather_and_copy_files(ws: Workspace) -> None:
    vmf = pathlib.Path(rpack.get_path("virtual_maize_field"))

    for folder in VMF_FOLDERS_TO_COPY:
        print(f"\033[92m\u2714 {folder} -> {SIMULATION_ASSETS_FOLDER / folder}\033[0m")
        copytree(vmf / folder, SIMULATION_ASSETS_FOLDER / folder)

    # Create gzweb assets
    gzweb_folder = SIMULATION_ASSETS_FOLDER / "gzweb"
    gzweb_folder.mkdir()

    for folder in GZWEB_VMF_FOLDERS_TO_COPY:
        print(f"\033[92m\u2714 {folder} -> {gzweb_folder}\033[0m")
        copytree(vmf / folder, gzweb_folder)

    # Copy additional Gazebo resources
    gazebo_material_resources = ws.get_material_resource_folder()
    print(f"\033[92m\u2714 {gazebo_material_resources} ->" f" {gzweb_folder}/materials/scripts\033[0m")
    copytree(gazebo_material_resources, gzweb_folder / "materials/scripts")

    # Copy all custom packages from workspace
    required_packages = ws.get_all_dependend_packages()
    for pkg in required_packages:
        pkg_path = pathlib.Path(rpack.get_path(pkg))
        if (pkg_path / "meshes").is_dir():
            print(f"\033[92m\u2714 {pkg_path} -> {gzweb_folder}\033[0m")
            copytree(pkg_path, gzweb_folder / pkg_path.name)

    # Cleanup GZWeb assets folder
    for f in gzweb_folder.glob("**/*"):
        if f.is_file() and not f.suffix.lower() in GZWEB_EXTENSIONS_TO_KEEP:
            f.unlink()
    remove_empty_directories(gzweb_folder)

    # Copy all custom packages from workspace to robot packages folder, they are needed to start Gazebo
    robot_packages_folder = SIMULATION_ASSETS_FOLDER / "robot_packages"
    robot_packages_folder.mkdir()

    required_packages = ws.get_all_dependend_packages()
    for pkg in required_packages:
        pkg_path = pathlib.Path(rpack.get_path(pkg))
        print(f"\033[92m\u2714 {pkg_path} -> {robot_packages_folder}\033[0m")
        copytree(pkg_path, robot_packages_folder / pkg_path.name)

    # Cleanup folder
    for f in robot_packages_folder.glob("**/*"):
        if f.is_file() and not f.suffix.lower() in GAZEBO_EXTENSIONS_TO_KEEP:
            f.unlink()
    remove_empty_directories(robot_packages_folder)


if __name__ == "__main__":
    try:
        ws = Workspace.resolve()

        print(f"Using workspace '{ws.workspace_folder}'.")

        valid = validator.validate_all(ws)

        if valid:
            print("\nRemoving old simulation files...")
            for f in SIMULATION_ASSETS_FOLDER.glob("*"):
                if f.is_dir():
                    shutil.rmtree(f)

            print("\nCopy files:")
            gather_and_copy_files(ws)

    except NotADirectoryError:
        print(
            "Cannot find your workspace 'src' folder. Did you place the"
            " 'virtual_maize_field' package in your 'src' folder?"
        )

    except ResourceNotFound:
        print(
            "Cannot find package 'virtual_maize_field'. Did you clone the virtual maize"
            " field package into your workspace and did a 'catkin_make'? Did you source"
            " your workspace?"
        )
