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

if [[ "$ROS_DISTRO" == "humble" ]]; then
    sudo apt update && sudo apt install -y \
        ros-humble-ur \
        ros-humble-ur-simulation-gazebo \
        ros-humble-moveit \
        ros-humble-ros2-control \
        ros-humble-ros2-controllers \
        ros-humble-gazebo-ros-pkgs \
        ros-humble-gazebo-ros2-control \
        ros-humble-joint-state-publisher-gui \
        ros-humble-xacro \
        ros-humble-rviz2
else
    sudo apt update && sudo apt install -y \
        ros-jazzy-ur \
        ros-jazzy-ur-simulation-gz \
        ros-jazzy-moveit \
        ros-jazzy-ros2-control \
        ros-jazzy-ros2-controllers \
        ros-jazzy-gz-ros2-control \
        ros-jazzy-joint-state-publisher-gui \
        ros-jazzy-xacro \
        ros-jazzy-rviz2
fi

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
