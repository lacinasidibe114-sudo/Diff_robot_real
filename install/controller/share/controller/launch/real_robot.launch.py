import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # =================================================================
    # URDF genere par xacro AVEC is_sim:=False
    #   -> le bloc <hardware> utilise bumperbot_firmware/BumperbotInterface
    #   -> aucun plugin Gazebo n'est genere
    # =================================================================
    robot_description = ParameterValue(
        Command([
            "xacro ",
            os.path.join(
                get_package_share_directory("robot_description"),
                "urdf", "robot.urdf.xacro",
            ),
            " is_sim:=False",
        ]),
        value_type=str,
    )

    # --- Robot State Publisher (horloge systeme : use_sim_time=False) ---
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": False}],
        output="screen",
    )

    # =================================================================
    # Controller Manager STANDALONE (le coeur du robot reel).
    # C'est lui qui charge ton plugin BumperbotInterface et ouvre le
    # port serie vers l'Arduino. PAS de Gazebo ici.
    # =================================================================
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_description, "use_sim_time": False},
            os.path.join(
                get_package_share_directory("controller"),
                "config", "bumperbot_controllers_real.yaml",
            ),
        ],
        output="screen",
    )

    # --- Spawners (ils attendent automatiquement le controller_manager) ---
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster",
                   "--controller-manager", "/controller_manager"],
        output="screen",
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller",
                   "--controller-manager", "/controller_manager"],
        output="screen",
    )

    return LaunchDescription([
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
    ])