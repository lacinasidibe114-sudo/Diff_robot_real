from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    # Chemins
    pkg_description = FindPackageShare('bumperbot_description').find('bumperbot_description')
    pkg_bringup = FindPackageShare('bumperbot_bringup').find('bumperbot_bringup')
    
    urdf_path = os.path.join(pkg_description, 'urdf', 'bumperbot.urdf.xacro')
    controllers_path = os.path.join(pkg_bringup, 'config', 'diff_drive_controller.yaml')
    
    # Traiter le fichier xacro
    robot_description = Command(['xacro ', urdf_path])
    
    return LaunchDescription([
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        
        # ROS2 Control Node
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[{'robot_description': robot_description}, controllers_path],
            output='screen'
        ),
        
        # Spawn Joint State Broadcaster
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 
                 'joint_state_broadcaster'],
            output='screen'
        ),
        
        # Spawn Diff Drive Controller
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 
                 'diff_drive_controller'],
            output='screen'
        ),
    ])