#!/usr/bin/env python3
"""
Detects box position using the overhead depth camera.
Subscribes to /overhead_camera/points (PointCloud2), transforms to world frame,
filters by height and workspace bounds, and publishes the centroid to /detected_box_pose.
"""

import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PointStamped
import sensor_msgs_py.point_cloud2 as pc2
import tf2_ros
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud


class BoxDetector(Node):
    def __init__(self):
        super().__init__("box_detector")
        self._tf_buffer = tf2_ros.Buffer()
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self)
        self._pub = self.create_publisher(PointStamped, "/detected_box_pose", 10)
        self._sub = self.create_subscription(
            PointCloud2, "/overhead_camera/points", self._cloud_callback, 10)
        self.get_logger().info("Box detector started — waiting for point clouds...")

    def _cloud_callback(self, msg: PointCloud2):
        # Transform cloud from camera frame to world frame
        try:
            transform = self._tf_buffer.lookup_transform(
                "world", msg.header.frame_id, rclpy.time.Time())
        except tf2_ros.LookupException as e:
            self.get_logger().warn(f"TF not ready: {e}", throttle_duration_sec=5.0)
            return

        world_cloud = do_transform_cloud(msg, transform)

        # Read all valid (non-NaN) xyz points
        points = np.array([
            [p[0], p[1], p[2]]
            for p in pc2.read_points(
                world_cloud, field_names=("x", "y", "z"), skip_nans=True)
        ], dtype=np.float32)

        if len(points) == 0:
            return

        # Filter by height: box is ~0.05 m tall sitting at z=0
        z_mask = (points[:, 2] > 0.01) & (points[:, 2] < 0.08)
        # Filter by workspace bounds
        x_mask = (points[:, 0] > 0.2) & (points[:, 0] < 0.8)
        y_mask = (points[:, 1] > -0.4) & (points[:, 1] < 0.4)
        filtered = points[z_mask & x_mask & y_mask]

        if len(filtered) < 20:
            return

        centroid = filtered.mean(axis=0)

        out = PointStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = "world"
        out.point.x = float(centroid[0])
        out.point.y = float(centroid[1])
        out.point.z = float(centroid[2])
        self._pub.publish(out)
        self.get_logger().info(
            f"Box detected at ({centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f})",
            throttle_duration_sec=2.0)


def main():
    rclpy.init()
    node = BoxDetector()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
