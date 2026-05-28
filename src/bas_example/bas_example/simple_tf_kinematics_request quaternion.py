import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster, TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import TransformStamped
from robot_msgs.srv import GetTransform
from tf_transformations import quaternion_from_euler, quaternion_multiply, quaternion_inverse

class SimpleTfKinematicsRequest(Node):
    def __init__(self):
        super().__init__("simple_tf_kinematics_request")

        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.dynamic_tf_broadcaster = TransformBroadcaster(self)

        self.static_transform_stamped = TransformStamped()
        self.dynamic_transform_stamped = TransformStamped()

        self.x_increment = 0.05
        self.last_x = 0.0

        # Rotation
        self.rotations_counter = 0   # entier
        self.last_rotation = quaternion_from_euler(0, 0, 0)
        self.orientation_increment = quaternion_from_euler(0, 0, 0.05)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Static transform
        self.static_transform_stamped.header.stamp = self.get_clock().now().to_msg()
        self.static_transform_stamped.header.frame_id = "bumperbot_base"
        self.static_transform_stamped.child_frame_id = "bumperbot_top"
        self.static_transform_stamped.transform.translation.x = 0.0
        self.static_transform_stamped.transform.translation.y = 0.0
        self.static_transform_stamped.transform.translation.z = 0.3
        #self.static_transform_stamped.transform.rotation.x = 0.0
        #self.static_transform_stamped.transform.rotation.y = 0.0
        #self.static_transform_stamped.transform.rotation.z = 0.0
        #self.static_transform_stamped.transform.rotation.w = 1.0

        self.static_tf_broadcaster.sendTransform(self.static_transform_stamped)
        self.get_logger().info(f"Static transform: {self.static_transform_stamped.header.frame_id} -> {self.static_transform_stamped.child_frame_id}")

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_transform_srv = self.create_service(GetTransform, "get_transform", self.getTransformCallback)

    def timer_callback(self):
        self.dynamic_transform_stamped.header.stamp = self.get_clock().now().to_msg()
        self.dynamic_transform_stamped.header.frame_id = "odom"
        self.dynamic_transform_stamped.child_frame_id = "bumperbot_base"

        # Translation
        new_x = self.last_x + self.x_increment
        self.dynamic_transform_stamped.transform.translation.x = new_x
        self.dynamic_transform_stamped.transform.translation.y = 0.0
        self.dynamic_transform_stamped.transform.translation.z = 0.0

        # Rotation
        q = quaternion_multiply(self.last_rotation, self.orientation_increment)
        self.dynamic_transform_stamped.transform.rotation.x = q[0]
        self.dynamic_transform_stamped.transform.rotation.y = q[1]
        self.dynamic_transform_stamped.transform.rotation.z = q[2]
        self.dynamic_transform_stamped.transform.rotation.w = q[3]

        self.dynamic_tf_broadcaster.sendTransform(self.dynamic_transform_stamped)

        # Mise à jour des états
        self.last_rotation = q
        self.last_x = new_x

        # Inverser le sens de rotation toutes les 100 itérations (10 secondes)
        self.rotations_counter += 1
        if self.rotations_counter >= 100:
            self.orientation_increment = quaternion_inverse(self.orientation_increment)
            self.rotations_counter = 0

        self.get_logger().debug(f"Dynamic transform: x={new_x:.2f}")

    def getTransformCallback(self, req, res):
        self.get_logger().info(f"Request transform from {req.frame_id} to {req.child_frame_id}")
        try:
            requested_transform = self.tf_buffer.lookup_transform(
                req.frame_id, req.child_frame_id, rclpy.time.Time())
        except TransformException as e:
            self.get_logger().error(f"Transform error: {e}")
            res.success = False
            return res
        res.transform = requested_transform
        res.success = True
        return res

def main():
    rclpy.init()
    node = SimpleTfKinematicsRequest()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()