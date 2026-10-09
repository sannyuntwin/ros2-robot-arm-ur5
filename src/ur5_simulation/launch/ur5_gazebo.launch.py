"""Launch UR5 in Gazebo Classic with ros2_control joint trajectory controller."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")
    launch_rviz = LaunchConfiguration("launch_rviz")

    ur_simulation_gz = FindPackageShare("ur_simulation_gz")

    return LaunchDescription([
        DeclareLaunchArgument(
            "ur_type",
            default_value="ur5",
            description="Type of UR robot: ur3, ur3e, ur5, ur5e, ur10, ur10e, ur16e",
        ),
        DeclareLaunchArgument(
            "launch_rviz",
            default_value="true",
            description="Launch RViz alongside Gazebo",
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [ur_simulation_gz, "/launch/ur_sim_control.launch.py"]
            ),
            launch_arguments={
                "ur_type": ur_type,
                "launch_rviz": launch_rviz,
            }.items(),
        ),
    ])
