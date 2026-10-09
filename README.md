# UR5 Robot Arm Simulation

ROS 2 Humble simulation of the Universal Robots UR5 6-DOF industrial arm using Gazebo Classic and MoveIt 2.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble

## Quick Start

```bash
git clone <your-repo-url>
cd ros2-robot-arm
chmod +x setup.sh
./setup.sh
```

## Launch

Source the workspace first:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

**Gazebo simulation only:**

```bash
ros2 launch ur5_simulation ur5_gazebo.launch.py
```

**Gazebo + MoveIt 2 (motion planning):**

```bash
ros2 launch ur5_simulation ur5_moveit.launch.py
```

**Send a programmatic joint goal:**

```bash
ros2 run ur5_simulation move_ur5
```

## Package Structure

```
src/ur5_simulation/
├── launch/
│   ├── ur5_gazebo.launch.py    # Gazebo physics simulation
│   └── ur5_moveit.launch.py    # Gazebo + MoveIt 2 planning
├── config/
│   └── controllers.yaml        # ros2_control joint controllers
├── scripts/
│   └── move_ur5.py             # Programmatic joint control demo
└── rviz/
    └── ur5_moveit.rviz         # RViz configuration
```

## UR5 Joints

| Joint | Range |
|-------|-------|
| shoulder_pan_joint | ±360° |
| shoulder_lift_joint | ±360° |
| elbow_joint | ±360° |
| wrist_1_joint | ±360° |
| wrist_2_joint | ±360° |
| wrist_3_joint | ±360° |
