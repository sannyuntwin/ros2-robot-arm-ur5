#!/bin/bash
set -e

echo "=== UR5 Simulation Setup ==="
echo "Installing ROS 2 Humble dependencies..."

source /opt/ros/humble/setup.bash

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
