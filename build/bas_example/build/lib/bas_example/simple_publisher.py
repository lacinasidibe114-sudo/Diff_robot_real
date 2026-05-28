import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    def __init__(self):
        super().__init__("simple_publisher")


        self.pub = self.create_publisher(String , "chatter",10)

        self.count = 0
        self.freq = 1.0 

        self.get_logger().info("pub at %d" % self.freq)

        self.timer = self.create_timer( self.freq , self.Callback)




    def Callback(self):

        msg = String()
        msg.data = "hello lacina _ counter: %d " % self.count
        self.pub.publish(msg) 
        self.count +=1




def main(): 
    rclpy.init()
    simple_publisher =SimplePublisher()
    rclpy.spin(simple_publisher)
    simple_publisher.destroy_node()
    rclpy.shutdown()
    
    

if __name__ == '__main__':
    main()