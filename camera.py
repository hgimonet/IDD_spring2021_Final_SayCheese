import paho.mqtt.client as mqtt
import uuid
import queue

import numpy as np
import cv2
import sys
import time

font = cv2.FONT_HERSHEY_SIMPLEX
comments = ['Dont forget to smile!!',
            'What a beautiful smile!']
label = ['Not smiling', 'ready']
is_smiling = []
timer = 0
message_queue = queue.Queue()

# import relevant Haar cascades for recognition
face_cascade = cv2.CascadeClassifier('cv/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('cv/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('cv/haarcascade_smile.xml')


# Attempt to open the webcam
img=None
webCam = False
try:
    print("Trying to open the Webcam.")
    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        raise("No camera")
    webCam = True
except:
    print("No camera found. Giving up.")



# Configure client connect and on message behaviors

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe("IDD/Saycheese/TakePic")

# this is the callback that gets called each time a message is recived
def on_message(client, userdata, msg):
    message_queue.put(msg.payload.decode('UTF-8'))
    print("message received!")

# Every client needs a random ID
cam_id = str(uuid.uuid1())
cam_topic = f'IDD/Saycheese/Cameras/{cam_id}'
# cam_topic = f'IDD/Saycheese/Cameras/Cam1'
client = mqtt.Client(cam_id)
# configure network encryption etc
client.tls_set()
# this is the username and pw we have setup for the class
client.username_pw_set('idd', 'device@theFarm')

# attach out callbacks to the client
client.on_connect = on_connect
client.on_message = on_message

# connect to the broker
client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

client.loop_start()
# print("Beyond the loop")

while(True):
    # get video feed from webcam
    if webCam:
        ret, img = cap.read()
        img_h, w, _ = img.shape

    # message handling part
    while not message_queue.empty():
        message = message_queue.get()
        if message == "take picture":
            print("Taking Picture!")
            cv2.imwrite('picture.jpg', img)

    # make grayscale image for recognition
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        cv2.putText(img, 'No face detected', (10, img_h-30), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        client.publish(cam_topic, 'No face detected')
    # only pick the first face
    for (x,y,w,h) in faces[:1]:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        # detect smiles
        smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 8)
        for (sx,sy,sw,sh) in smiles:
            # draw a rectangle around the smile
            cv2.rectangle(roi_color,(sx,sy),(sx+sw,sy+sh),(0,0,255),2)
        is_smiling.append(len(smiles) > 0)
        # print whether person is smiling
        txt = comments[int(np.mean(is_smiling[-15:]) > 0.5)]
        # print(txt)
        cv2.putText(img, txt, (10, 50), font, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, label[int(is_smiling[-1])], (10, img_h-30), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        # publish ready
        client.publish(cam_topic, label[int(is_smiling[-1])])

    # handle graceful quitting
    if webCam:
        cv2.imshow('Say Cheese! (press q to quit.)',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
    else:
        break

    time.sleep(0.1)
    timer += 1

cv2.destroyAllWindows()

