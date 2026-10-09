"""Launch UR5 in Gazebo with MoveIt 2 motion planning."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")

    ur_simulation_gazebo = FindPackageShare("ur_simulation_gazebo")

    return LaunchDescription([
        DeclareLaunchArgument(
            "ur_type",
            default_value="ur5",
            description="Type of UR robot: ur3, ur3e, ur5, ur5e, ur10, ur10e, ur16e",
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [ur_simulation_gazebo, "/launch/ur_sim_moveit.launch.py"]
            ),
            launch_arguments={
                "ur_type": ur_type,
            }.items(),
        ),
    ])
