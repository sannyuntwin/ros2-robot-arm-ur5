#!/bin/bash
set -e

echo "=== UR5 Simulation Setup ==="

# Detect ROS distro based on Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs)
if [[ "$UBUNTU_VERSION" == "22.04" ]]; then
    ROS_DISTRO="humble"
elif [[ "$UBUNTU_VERSION" == "24.04" ]]; then
    ROS_DISTRO="jazzy"
else
    echo "Unsupported Ubuntu version: $UBUNTU_VERSION"
    exit 1
fi

echo "Detected Ubuntu $UBUNTU_VERSION → using ROS 2 $ROS_DISTRO"
source /opt/ros/$ROS_DISTRO/setup.bash

sudo apt update && sudo apt install -y \
    ros-$ROS_DISTRO-ur \
    ros-$ROS_DISTRO-ur-simulation-gazebo \
    ros-$ROS_DISTRO-moveit \
    ros-$ROS_DISTRO-ros2-control \
    ros-$ROS_DISTRO-ros2-controllers \
    ros-$ROS_DISTRO-joint-state-publisher-gui \
    ros-$ROS_DISTRO-xacro \
    ros-$ROS_DISTRO-rviz2

echo ""
echo "=== Building workspace ==="
cd "$(dirname "$0")"
colcon build --symlink-install

echo ""
echo "=== Done! ==="
echo "Source the workspace:"
echo "  source install/setup.bash"
echo ""
echo "Launch Gazebo simulation:"
echo "  ros2 launch ur5_simulation ur5_gazebo.launch.py"
echo ""
echo "Launch with MoveIt 2:"
echo "  ros2 launch ur5_simulation ur5_moveit.launch.py"
