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




# 假设你已经有相机的内参矩阵和畸变系数
camera_matrix = np.array([[540.65945374, 0, 352.78537456],
                          [0, 532.41856823, 179.58045514],
                          [0, 0, 1]])

dist_coeffs = np.array([1.83537582e-01, -5.84076503e-01, -1.58649228e-02, 3.48868589e-04, 8.67641532e-01])  # 畸变系数（如果不需要校正可以设置为零）
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

    mpHands = mp.solutions.hands
    mpdraw = mp.solutions.drawing_utils

    hands=mpHands.Hands(min_detection_confidence=0.8,min_tracking_confidence=0.8)
    tt=0
    X=0
    Y=0
    Z=0
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

        if tt % 1 ==0:
            if result.multi_hand_landmarks:
                for handLms in result.multi_hand_landmarks:
                    la_X=X
                    la_Y=Y
                    la_Z=Z
                    mpdraw.draw_landmarks(cframe,handLms, mpHands.HAND_CONNECTIONS)
                    wrist = handLms.landmark[mpHands.HandLandmark.WRIST]
                    now_wrist=(wrist.x,wrist.y,dpt[int(wrist.y*479),int(wrist.x*639)])
                    u=int(wrist.x*640)
                    v=int(wrist.y*480)
                    Z=dpt[int(wrist.y*479),int(wrist.x*639)]
                    X = (u - camera_matrix[0, 2]) * Z / camera_matrix[0, 0]
                    Y = (v - camera_matrix[1, 2]) * Z / camera_matrix[1, 1]
                    wrist_position =(u,v,dpt[int(wrist.y*479),int(wrist.x*639)])
                    wrist_position_world=(X/1000,Y/1000,Z/1000)
                    # print(dpt[int(wrist.y*480),int(wrist.x*640)])
                    # print((X-la_X)/1000)
                    
                    # print((Z-la_Z)/1000)
                    client.publish(topic='plane', payload=str(wrist_position_world), qos=0, retain=False)
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



