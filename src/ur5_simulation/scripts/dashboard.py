#!/usr/bin/env python3
"""
Simple GUI dashboard for UR5 pick-and-place demo.
Shows live joint states, gripper position, detected box location.
Buttons: Open Gripper, Close Gripper, Run Pick & Place, Go Home.
"""

import threading
import subprocess
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import PointStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, JointConstraint, Constraints, RobotState
from rclpy.action import ActionClient

import tkinter as tk
from tkinter import ttk, font


GRIPPER_OPEN  = 0.04
GRIPPER_GRASP = 0.012
JOINT_NAMES = [
    "shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
    "wrist_1_joint",      "wrist_2_joint",       "wrist_3_joint",
]
HOME_POSE = [0.000, -1.5708, 0.000, -1.5708, 0.000, 0.000]


class DashboardNode(Node):
    def __init__(self):
        super().__init__("dashboard")
        self.joint_positions = {}
        self.gripper_pos     = None
        self.detected_box    = None
        self.status_text     = "Ready"

        self._gripper_pub = self.create_publisher(
            Float64MultiArray, "/gripper_controller/commands", 10)
        self._arm = ActionClient(self, MoveGroup, "/move_action")

        self.create_subscription(JointState,   "/joint_states",      self._js_cb,  10)
        self.create_subscription(PointStamped, "/detected_box_pose", self._box_cb, 10)

    def _js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name in JOINT_NAMES:
                self.joint_positions[name] = pos
            if "finger" in name:
                self.gripper_pos = pos

    def _box_cb(self, msg: PointStamped):
        self.detected_box = msg.point

    def send_gripper(self, position: float):
        m = Float64MultiArray()
        m.data = [position, position]
        self._gripper_pub.publish(m)

    def move_home(self):
        self.status_text = "Moving to home..."
        if not self._arm.wait_for_server(timeout_sec=5.0):
            self.status_text = "ERROR: MoveIt not ready"
            return
        goal = MoveGroup.Goal()
        goal.request = MotionPlanRequest()
        goal.request.group_name = "ur_manipulator"
        goal.request.num_planning_attempts = 5
        goal.request.allowed_planning_time = 5.0
        goal.request.start_state = RobotState()
        goal.request.start_state.is_diff = True
        goal.request.max_velocity_scaling_factor = 0.3
        goal.request.max_acceleration_scaling_factor = 0.2

        constraints = Constraints()
        for name, value in zip(JOINT_NAMES, HOME_POSE):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = value
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)
        goal.request.goal_constraints.append(constraints)

        future = self._arm.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if future.result() is None:
            self.status_text = "ERROR: goal rejected"
            return
        result_future = future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=15.0)
        code = result_future.result().result.error_code.val if result_future.result() else -99
        self.status_text = "Home reached" if code == 1 else f"Home failed (code={code})"


