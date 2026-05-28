#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist
import numpy as np


class SimpleController(Node):

    def __init__(self):
        super().__init__("simple_controller")
        
        # Déclarer les paramètres avec des valeurs par défaut
        self.declare_parameter("wheel_radius", 0.033)
        self.declare_parameter("wheel_separation", 0.17)

        # Récupérer les paramètres CORRECTEMENT
        self.wheel_radius_ = self.get_parameter("wheel_radius").value
        self.wheel_separation_ = self.get_parameter("wheel_separation").value

        self.get_logger().info(f"Using wheel radius: {self.wheel_radius_}")
        self.get_logger().info(f"Using wheel separation: {self.wheel_separation_}")

        # Matrice de conversion inverse
        self.speed_conversion_ = np.array([[self.wheel_radius_/2, self.wheel_radius_/2],
                                           [self.wheel_radius_/self.wheel_separation_, 
                                            -self.wheel_radius_/self.wheel_separation_]])

        self.get_logger().info(f"The conversion matrix is:\n{self.speed_conversion_}")

        # Publishers et Subscribers
        self.wheel_cmd_pub_ = self.create_publisher(Float64MultiArray, "/simple_velocity_controller/commands", 10)
        self.cmd_vel_sub_ = self.create_subscription(Twist, "/cmd_vel", self.velCallback, 10)

        self.get_logger().info("Simple Controller Node has been started and waiting for /cmd_vel messages")

    def velCallback(self, msg):
        # Implements the differential kinematic model
        # Given v and w, calculate the velocities of the wheels
        robot_speed = np.array([[msg.linear.x],
                                [msg.angular.z]])
        
        wheel_speed = np.matmul(np.linalg.inv(self.speed_conversion_), robot_speed)

        wheel_speed_msg = Float64MultiArray()
        # Ordre: [vitesse roue droite, vitesse roue gauche]
        wheel_speed_msg.data = [wheel_speed[1, 0], wheel_speed[0, 0]]

        self.wheel_cmd_pub_.publish(wheel_speed_msg)
        self.get_logger().info(f"cmd_vel received: v={msg.linear.x}, w={msg.angular.z} -> wheel speeds: {wheel_speed_msg.data}")


def main(args=None):
    rclpy.init(args=args)
    simple_controller = SimpleController()
    rclpy.spin(simple_controller)
    simple_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()