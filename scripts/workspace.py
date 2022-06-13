from __future__ import annotations

from os import environ
from pathlib import Path
from re import compile, finditer, search
from typing import TypeVar
from xml.etree import ElementTree

import rospkg
from rospkg import RosPack
from rospkg.common import ResourceNotFound

_T = TypeVar("_T")
_URDF_EXTENSIONS = (".world", ".sdf", ".xacro", ".urdf")


class URDF:
    PACKAGE_REGEX = compile(r"package:\/\/(.+?)\/(.+\..+)")
    FIND_REGEX = compile(r"\$\(find (.+)\)\/(.+\..+)")

    def __init__(self, urdf_file: Path) -> None:
        self.urdf_file = urdf_file
        self.urdf_root = ElementTree.parse(self.urdf_file).getroot()

    def __repr__(self) -> str:
        return f"URDF file ({self.urdf_file.name})"

    def get_all_dependend_xacro_or_urdf_files(self) -> list[URDF]:
        all_used_files = [self]

        for used_file in self.get_all_dependencies(self.urdf_root)[1]:
            if used_file.suffix in _URDF_EXTENSIONS:
                all_used_files.append(URDF(used_file))

        return all_used_files

    def get_all_dependend_packages(self) -> list[str]:
        all_used_packages = []

        for used_file in self.get_all_dependencies(self.urdf_root)[0]:
            all_used_packages.append(used_file)

        return list(set(all_used_packages))

    @staticmethod
    def get_all_dependencies(xml: Path | ElementTree.Element) -> tuple[list[str], list[Path]]:
        packages = []
        resources = []

        if isinstance(xml, Path):
            xml = ElementTree.parse(xml).getroot()

        packages_, resources_ = URDF.get_dependencies_from_element(xml)

        packages.extend(packages_)
        resources.extend(resources_)

        packages = URDF.remove_double_instances(packages)
        resources = URDF.remove_double_instances(resources)

        for resource in resources:
            if resource.suffix.lower() in _URDF_EXTENSIONS:
                packages_, resources_ = URDF.get_all_dependencies(resource)

                packages.extend(packages_)
                resources.extend(resources_)

                packages = URDF.remove_double_instances(packages)
                resources = URDF.remove_double_instances(resources)

        return packages, resources

    @staticmethod
    def get_dependencies_from_element(xml_root: ElementTree.Element) -> tuple[list[str], list[Path]]:
        packages = []
        resources = []

        for tag in xml_root.findall(".//*[@filename]"):
            if tag.attrib["filename"].startswith("package://"):
                package_name_match = search(URDF.PACKAGE_REGEX, tag.attrib["filename"])

                if package_name_match is None:
                    raise SyntaxError(f"Cannot match resource path {tag.attrib['filename']}")

                package_name = package_name_match.group(1)
                resource_path = package_name_match.group(2)

            elif tag.attrib["filename"].startswith("$(find"):
                package_name_match = search(URDF.FIND_REGEX, tag.attrib["filename"])

                if package_name_match is None:
                    raise SyntaxError(f"Cannot match resource path {tag.attrib['filename']}")

                package_name = package_name_match.group(1)
                resource_path = package_name_match.group(2)

            elif tag.attrib["filename"].endswith(".so"):
                continue

            else:
                raise NotImplementedError(f"Cannot parse {tag.attrib['filename']}")

            relative_path = resource_path[1:] if resource_path.startswith("/") else resource_path

            try:
                resource_path = Path(RosPack().get_path(package_name)) / relative_path

                if not resource_path.is_file():
                    raise FileNotFoundError(f"Could not resolve file {resource_path} in {tag.attrib['filename']}")

            except ResourceNotFound as e:
                print(f"Could not find resource '{package_name}'!")
                raise ResourceNotFound from e

            packages.append(package_name)
            resources.append(resource_path)

        return packages, resources

    @staticmethod
    def remove_double_instances(input: list[_T]) -> list[_T]:
        return list(set(input))


