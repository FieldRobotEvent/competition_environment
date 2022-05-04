from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from xml.etree import ElementTree

from rospkg.common import ResourceNotFound
from workspace import Workspace

COLLADA_NS = "{http://www.collada.org/2005/11/COLLADASchema}"
ALLOWED_GAZEBO_PLUGINS = (
    "libgazebo_ros_camera.so",
    "libgazebo_ros_multicamera.so",
    "libgazebo_ros_openni_kinect.so",
    "libgazebo_ros_control.so",
    "libgazebo_ros_gpu_laser.so",
    "libhector_gazebo_ros_imu.so",
    "libgazebo_ros_bumper.so",
    "librealsense_gazebo_plugin.so",
)  # All allowed sensor plugins. No other plugins will be installed in the simulation container.


class ValidationResult(Enum):
    ERROR = auto()
    OK = auto()
    WARNING = auto()


@dataclass
class ValidationFeedback:
    result: ValidationResult
    msg: str = ""


class Validation:
    def __init__(self) -> None:
        self.validation_checks: list[Callable[[Workspace], ValidationFeedback]] = []

    def register(self, f: Callable[[Workspace], ValidationFeedback]) -> None:
        self.validation_checks.append(f)

    def validate_all(self, ws: Workspace) -> bool:
        for ck in self.validation_checks:
            name = ck.__name__.replace("check_", "").replace("_", " ").capitalize()
            fdbck = ck(ws)

            if fdbck.result == ValidationResult.ERROR:
                color = "\033[91m"
                sign = "\u2718"
            elif fdbck.result == ValidationResult.WARNING:
                color = "\033[93m"
                sign = "\u003f"
            else:
                sign = "\u2714"
                color = "\033[92m"

            print(f"{color}{sign} {name : <20}\t: {fdbck.msg}\033[0m")
            if fdbck.result == ValidationResult.ERROR:
                return False

        return True


# Create validator to check the folder structure, meshes etc.
validator = Validation()


@validator.register
def check_find_gazebo_resources(ws: Workspace) -> ValidationFeedback:
    # Check if we can find the Gazebo material resource
    try:
        gazebo_material_resource_folder = ws.get_material_resource_folder()

        msg = "Found gazebo material resource folder in" f" '{gazebo_material_resource_folder}'"
        return ValidationFeedback(ValidationResult.OK, msg)

    except NotADirectoryError:
        msg = "Could not find the gazebo material resource folder! Check your Gazebo" " installation."
        return ValidationFeedback(ValidationResult.ERROR, msg)

    except EnvironmentError:
        msg = (
            "GAZEBO_RESOURCE_PATH is not set! Did you source Gazebo in your .bashrc"
            " file? If not, try adding 'source /usr/share/gazebo/setup.bash' to your"
            " bash file."
        )
        return ValidationFeedback(ValidationResult.ERROR, msg)


@validator.register
def check_world_file(ws: Workspace) -> ValidationFeedback:
    model_files = ws.get_all_used_model_files()
    _found_world_file = False

    for model_file in model_files:
        if "virtual_maize_field/worlds/generated.world" in str(model_file):
            _found_world_file = True

        # Empty <materials></materials> tags don't work using GZWeb. Raise error if they are in the world file.
        # Probably because of old world template
        root = ElementTree.parse(model_file).getroot()
        for m_tag in root.findall(".//materials"):
            if m_tag.text is None:
                msg = (
                    f"The model file '{model_file}' contains empty <materials></materials>"
                    " tags. This gives a problem in visualisation of the environment. Update"
                    " the virtual_maize_field package to the newest version or manually remove"
                    " the empty <materials></materials>tags from the world file."
                )
                return ValidationFeedback(ValidationResult.ERROR, msg)

    if not _found_world_file:
        msg = (
            "Could not find your generated .world file at '(..)/virtual_maize_field/worlds/generated.world'. "
            "Generate a world file by 'rosrun virtual_maize_field generate_world.py fre22_task_navigation_mini'"
        )
        return ValidationFeedback(ValidationResult.ERROR, msg)

    msg = "World file is correct."
    return ValidationFeedback(ValidationResult.OK, msg)


@validator.register
def check_dependencies(ws: Workspace) -> ValidationFeedback:
    try:
        resources = ws.get_all_dependend_packages()
        msg = f"Need resources from {resources}"
        return ValidationFeedback(ValidationResult.OK, msg)

    except FileNotFoundError as exc:
        msg = "Could not find all dependencies of the xacro and urdf files:" f" '{str(exc)}'."
        return ValidationFeedback(ValidationResult.WARNING, msg)

    except SyntaxError as exc:
        msg = f"Syntax of some files is not correct: '{str(exc)}'."
        return ValidationFeedback(ValidationResult.WARNING, msg)

    except ResourceNotFound as exc:
        msg = "Could not find all packages required by the xacro and urdf files:" f" '{str(exc)}'."
        return ValidationFeedback(ValidationResult.WARNING, msg)


@validator.register
def check_mesh_files(ws: Workspace) -> ValidationFeedback:
    model_files = ws.get_all_used_model_files()

    i = 0
    for model_file in model_files:
        for mesh_file in model_file.parent.glob("**/*.dae"):
            i += 1

            root = ElementTree.parse(mesh_file).getroot()
            for init_tag in root.findall(f".//{COLLADA_NS}init_from"):
                if (
                    init_tag.text.endswith(".png") or init_tag.text.endswith(".jpg") or init_tag.text.endswith(".jpeg")
                ) and "../materials/textures" not in init_tag.text:
                    msg = (
                        f"Texture '{ init_tag.text.split('/')[-1] }' in"
                        f" '{mesh_file.parents[1]}' should be placed in the folder"
                        f" {mesh_file.parents[1]}/materials/textures'. Move the file to this"
                        f" folder and edit the '{mesh_file.name} file."
                    )
                    return ValidationFeedback(ValidationResult.ERROR, msg)

    msg = f"All {i} meshes in { len(model_files) } models files are valid"
    return ValidationFeedback(ValidationResult.OK, msg)


@validator.register
def check_gazebo_plugins(ws: Workspace) -> ValidationFeedback:
    xacro_files = ws.get_all_used_xacro_files()
    used_plugins = []

    for xacro_file in xacro_files:
        for plugin_tag in xacro_file.urdf_root.findall(".//plugin"):
            used_plugins.append(plugin_tag.attrib["filename"])

            if plugin_tag.attrib["filename"] not in ALLOWED_GAZEBO_PLUGINS:
                allowed_plugin_str = ", ".join(ALLOWED_GAZEBO_PLUGINS)
                msg = (
                    f"Gazebo plugin '{plugin_tag.attrib['filename']}' used in"
                    f" '{xacro_file.urdf_file.name}' is not allowed in the"
                    f" competition! Allowed sensor plugins are: {allowed_plugin_str}"
                )
                return ValidationFeedback(ValidationResult.ERROR, msg)

    used_plugins_str = ", ".join(used_plugins)

    msg = f"All used Gazebo plugins ({used_plugins_str}) are allowed"
    return ValidationFeedback(ValidationResult.OK, msg)
