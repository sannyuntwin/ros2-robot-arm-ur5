#!/usr/bin/env python3
"""Demo node: move UR5 to predefined joint poses via MoveIt 2 MoveGroup interface."""

import rclpy
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    JointConstraint,
    Constraints,
    WorkspaceParameters,
)
from rclpy.action import ActionClient
from builtin_interfaces.msg import Duration


JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

# Predefined poses: (name, [j1..j6] in radians)
POSES = {
    "home":   [0.0,  -1.5708, 0.0, -1.5708, 0.0, 0.0],
    "up":     [0.0,  -1.5708, -1.5708, -1.5708, 0.0, 0.0],
    "reach":  [0.0,  -1.0,    1.0,  -1.5708, 0.0, 0.0],
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
        self._client.wait_for_server()

        goal = MoveGroup.Goal()
        goal.request = MotionPlanRequest()
        goal.request.group_name = "manipulator"
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

    for pose in ["home", "up", "reach", "home"]:
        node.move_to(pose)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
