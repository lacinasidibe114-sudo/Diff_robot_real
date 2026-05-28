import rclpy
from rclpy.node import Node 
from std_msgs.msg import String


class SimplePu(Node):
    def __init__(self):
        super().__init__( "simple")


        self.pu = self.create_publisher(String , "test" , 10 ,self.Callback)


    def Callback(self , msg):
        self.get_logger().info(msg.data)



def main():
    rclpy.init()
    simple = SimplePu()
    rclpy.spin(simple)
    simple.destroy_node()
    rclpy.shutdown()
    


if __name__=='__amin__':
    main()