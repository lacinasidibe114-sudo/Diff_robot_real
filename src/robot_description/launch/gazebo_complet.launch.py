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
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # --- Chemins des packages ---
    robot_description_pkg = get_package_share_directory("robot_description")
    ros_gz_sim_pkg = get_package_share_directory("ros_gz_sim")
    controller_pkg = get_package_share_directory("controller")

    # --- Arguments ---
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(robot_description_pkg, "urdf", "robot.urdf.xacro"),
        description="Chemin absolu vers le fichier URDF du robot",
    )

    use_teleop_arg = DeclareLaunchArgument(
        name="use_teleop",
        default_value="true",
        description="Ouvrir un terminal de teleop clavier (true/false)",
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

    # --- Bridge /clock : Gazebo -> ROS (indispensable pour use_sim_time) ---
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

    # --- Teleop clavier ---
    # teleop_twist_keyboard lit le clavier sur stdin : il DOIT tourner dans son
    # propre terminal, sinon il ne capte aucune touche. On l'ouvre donc via
    # 'xterm -e'  (paquet xterm requis : sudo apt install xterm).
    # Remap : /cmd_vel (defaut du teleop) -> topic ecoute par diff_drive_controller.
    # Demarre a 12s, apres le controleur, pour que la cible existe deja.
    # Desactivable avec :  ros2 launch ... use_teleop:=false
    teleop_node = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="teleop_twist_keyboard",
                executable="teleop_twist_keyboard",
                name="teleop_twist_keyboard",
                prefix="xterm -e",
                remappings=[("/cmd_vel", "/diff_drive_controller/cmd_vel_unstamped")],
                output="screen",
                condition=IfCondition(LaunchConfiguration("use_teleop")),
            )
        ],
    )

    return LaunchDescription([
        model_arg,
        use_teleop_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        clock_bridge,
        gz_spawn_entity,
        joint_state_broadcaster,
        diff_drive_controller,
        teleop_node,
    ])