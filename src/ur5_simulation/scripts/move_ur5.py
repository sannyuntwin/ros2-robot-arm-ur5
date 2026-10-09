#!/usr/bin/env python3
"""Demo node: move UR5 to predefined joint poses via MoveIt 2 MoveGroup interface."""

import time
import rclpy
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    JointConstraint,
    Constraints,
)
from rclpy.action import ActionClient


JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

# Predefined poses: name → [shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3]
POSES = {
    # Standard positions
    "home":       [ 0.0,   -1.5708,  0.0,    -1.5708,  0.0,   0.0],   # default ready pose
    "zero":       [ 0.0,    0.0,     0.0,     0.0,      0.0,   0.0],   # all joints at 0 (arm straight up)
    "fold":       [ 0.0,   -3.1416,  2.4,    -0.8,      0.0,   0.0],   # compact folded

    # Reach poses
    "reach_fwd":  [ 0.0,   -1.0,     1.0,    -1.5708,   0.0,   0.0],   # reach forward
    "reach_up":   [ 0.0,   -1.5708, -1.5708, -1.5708,   0.0,   0.0],   # reach upward
    "reach_down": [ 0.0,   -0.5,     1.8,    -2.8,       0.0,   0.0],   # reach downward

    # Side poses
    "side_left":  [ 1.5708, -1.5708,  1.5708, -1.5708, -1.5708, 0.0],  # arm to the left
    "side_right": [-1.5708, -1.5708,  1.5708, -1.5708,  1.5708, 0.0],  # arm to the right

    # Wrist variations (from home)
    "wrist_flip": [ 0.0,   -1.5708,  0.0,    -1.5708,   0.0,   3.1416], # wrist 180° spin
    "carry":      [ 0.0,   -2.0,     2.0,    -1.5708,  -1.5708, 0.0],   # compact carry pose
}


class MoveUR5(Node):
    def __init__(self):
        super().__init__("move_ur5")
        self._client = ActionClient(self, MoveGroup, "/move_action")

    def move_to(self, pose_name: str):
        if pose_name not in POSES:
            self.get_logger().error(f"Unknown pose: {pose_name}. Choose from {list(POSES)}")
            return

        self.get_logger().info(f"Moving to pose: {pose_name}")
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("MoveGroup action server not available — is ur5_moveit.launch.py running?")
            return

        goal = MoveGroup.Goal()
        goal.request = MotionPlanRequest()
        goal.request.group_name = "ur_manipulator"
        goal.request.num_planning_attempts = 10
        goal.request.allowed_planning_time = 5.0
        goal.request.max_velocity_scaling_factor = 0.5
        goal.request.max_acceleration_scaling_factor = 0.5

        constraints = Constraints()
        for name, value in zip(JOINT_NAMES, POSES[pose_name]):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = value
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        goal.request.goal_constraints.append(constraints)

        future = self._client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        result_future = future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info(f"Done: error_code={result_future.result().result.error_code.val}")


def main():
    rclpy.init()
    node = MoveUR5()

    # Give MoveIt time to fully initialize
    node.get_logger().info("Waiting 3s for MoveIt to initialize...")
    time.sleep(3.0)

    sequence = [
        "home",
        "zero",
        "reach_fwd",
        "side_left",
        "side_right",
        "reach_up",
        "reach_down",
        "carry",
        "wrist_flip",
        "fold",
        "home",
    ]

    for pose in sequence:
        node.move_to(pose)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
