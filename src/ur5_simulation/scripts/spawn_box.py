#!/usr/bin/env python3
"""Spawn a red box in Gazebo at a fixed position in front of the UR5."""

import subprocess
import sys

BOX_SDF = """
<sdf version='1.7'>
  <model name='pick_box'>
    <static>false</static>
    <link name='box_link'>
      <inertial>
        <mass>0.1</mass>
        <inertia><ixx>0.00004</ixx><ixy>0</ixy><ixz>0</ixz>
                 <iyy>0.00004</iyy><iyz>0</iyz><izz>0.00004</izz></inertia>
      </inertial>
      <collision name='collision'>
        <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
      </collision>
      <visual name='visual'>
        <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
        <material>
          <ambient>0.8 0.1 0.1 1</ambient>
          <diffuse>0.8 0.1 0.1 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

PLACE_SDF = """
<sdf version='1.7'>
  <model name='place_marker'>
    <static>true</static>
    <link name='marker_link'>
      <visual name='visual'>
        <geometry><box><size>0.06 0.06 0.002</size></box></geometry>
        <material>
          <ambient>0.1 0.8 0.1 1</ambient>
          <diffuse>0.1 0.8 0.1 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""


def spawn(name, sdf, x, y, z):
    req = f'sdf: "{sdf.strip()}", pose: {{position: {{x: {x}, y: {y}, z: {z}}}}}'
    result = subprocess.run([
        "gz", "service",
        "-s", "/world/default/create",
        "--reqtype", "gz.msgs.EntityFactory",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "3000",
        "--req", req,
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Spawned '{name}' at ({x}, {y}, {z})")
    else:
        print(f"Failed to spawn '{name}': {result.stderr}", file=sys.stderr)


def main():
    # Red box to pick — 50cm in front of the robot
    spawn("pick_box", BOX_SDF, x=0.5, y=0.0, z=0.025)
    # Green marker showing place target — 30cm left
    spawn("place_marker", PLACE_SDF, x=0.3, y=-0.4, z=0.001)


if __name__ == "__main__":
    main()