class Dashboard:
    def __init__(self, node: DashboardNode):
        self.node = node
        self.root = tk.Tk()
        self.root.title("UR5 Dashboard")
        self.root.geometry("520x620")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        title_font  = font.Font(family="Segoe UI", size=14, weight="bold")
        header_font = font.Font(family="Segoe UI", size=10, weight="bold")
        mono_font   = font.Font(family="Consolas",  size=10)
        btn_font    = font.Font(family="Segoe UI", size=10, weight="bold")

        # ── Title ──────────────────────────────────────────────────────────
        tk.Label(self.root, text="UR5 Robot Dashboard",
                 font=title_font, bg="#1e1e2e", fg="#cdd6f4").pack(pady=(14, 4))

        # ── Status bar ─────────────────────────────────────────────────────
        self._status_var = tk.StringVar(value="Ready")
        status_frame = tk.Frame(self.root, bg="#313244", bd=0)
        status_frame.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(status_frame, textvariable=self._status_var,
                 font=mono_font, bg="#313244", fg="#a6e3a1",
                 anchor="w", padx=8, pady=4).pack(fill="x")

        # ── Joint states ───────────────────────────────────────────────────
        jf = tk.LabelFrame(self.root, text=" Joint Positions (rad) ",
                           font=header_font, bg="#1e1e2e", fg="#89b4fa",
                           bd=1, relief="groove")
        jf.pack(fill="x", padx=14, pady=4)

        self._joint_labels = {}
        cols = [("shoulder_pan", 0), ("shoulder_lift", 1), ("elbow", 2),
                ("wrist_1",      3), ("wrist_2",       4), ("wrist_3", 5)]
        for r, (short, _) in enumerate(cols):
            row = tk.Frame(jf, bg="#1e1e2e")
            row.pack(fill="x", padx=8, pady=1)
            tk.Label(row, text=f"{short}:", width=16, anchor="w",
                     font=mono_font, bg="#1e1e2e", fg="#cdd6f4").pack(side="left")
            var = tk.StringVar(value="—")
            tk.Label(row, textvariable=var, width=10, anchor="e",
                     font=mono_font, bg="#1e1e2e", fg="#f9e2af").pack(side="left")
            self._joint_labels[JOINT_NAMES[r]] = var

        # ── Gripper & box ──────────────────────────────────────────────────
        info_frame = tk.Frame(self.root, bg="#1e1e2e")
        info_frame.pack(fill="x", padx=14, pady=6)

        gf = tk.LabelFrame(info_frame, text=" Gripper ",
                           font=header_font, bg="#1e1e2e", fg="#89b4fa",
                           bd=1, relief="groove", width=230)
        gf.pack(side="left", fill="both", expand=True, padx=(0, 6))
        gf.pack_propagate(False)
        self._gripper_var = tk.StringVar(value="—")
        tk.Label(gf, textvariable=self._gripper_var,
                 font=mono_font, bg="#1e1e2e", fg="#f9e2af").pack(pady=8)

        bf = tk.LabelFrame(info_frame, text=" Detected Box ",
                           font=header_font, bg="#1e1e2e", fg="#89b4fa",
                           bd=1, relief="groove")
        bf.pack(side="left", fill="both", expand=True)
        self._box_var = tk.StringVar(value="Not detected")
        tk.Label(bf, textvariable=self._box_var,
                 font=mono_font, bg="#1e1e2e", fg="#a6e3a1",
                 justify="left", padx=8).pack(pady=8, anchor="w")

        # ── Buttons ────────────────────────────────────────────────────────
        btn_frame = tk.LabelFrame(self.root, text=" Controls ",
                                  font=header_font, bg="#1e1e2e", fg="#89b4fa",
                                  bd=1, relief="groove")
        btn_frame.pack(fill="x", padx=14, pady=8)

        def make_btn(parent, text, color, cmd):
            b = tk.Button(parent, text=text, font=btn_font,
                          bg=color, fg="#1e1e2e", activebackground="#cdd6f4",
                          relief="flat", bd=0, padx=14, pady=8,
                          command=cmd, cursor="hand2")
            b.pack(side="left", expand=True, fill="x", padx=4, pady=8)
            return b

        row1 = tk.Frame(btn_frame, bg="#1e1e2e")
        row1.pack(fill="x")
        make_btn(row1, "Open Gripper",  "#89dceb", self._open_gripper)
        make_btn(row1, "Close Gripper", "#fab387", self._close_gripper)

        row2 = tk.Frame(btn_frame, bg="#1e1e2e")
        row2.pack(fill="x")
        make_btn(row2, "Go Home",       "#a6e3a1", self._go_home)
        make_btn(row2, "Run Pick & Place", "#cba6f7", self._run_pick_place)

        # ── Log ────────────────────────────────────────────────────────────
        lf = tk.LabelFrame(self.root, text=" Log ",
                           font=header_font, bg="#1e1e2e", fg="#89b4fa",
                           bd=1, relief="groove")
        lf.pack(fill="both", expand=True, padx=14, pady=(4, 14))
        self._log = tk.Text(lf, height=6, bg="#181825", fg="#cdd6f4",
                            font=mono_font, relief="flat", state="disabled",
                            wrap="word")
        self._log.pack(fill="both", expand=True, padx=4, pady=4)

        self.root.after(200, self._poll)

    # ── Button handlers ────────────────────────────────────────────────────

    def _open_gripper(self):
        self._log_msg("Opening gripper...")
        threading.Thread(target=self.node.send_gripper,
                         args=(GRIPPER_OPEN,), daemon=True).start()

    def _close_gripper(self):
        self._log_msg("Closing gripper (grasp)...")
        threading.Thread(target=self.node.send_gripper,
                         args=(GRIPPER_GRASP,), daemon=True).start()

    def _go_home(self):
        self._log_msg("Sending arm to home pose...")
        threading.Thread(target=self.node.move_home, daemon=True).start()

    def _run_pick_place(self):
        self._log_msg("Launching pick_place node...")
        def run():
            proc = subprocess.Popen(
                ["ros2", "run", "ur5_simulation", "pick_place"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self._log_msg(line.rstrip())
        threading.Thread(target=run, daemon=True).start()

    # ── Poll / update ──────────────────────────────────────────────────────

    def _poll(self):
        # Spin ROS briefly to process callbacks
        rclpy.spin_once(self.node, timeout_sec=0.05)

        # Joint labels
        for name, var in self._joint_labels.items():
            pos = self.node.joint_positions.get(name)
            var.set(f"{pos:.4f}" if pos is not None else "—")

        # Gripper
        gp = self.node.gripper_pos
        if gp is not None:
            gap_mm = int((gp * 2) * 1000)
            self._gripper_var.set(f"{gp:.4f} m  ({gap_mm} mm gap)")
        else:
            self._gripper_var.set("—")

        # Box
        b = self.node.detected_box
        if b is not None:
            self._box_var.set(f"x: {b.x:.3f} m\ny: {b.y:.3f} m\nz: {b.z:.3f} m")
        else:
            self._box_var.set("Not detected")

        # Status
        self._status_var.set(self.node.status_text)

        self.root.after(200, self._poll)

    def _log_msg(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def run(self):
        self.root.mainloop()


def main():
    rclpy.init()
    node = DashboardNode()
    app = Dashboard(node)
    app.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
