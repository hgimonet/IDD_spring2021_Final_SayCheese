import numpy as np
import cv2
from PIL import Image
import sys
import time

import paho.mqtt.client as mqtt
import uuid
import queue

ON_PI = True  # toggle this to false if not running on pi
if ON_PI:
    import board
    import busio
    import adafruit_mpr121

    # Import the capacitor sensor
    i2c = busio.I2C(board.SCL, board.SDA)
    mpr121 = adafruit_mpr121.MPR121(i2c)

# load emojis
EMOJIS = {
    0: "emojis/lower-left-paintbrush_1f58c.png",
    1: "emojis/grinning-face_1f600.png",
    2: "emojis/partying-face_1f973.png",
    3: "emojis/zany-face_1f92a.png",
    4: "emojis/shamrock_2618.png",
    5: "emojis/red-heart_2764-fe0f.png",
    6: "emojis/waving-hand_1f44b.png",
    7: "emojis/globe-showing-americas_1f30e.png",
    8: "emojis/graduation-cap_1f393.png",
    9: "emojis/bottle-with-popping-cork_1f37e.png",
    10: "emojis/balloon_1f388.png",
    11: "emojis/light-bulb_1f4a1.png",
}
if ON_PI:
    for i in EMOJIS:
        EMOJIS[i] = Image.open(EMOJIS[i]).resize((50, 50), Image.LANCZOS)
else:
    for i in EMOJIS:
        EMOJIS[i] = Image.open(f'CollaBoard/{EMOJIS[i]}').resize((50, 50), Image.LANCZOS)

mode = 0 # Drawing mode by default

# Green HSV
DETECT_COL_MIN = np.array((40, 30,30))
DETECT_COL_MAX = np.array((70, 255,255))

# # Orange HSV
# DETECT_COL_MIN = np.array((10, 100, 20))
# DETECT_COL_MAX = np.array((25, 255,255))

PAINT_SIZE = 2

PIXEL_MEM = 2000
EMOJI_MEM = 12

saved_emoji = [] # N by 3 list of N (id, x, y)
saved_pixel = []

message_q = queue.Queue()

emoji_counting = False
emoji_start = time.time()
emoji_timer = 0

# Attempt to open the webcam
webCam = True
try:
    print("Trying to open the Webcam.")
    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        raise ("No camera")
    webCam = True
except:
    print("Cannot open the webcam.")

# Configure client connect and on message behaviors

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe("IDD/CollaBoard/#")

# this is the callback that gets called each time a message is recived
def on_message(client, userdata, msg):
    message_q.put(list(map(int, msg.payload.decode('UTF-8').split(','))))

# Every client needs a random ID
cam_id = str(uuid.uuid1())
cam_topic = f'IDD/CollaBoard/Cameras/{cam_id}'
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

while True:

    if ON_PI:
        # Get mode from capacitor sensor
        for i in range(12):
            if mpr121[i].value:
                mode = i

    # get camera frame
    if webCam:
        ret, img = cap.read()
        img = cv2.flip(img, 1)

    rows, cols, channels = img.shape
    col_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # detect object for painting
    detected_colors = cv2.inRange(col_img, DETECT_COL_MIN, DETECT_COL_MAX)
    # detected_colors = cv2.threshold(img[:, :,1], 200, 255, cv2.THRESH_BINARY)
    detected_contours, _ = cv2.findContours(detected_colors, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(detected_contours):
        area = cv2.contourArea(contour)
        if (area > 20):
            x, y, w, h = cv2.boundingRect(contour)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if mode == 0:  # paint mode
                # mqtt post
                client.publish(cam_topic,f"{x},{y}")
            else:  # emoji mode
                emoji_counting = True
                emoji_timer = time.time() - emoji_start
                emoji_countdown = round(3 - emoji_timer, 2)
                # display countdown
                cv2.putText(img, f"{emoji_countdown}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2.0,
                            (0, 255, 0), 5)
                if emoji_countdown < 0.1:
                    # mqtt post
                    client.publish(cam_topic,f"{mode},{x},{y}")
                    emoji_counting = False

        if not emoji_counting:
            emoji_start = time.time()

    # get all messages
    while not message_q.empty():
        m = message_q.get()
        if len(m) == 2:
            saved_pixel.append(m)
            # cap list memory
            saved_pixel = saved_pixel[-PIXEL_MEM:]
        elif len(m) == 3:
            saved_emoji.append(m)
            # cap list memory
            saved_emoji = saved_emoji[-PIXEL_MEM:]

    # Draw on the image
    for x,y in saved_pixel:
        img = cv2.circle(img, (x,y), radius=4, color=(255,0,255), thickness=-1)

    # print emojis on the image
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    for i, x, y in saved_emoji:
        pil_img.paste(EMOJIS[i], box=(x, y), mask=EMOJIS[i])

    # handle graceful quitting
    if webCam:
        cv2.imshow(f'CollaBoard - mode {mode} (press m to switch drawing modes, or press q to quit.)', cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR))
        # cv2.imshow('Mask (press q to quit.)', detected_colors)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
        if cv2.waitKey(1) & 0xFF == ord('p'):
            mode = min(mode+1, 11)
            print(f"changing mode to {mode}")
    else:
        break

    time.sleep(0.1)

cv2.destroyAllWindows()

