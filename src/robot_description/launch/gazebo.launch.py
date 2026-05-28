import os
from os import pathsep
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # --- Chemins des packages ---
    robot_description_pkg = get_package_share_directory("robot_description")
    ros_gz_sim_pkg = get_package_share_directory("ros_gz_sim")
    controller_pkg = get_package_share_directory("controller")

    # --- Argument modele ---
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(robot_description_pkg, "urdf", "robot.urdf.xacro"),
        description="Chemin absolu vers le fichier URDF du robot",
    )

    # --- Chemins de ressources pour Gazebo Fortress (meshes) ---
    model_path = str(Path(robot_description_pkg).parent.resolve())
    model_path += pathsep + os.path.join(robot_description_pkg, "meshes")
    gazebo_resource_path = SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", model_path)

    # --- Robot description (xacro -> URDF) ---
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str,
    )

    # --- Robot State Publisher ---
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        output="screen",
    )

    # --- Gazebo Fortress ---
    # gz_sim.launch.py + 'gz_args' : syntaxe correcte pour Humble/Fortress (0.244.x)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    # --- Spawn du robot depuis le topic /robot_description ---
    gz_spawn_entity = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                output="screen",
                arguments=["-topic", "robot_description", "-name", "bumperbot"],
            )
        ],
    )

    # --- Bridge /clock : Gazebo -> ROS ---
    # INDISPENSABLE pour que use_sim_time fonctionne cote ROS.
    # '[' = direction Gazebo vers ROS. 'ignition.msgs.Clock' = type Fortress
    # (ce serait 'gz.msgs.Clock' a partir de Garden).
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock"],
        output="screen",
    )

    # --- Joint State Broadcaster ---
    joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "joint_state_broadcaster",
                    "--param-file",
                    os.path.join(controller_pkg, "config", "bumperbot_controllers.yaml"),
                ],
                output="screen",
            )
        ],
    )

    # --- Diff Drive Controller ---
    diff_drive_controller = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "diff_drive_controller",
                    "--param-file",
                    os.path.join(controller_pkg, "config", "bumperbot_controllers.yaml"),
                ],
                output="screen",
            )
        ],
    )

    # NOTE : le bridge /cmd_vel d'origine a ete RETIRE.
    # Avec diff_drive_controller (ros2_control), c'est le controleur qui pilote
    # directement les roues via le plugin ign_ros2_control : aucun bridge cmd_vel
    # vers Gazebo n'est necessaire. Pour conduire le robot, publie un Twist sur le
    # topic du controleur (voir les notes accompagnant ce fichier).

    return LaunchDescription([
        model_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        clock_bridge,
        gz_spawn_entity,
        joint_state_broadcaster,
        diff_drive_controller,
    ])