class Workspace:
    XACRO_IN_LAUNCH_REGEX = compile(r"\$\(find\s(\S+)\)(\S+\.xacro|\.urdf)")

    def __init__(self, workspace_folder: Path) -> None:
        self.workspace_folder = workspace_folder

    def get_all_used_model_files(self) -> list[Path]:
        model_files = {}
        used_model_files = []

        for model_sdf in self.workspace_folder.glob("**/model.sdf"):
            root = model_sdf.parents[0]
            model_files[root.name] = model_sdf

        for world_file in self.workspace_folder.glob("**/*.world"):
            try:
                world_root = ElementTree.parse(world_file).getroot()
            except:
                print(f"Skipping non parseable world file {world_file}")
                continue

            used_model_files.append(world_file)

            for tag in world_root.findall(".//include/uri"):
                model_name_match = search(r"model:\/\/(.+)", tag.text)

                if model_name_match is None:
                    raise SyntaxError(f"Cannot parse model {tag.text}")

                model_name = model_name_match.group(1)

                try:
                    model_path = model_files[model_name]

                    if model_path not in used_model_files:
                        used_model_files.append(model_path)

                except KeyError as e:
                    print(f"Error: could not find model name {model_name}!")
                    raise KeyError from e

        return used_model_files

    def get_all_dependend_packages(self) -> list[str]:
        used_packages = []

        for launch_file in self.workspace_folder.glob("**/*.launch"):
            for xacro_or_urdf_file in finditer(
                Workspace.XACRO_IN_LAUNCH_REGEX, launch_file.read_text(encoding="utf-8")
            ):
                package_name = xacro_or_urdf_file.group(1)
                file_path = xacro_or_urdf_file.group(2)

                used_packages.append(package_name)

                try:
                    xacro_or_urdf_path = Path(RosPack().get_path(package_name)) / file_path[1:]

                    if not xacro_or_urdf_path.is_file():
                        raise FileNotFoundError(f"Could not resolve file {xacro_or_urdf_path} in {launch_file}")

                    urdf = URDF(xacro_or_urdf_path)
                    used_packages.extend(urdf.get_all_dependend_packages())

                except ResourceNotFound as e:
                    print(f"Could not find resource '{package_name}'!")
                    raise ResourceNotFound from e

        return list(set(used_packages))

    def get_all_used_xacro_files(self) -> list[URDF]:
        used_xacro_urdf_files = []

        for launch_file in self.workspace_folder.glob("**/*.launch"):
            for xacro_or_urdf_file in finditer(
                Workspace.XACRO_IN_LAUNCH_REGEX, launch_file.read_text(encoding="utf-8")
            ):
                package_name = xacro_or_urdf_file.group(1)
                file_path = xacro_or_urdf_file.group(2)

                try:
                    xacro_or_urdf_path = Path(RosPack().get_path(package_name)) / file_path[1:]

                    if not xacro_or_urdf_path.is_file():
                        raise FileNotFoundError(f"Could not resolve file {xacro_or_urdf_path} in {launch_file}")

                    urdf = URDF(xacro_or_urdf_path)
                    used_xacro_urdf_files.extend(urdf.get_all_dependend_xacro_or_urdf_files())

                except ResourceNotFound as e:
                    print(f"Could not find resource '{package_name}'!")
                    raise ResourceNotFound from e

        return list(set(used_xacro_urdf_files))

    @staticmethod
    def get_material_resource_folder() -> Path:
        gz_resource_path = environ.get("GAZEBO_RESOURCE_PATH", None)

        if gz_resource_path is None:
            raise EnvironmentError("GAZEBO_RESOURCE_PATH is not set!")

        for gz_resource in gz_resource_path.split(":"):
            material_resource_folder = Path(gz_resource).resolve() / "media/materials/scripts"
            if material_resource_folder.is_dir():
                return material_resource_folder

        raise NotADirectoryError("Could not find the gazebo material resource folder!")

    @classmethod
    def resolve(cls) -> Workspace:
        try:
            workspace_src_folder = Path(rospkg.RosPack().get_path("virtual_maize_field"))

            # Try to resolve the 'src' folder recursively
            max_depth = 10
            current_depth = 0
            while workspace_src_folder.name != "src" and current_depth < max_depth:
                workspace_src_folder = workspace_src_folder.parent
                current_depth += 1

            if current_depth == max_depth:
                raise NotADirectoryError("Cannot resolve the workspace source folder.")

        except ResourceNotFound as e:
            print("Could not find resource 'virtual_maize_field'!")
            raise ResourceNotFound from e

        return cls(workspace_src_folder)
