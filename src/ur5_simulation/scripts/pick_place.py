#!/usr/bin/env python3
"""
Pick and place demo for UR5 with simple parallel-jaw gripper.
Moves the arm through approach → pick → lift → transport → place → retreat.

Box spawned at: (0.5, 0.0, 0.025)  — run spawn_box.py first
Place target:   (0.3, -0.4, 0.025)
"""

import time
import rclpy
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, JointConstraint, Constraints, RobotState
from std_msgs.msg import Float64MultiArray
from rclpy.action import ActionClient


JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

POSES = {
    #                   pan     lift     elbow   wrist1   wrist2   wrist3
    "home":         [ 0.000, -1.5708,  0.000, -1.5708,  0.000,  0.000],
    "pre_pick":     [ 0.000, -1.200,   1.600, -2.000,  -1.5708,  0.000],
    "pick":         [ 0.000, -1.050,   1.850, -2.400,  -1.5708,  0.000],
    "lift":         [ 0.000, -1.200,   1.400, -1.800,  -1.5708,  0.000],
    "transport":    [-0.900, -1.200,   1.400, -1.800,  -1.5708,  0.000],
    "pre_place":    [-0.900, -1.200,   1.600, -2.000,  -1.5708,  0.000],
    "place":        [-0.900, -1.050,   1.850, -2.400,  -1.5708,  0.000],
    "retreat":      [-0.900, -1.200,   1.400, -1.800,  -1.5708,  0.000],
}

SEQUENCE = [
    "home",
    "pre_pick",
    "pick",
    "lift",
    "transport",
    "pre_place",
    "place",
    "retreat",
    "home",
]

GRIPPER_OPEN   = 0.04   # fingers fully open (110 mm gap)
GRIPPER_GRASP  = 0.012  # fingers around 5 cm box (~54 mm gap)


class PickPlace(Node):
    def __init__(self):
        super().__init__("pick_place")
        self._arm = ActionClient(self, MoveGroup, "/move_action")
        self._gripper_pub = self.create_publisher(
            Float64MultiArray, "/gripper_controller/commands", 10)

    def move_to(self, pose_name: str, slow: bool = False) -> bool:
        self.get_logger().info(f"→ {pose_name}")

        if not self._arm.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("MoveGroup action server not available")
            return False

        goal = MoveGroup.Goal()
        goal.request = MotionPlanRequest()
        goal.request.group_name = "ur_manipulator"
        goal.request.num_planning_attempts = 10
        goal.request.allowed_planning_time = 5.0
        goal.request.start_state = RobotState()
        goal.request.start_state.is_diff = True
        goal.request.max_velocity_scaling_factor = 0.2 if slow else 0.4
        goal.request.max_acceleration_scaling_factor = 0.1 if slow else 0.3

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

        future = self._arm.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        result_future = future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        code = result_future.result().result.error_code.val
        if code == 1:
            self.get_logger().info(f"  ✓ reached {pose_name}")
            return True
        else:
            self.get_logger().warn(f"  ✗ failed at {pose_name} (error_code={code})")
            return False

    def gripper(self, position: float):
        msg = Float64MultiArray()
        msg.data = [position, position]  # left and right fingers
        self._gripper_pub.publish(msg)
        time.sleep(1.0)


def main():
    rclpy.init()
    node = PickPlace()

    node.get_logger().info("Waiting 5s for MoveIt to initialize...")
    time.sleep(5.0)

    node.get_logger().info("=== Pick and Place Demo ===")
    node.get_logger().info("Make sure spawn_box.py was run first!")

    node.get_logger().info("Opening gripper...")
    node.gripper(GRIPPER_OPEN)

    for pose in SEQUENCE:
        slow = pose in ("pick", "place", "pre_pick", "pre_place")

        # Open gripper before approaching the box
        if pose == "pre_pick":
            node.get_logger().info("  [OPEN] gripper")
            node.gripper(GRIPPER_OPEN)

        ok = node.move_to(pose, slow=slow)

        if pose == "pick":
            node.get_logger().info("  [GRASP] closing gripper")
            node.gripper(GRIPPER_GRASP)
            time.sleep(0.5)
        elif pose == "place":
            node.get_logger().info("  [RELEASE] opening gripper")
            node.gripper(GRIPPER_OPEN)
            time.sleep(0.5)

        if not ok:
            node.get_logger().error(f"Stopping at {pose}")
            break

    rclpy.shutdown()


if __name__ == "__main__":
    main()
