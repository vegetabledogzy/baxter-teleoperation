from openni import openni2
import numpy as np
import cv2
import mediapipe as mp
import math
import paho.mqtt.client as mqtt




def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


#   订阅回调
def on_subscribe(client, userdata, mid, granted_qos):
    print("On Subscribed: qos = %d" % granted_qos)
    pass


#   取消订阅回调
def on_unsubscribe(client, userdata, mid, granted_qos):
    print("On unSubscribed: qos = %d" % granted_qos)
    pass
#   发布消息回调
def on_publish(client, userdata, mid):
    print("On onPublish: qos = %d" % mid)
    pass


#   断开链接回调
def on_disconnect(client, userdata, rc):
    print("Unexpected disconnection rc = " + str(rc))
    pass
client = mqtt.Client("7ac43bc501d1d99d4f09fe6e6c5ed0f9")
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_disconnect = on_disconnect
client.on_unsubscribe = on_unsubscribe
client.on_subscribe = on_subscribe
client.connect('bemfa.com', 9501, 600)  # 600为keepalive的时间间隔





if __name__ == "__main__": 
    openni2.initialize()

    dev = openni2.Device.open_any()
    print(dev.get_device_info())

    depth_stream = dev.create_depth_stream()
    depth_stream.start()

    cap = cv2.VideoCapture(0)
    cv2.namedWindow('depth')

    
    color_stream = dev.create_color_stream()
    color_stream.start()
    cv2.namedWindow('color')
    mp_pose=mp.solutions.pose
    mp_drawing=mp.solutions.drawing_utils
    pose=mp_pose.Pose(static_image_mode=True,#选择静态图片还是连续视频帧
                    model_complexity=2,#选择人体姿态关键点检测模型，0性能差但快，2性能好但慢，1介于之间
                    smooth_landmarks=True,#是否选择平滑关键点
                    min_detection_confidence=0.4,#置信度阈值
                    min_tracking_confidence=0.8)#追踪阈值
    mpHands = mp.solutions.hands
    mpdraw = mp.solutions.drawing_utils

    hands=mpHands.Hands(min_detection_confidence=0.6,min_tracking_confidence=0.8)
    tt=0
    while True:
        frame = depth_stream.read_frame()
        dframe_data = np.array(frame.get_buffer_as_triplet()).reshape([480, 640, 2])
        dpt1 = np.asarray(dframe_data[:, :, 0], dtype='float32')
        dpt2 = np.asarray(dframe_data[:, :, 1], dtype='float32')
        
        dpt2 *= 255
        dpt = dpt1 + dpt2
        
        cv2.imshow('depth', dpt)
        colorTemplateframe = color_stream.read_frame()
        # colorTemplateframe是VideoFrame类型，所以需要转换为np.ndarry类型。
        cframe_data = np.array(colorTemplateframe.get_buffer_as_uint8()).reshape([480,640,3])
        # 通道转换：RGB转为BGR
        cframe = cv2.cvtColor(cframe_data,cv2.COLOR_BGR2RGB)
        result = hands.process(cframe_data)
        result_pose=pose.process(cframe_data)
        # result_pose.pose_landmarks.landmark[13]
        # if tt % 1 ==0:
        #     if result_pose.pose_landmarks:
        #         mpdraw.draw_landmarks(cframe,result_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        #         wrist = result_pose.pose_landmarks.landmark[13]
        #         print(wrist)
        #         now_wrist=(wrist.x,wrist.y,dpt[math.floor(wrist.y*479),math.floor(wrist.x*639)])
                
        #         wrist_position =(math.floor(wrist.x*640),math.floor(wrist.y*480),dpt[math.floor(wrist.y*479),math.floor(wrist.x*639)])
        #         # print(dpt[math.floor(wrist.y*480),math.floor(wrist.x*640)])

        #         client.publish(topic='plane', payload=str(wrist_position), qos=0, retain=False)
        if tt % 30 ==0:
            if result.multi_hand_landmarks:
                for handLms in result.multi_hand_landmarks:
                    mpdraw.draw_landmarks(cframe,handLms, mpHands.HAND_CONNECTIONS)
                    wrist = handLms.landmark[mpHands.HandLandmark.WRIST]
                    now_wrist=(wrist.x,wrist.y,dpt[math.floor(wrist.y*479),math.floor(wrist.x*639)])
                    
                    wrist_position =(math.floor(wrist.x*640),math.floor(wrist.y*480),dpt[math.floor(wrist.y*479),math.floor(wrist.x*639)])
                    # print(dpt[math.floor(wrist.y*480),math.floor(wrist.x*640)])

                    client.publish(topic='plane', payload=str(wrist_position), qos=0, retain=False)
        cv2.imshow("color",cframe)
        tt+=1
        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break
cap.release()
color_stream.stop()
depth_stream.stop()
dev.close()
cv2.destroyAllWindows()
openni2.unload()


    
