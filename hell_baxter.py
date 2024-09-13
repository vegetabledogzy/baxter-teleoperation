#!/usr/bin/python
# Import the necessary Python modules
# rospy - ROS Python API
import rospy
# baxter_interface - Baxter Python API
import baxter_interface
from std_msgs.msg import String
from ik_service_client import ik_test
import ast
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)

def get_cartesian_coordinates(limb):
    endpoint_pose = limb.endpoint_pose()
    position = endpoint_pose['position']
    orientation = endpoint_pose['orientation']
    return position, orientation

# initialize our ROS node, registering it with the Master
rospy.init_node('Hello_Baxter')
# create an instance of baxter_interface's Limb class

limb = baxter_interface.Limb('right')
callback_flag=0
xyz=[]
wave_1 = {'right_s0': -0.395, 'right_s1': -0.202, 'right_e0': 1.831, 'right_e1': 1.981, 'right_w0': 
-0, 'right_w1': -1.100, 'right_w2': -0.448}
limb.move_to_joint_positions(wave_1)
def callback(msg,limb):
    global callback_flag
    global xyz
    if callback_flag == 0:
        xyz=ast.literal_eval(msg.data)
        callback_flag=1
    else:
        position11=[1,1,1]
        last_xyz=xyz
        xyz=ast.literal_eval(msg.data)
        vec=[xyz[0]-last_xyz[0],xyz[1]-last_xyz[1],xyz[2]-last_xyz[2]]
        position, orientation=get_cartesian_coordinates(limb)
        position11[0]=(-vec[2])+(position.x)
        position11[1]=(vec[0])+(position.y)
        position11[2]=(-vec[1])+(position.z)
        print(position11[1],position11[2])
        limb.move_to_joint_positions(ik_test('right',position11,orientation))

rospy.Subscriber('che', String, callback,callback_args=(limb))

# get the right limb's current joint angles
# angles = limb.joint_angles()


# print the joint angle command
# limb.move_to_joint_positions(angles)

# print angles
# move the right arm to those joint angles
# print(ik_test('right'))
# limb.move_to_joint_positions(ik_test('right'))
# # Baxter wants to say hello, let's wave the arm
# # store the first wave position 

rospy.spin()
# # store the second wave position
# wave_2 = {'right_s0': -0.395, 'right_s1': -0.202, 'right_e0': 1.831, 'right_e1': 1.981, 'right_w0': 
# -1.979, 'right_w1': -1.100, 'right_w2': -0.448}
# # wave three times
# for _move in range(3):

#  limb.move_to_joint_positions(wave_2)
# quit
# quit()