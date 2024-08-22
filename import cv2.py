import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import time


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
   
cap=cv2.VideoCapture(0)

mpHands = mp.solutions.hands
mpdraw = mp.solutions.drawing_utils

hands=mpHands.Hands()

while True:
    ret,img=cap.read()
    if ret:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(img.shape)
        result = hands.process(imgRGB)
        #坐标
        # print(result.multi_hand_world_landmarks[mpHands.HandLandmark.WRIST])
        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                mpdraw.draw_landmarks(img,handLms, mpHands.HAND_CONNECTIONS)
                wrist = handLms.landmark[mpHands.HandLandmark.WRIST]
                wrist_position = {
                'x': wrist.x,
                'y': wrist.y,
                'z': wrist.z
                }
                print(wrist_position)
                client.publish(topic='plane', payload=str(wrist_position), qos=0, retain=False)
        cv2.imshow('img',img)
        
    if cv2.waitKey(1) == ord('q'):
        break