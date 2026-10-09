"""Launch UR5 with gripper in Gazebo with MoveIt 2."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")

    ur5_pkg = FindPackageShare("ur5_simulation")
    ur_sim_gz = FindPackageShare("ur_simulation_gz")

    return LaunchDescription([
        DeclareLaunchArgument(
            "ur_type",
            default_value="ur5",
            description="Type of UR robot: ur3, ur5, ur10, ur5e, ...",
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [ur_sim_gz, "/launch/ur_sim_moveit.launch.py"]
            ),
            launch_arguments={
                "ur_type": ur_type,
                "description_file": PathJoinSubstitution(
                    [ur5_pkg, "urdf", "ur5_with_gripper.urdf.xacro"]
                ),
                "controllers_file": PathJoinSubstitution(
                    [ur5_pkg, "config", "ur_controllers_gripper.yaml"]
                ),
            }.items(),
        ),
        # Spawn the gripper controller after controller_manager is ready
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "gripper_controller",
                "--controller-manager", "/controller_manager",
                "--controller-manager-timeout", "30",
            ],
            output="screen",
        ),
    ])
