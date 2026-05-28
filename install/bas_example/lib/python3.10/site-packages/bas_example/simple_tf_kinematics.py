import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster  # Changé: TransformBroadcaster pour dynamique
from geometry_msgs.msg import TransformStamped

class SimpleTfKinematics(Node):
    def __init__(self):
        super().__init__("simple_tf_kinematics")

        # Broadcaster pour transformations statiques et dynamiques
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.dynamic_tf_broadcaster = TransformBroadcaster(self)  # CORRECTION 1: TransformBroadcaster, pas StaticTransformBroadcaster

        self.static_transform_stamped = TransformStamped()
        self.dynamic_transform_stamped = TransformStamped()  # CORRECTION 2: À utiliser pour la dynamique

        # Variable pour incrémenter la position x
        self.x_increment = 0.05  # Correction: x_incre -> x_increment
        self.last_x = 0.0 

        # === TRANSFORMATION STATIQUE ===
        self.static_transform_stamped.header.stamp = self.get_clock().now().to_msg()
        self.static_transform_stamped.header.frame_id = "bumperbot_base"
        self.static_transform_stamped.child_frame_id = "bumperbot_top"
        self.static_transform_stamped.transform.translation.x = 0.0
        self.static_transform_stamped.transform.translation.y = 0.0
        self.static_transform_stamped.transform.translation.z = 0.3
        self.static_transform_stamped.transform.rotation.x = 0.0
        self.static_transform_stamped.transform.rotation.y = 0.0
        self.static_transform_stamped.transform.rotation.z = 0.0
        self.static_transform_stamped.transform.rotation.w = 1.0

        # Publication de la transformation statique
        self.static_tf_broadcaster.sendTransform(self.static_transform_stamped)
        
        self.get_logger().info("Publishing static transform between %s and %s" % (
            self.static_transform_stamped.header.frame_id,
            self.static_transform_stamped.child_frame_id
        ))

        # Timer pour les transformations dynamiques (10 Hz)
        self.timer = self.create_timer(0.1, self.timer_callback)  # Correction: TimerCallback -> timer_callback

    def timer_callback(self):  # Correction: nom de méthode en snake_case
        # === TRANSFORMATION DYNAMIQUE ===
        self.dynamic_transform_stamped.header.stamp = self.get_clock().now().to_msg()  # CORRECTION 3: utiliser dynamic_transform_stamped
        self.dynamic_transform_stamped.header.frame_id = "odom"  # CORRECTION 4: frame_id correct
        self.dynamic_transform_stamped.child_frame_id = "bumperbot_base"
        
        # Incrémentation de la position x
        new_x = self.last_x + self.x_increment
        self.dynamic_transform_stamped.transform.translation.x = new_x
        self.dynamic_transform_stamped.transform.translation.y = 0.0
        self.dynamic_transform_stamped.transform.translation.z = 0.0
        self.dynamic_transform_stamped.transform.rotation.x = 0.0
        self.dynamic_transform_stamped.transform.rotation.y = 0.0
        self.dynamic_transform_stamped.transform.rotation.z = 0.0
        self.dynamic_transform_stamped.transform.rotation.w = 1.0

        # Publication de la transformation dynamique
        self.dynamic_tf_broadcaster.sendTransform(self.dynamic_transform_stamped)  # CORRECTION 5: envoyer dynamic_transform_stamped

        # Mise à jour de last_x
        self.last_x = new_x  # CORRECTION 6: utiliser new_x

        # Log optionnel (toutes les 10 itérations pour éviter le spam)
        self.get_logger().debug(f"Dynamic transform: x = {new_x:.2f}")

def main(): 
    rclpy.init()
    simple_tf_kinematics = SimpleTfKinematics()
    rclpy.spin(simple_tf_kinematics)
    simple_tf_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()