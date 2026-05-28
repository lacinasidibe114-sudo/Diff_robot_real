import os
from os import pathsep
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Package paths
    robot_description_pkg = get_package_share_directory("robot_description")
    ros_gz_sim_pkg = get_package_share_directory("ros_gz_sim")

    # Arguments
    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value=os.path.join(robot_description_pkg, "urdf", "robot.urdf.xacro"),
        description="Absolute path to robot urdf file"
    )

    world_arg = DeclareLaunchArgument(
        name="world", 
        default_value="empty.sdf",
        description="Gazebo world file"
    )

    # Configuration des chemins pour les meshes
    model_path = str(Path(robot_description_pkg).parent.resolve())
    model_path += pathsep + os.path.join(robot_description_pkg, 'meshes')

    gazebo_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        model_path
    )

    # Robot description
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        output="screen"
    )

    # IMPORTANT: Charger ros2_control via un nœud séparé
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        output="screen"
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": ["-r ", LaunchConfiguration("world")],
            "on_exit_shutdown": "true"
        }.items(),
    )

    # Spawn robot
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description", "-name", "bumperbot", 
                   "-x", "0", "-y", "0", "-z", "0.1"],
    )

    return LaunchDescription([
        model_arg,
        world_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        ros2_control_node,  # AJOUTER CETTE LIGNE
        gazebo,
        gz_spawn_entity,
    ])