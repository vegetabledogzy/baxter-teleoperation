#! /usr/bin/env python3.8

"""
    Python 版 HelloWorld

"""
import rospy
from std_msgs.msg import String
import paho.mqtt.client as mqtt


ros_pub=None
def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
    client.subscribe('plane', qos=0)


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    msg.payload
    ros_pub.publish(msg.payload.decode("utf-8"))


#   订阅回调
def on_subscribe(client, userdata, mid, granted_qos):
    print("On Subscribed: qos = %d" % granted_qos)
    
    pass


#   取消订阅回调
def on_unsubscribe(client, userdata, mid):
    print("On unSubscribed: qos = %d" % mid)
    pass


#   发布消息回调
def on_publish(client, userdata, mid):
    print("On onPublish: qos = %d" % mid)
    pass


#   断开链接回调
def on_disconnect(client, userdata, rc):
    print("Unexpected disconnection rc = " + str(rc))
    pass


def mqtt_ros_bridge():
    global ros_pub
    
    # 初始化ROS节点
    rospy.init_node('mqtt_ros_bridge', anonymous=True)
    
    # 创建ROS发布器
    ros_pub = rospy.Publisher('che', String, queue_size=10)
    
    # 初始化MQTT客户端
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "7ac43bc501d1d99d4f09fe6e6c5ed0f9")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('bemfa.com', 9501, 600)
    
    # 开始MQTT客户端的循环处理
    client.loop_start()
    
    # ROS主循环
    rospy.spin()

# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "7ac43bc501d1d99d4f09fe6e6c5ed0f9")
# client.on_connect = on_connect
# client.on_message = on_message
# client.on_publish = on_publish
# client.on_disconnect = on_disconnect
# client.on_unsubscribe = on_unsubscribe
# client.on_subscribe = on_subscribe
# client.connect('bemfa.com', 9501, 600)   # 600为keepalive的时间间隔
# client.subscribe('plane', qos=0)

if __name__ == '__main__':
    try:
        mqtt_ros_bridge()
    except rospy.ROSInterruptException:
        pass


# rospy.init_node("Hello")
# pub = rospy.Publisher("che",String,queue_size=20)
# rospy.loginfo("Hello World!!!!")
# msg=String()
# msg_front = "hello 你好"
# count = 0  #计数器 
# # 设置循环频率
# rate = rospy.Rate(1)
# while not rospy.is_shutdown():

#     #拼接字符串
#     msg.data = msg_front + str(count)

#     pub.publish(msg)
#     rate.sleep()
#     rospy.loginfo("写出的数据:%s",msg.data)
#     count += 1
# client.loop_forever()  # 保持连接
