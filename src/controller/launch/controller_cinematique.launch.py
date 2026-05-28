from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    # Déclarer les paramètres modifiables
    wheel_radius_arg = DeclareLaunchArgument(
        'wheel_radius',
        default_value='0.033',
        description='Radius of the wheels in meters'
    )
    
    wheel_separation_arg = DeclareLaunchArgument(
        'wheel_separation',
        default_value='0.17',
        description='Distance between the wheels in meters'
    )

    # Spawner pour le joint state broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    # Spawner pour le simple velocity controller
    simple_velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "simple_velocity_controller", 
            "--controller-manager", 
            "/controller_manager"
        ],
    )

    # Votre nœud personnalisé simple_controller
    simple_controller_node = Node(
        package="controller",
        executable="simple_controller.py",
        name="simple_controller",
        parameters=[{
            "wheel_radius": LaunchConfiguration('wheel_radius'),
            "wheel_separation": LaunchConfiguration('wheel_separation')
        }],
        output="screen"
    )

    return LaunchDescription([
        wheel_radius_arg,
        wheel_separation_arg,
        joint_state_broadcaster_spawner,
        simple_velocity_controller,
        simple_controller_node
    ])