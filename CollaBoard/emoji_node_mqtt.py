import numpy as np
import cv2
from PIL import Image
import sys
import time
import random
import matplotlib.colors as mcolors

import paho.mqtt.client as mqtt
import uuid
import queue



try:
    import board
    import busio
    import adafruit_mpr121

    ON_PI = True  # toggle this to false if not running on pi

    # Import the capacitor sensor
    i2c = busio.I2C(board.SCL, board.SDA)
    mpr121 = adafruit_mpr121.MPR121(i2c)
except:
    ON_PI = False

print(f"Running on a Pi: {ON_PI}")

# load emojis
EMOJIS = {
    0: "emojis/lower-left-paintbrush_1f58c.png",
    1: "emojis/grinning-face_1f600.png",
    2: "emojis/partying-face_1f973.png",
    3: "emojis/light-bulb_1f4a1.png",
    4: "emojis/shamrock_2618.png",
    5: "emojis/red-heart_2764-fe0f.png",
    6: "emojis/waving-hand_1f44b.png",
    7: "emojis/globe-showing-americas_1f30e.png",
    8: "emojis/graduation-cap_1f393.png",
    9: "emojis/bottle-with-popping-cork_1f37e.png",
    10: "emojis/balloon_1f388.png",
    11: "emojis/zany-face_1f92a.png",

}

# import emoji images
if ON_PI:
    for i in EMOJIS:
        EMOJIS[i] = Image.open(EMOJIS[i]).resize((50, 50), Image.LANCZOS)
else:
    for i in EMOJIS:
        EMOJIS[i] = Image.open(f'CollaBoard/{EMOJIS[i]}').resize((50, 50), Image.LANCZOS)

# Set range of color to detect for the drawing pen

# Green HSV
DETECT_COL_MIN = np.array((40, 30,30))
DETECT_COL_MAX = np.array((70, 255,255))

# # Orange HSV
# DETECT_COL_MIN = np.array((10, 100, 20))
# DETECT_COL_MAX = np.array((25, 255,255))

PAINT_SIZE = 2
PAINT_COLS = [tuple(int(round(i)) for i in mcolors.rgb_to_hsv(mcolors.to_rgb(col))*255)
              for col in ['b', 'g', 'r', 'c', 'm', 'y'] ]

# Set the memory size for the pen and the emojis
PIXEL_MEM = 1500
EMOJI_MEM = 12

message_q = queue.Queue()

saved_emoji = [] # N by 3 list of N (id, x, y)
saved_pixel = []

mode = 0  # default mode is draw mode

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
# Pick a random color for the camera's pen:
CAM_COLOR = random.randint(0,len(PAINT_COLS)-1)
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
        for i in range(11):
            if mpr121[i].value:
                mode = i
                print(f'Switching to mode {i}: {EMOJIS[i]}')
            if mpr121[11].value:
                print("clearing board")
                client.publish(cam_topic, f"0")

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
        if (area > 30):
            x, y, w, h = cv2.boundingRect(contour)
            # img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if mode == 0:  # paint mode
                # mqtt post
                client.publish(cam_topic,f"{mode},{x},{y},{CAM_COLOR}")
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
        # emoji_counting = False

    # get all messages
    while not message_q.empty():
        m = message_q.get()
        if len(m) == 1:
            print("Clearing board.")
            saved_emoji = []
            saved_pixel = []
        elif m[0] == 0:
            saved_pixel.append(m)
            # cap list memory
            saved_pixel = saved_pixel[-PIXEL_MEM:]
        else:
            saved_emoji.append(m)
            # cap list memory
            saved_emoji = saved_emoji[-EMOJI_MEM:]

    # Draw on the image
    for _,x,y,c in saved_pixel:
        img = cv2.circle(img, (x,y), radius=4, color=PAINT_COLS[c], thickness=-1)

    # print emojis on the image
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    pil_img.paste(EMOJIS[mode], box=(10, 10), mask=EMOJIS[mode])
    for i, x, y in saved_emoji:
        pil_img.paste(EMOJIS[i], box=(x, y), mask=EMOJIS[i])

    # handle graceful quitting
    if webCam:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
        cv2.imshow(f'CollaBoard (press q to quit.)',
                       cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR))
        # cv2.imshow('Mask (press q to quit.)', detected_colors)
        # for changing modes
        if cv2.waitKey(1) & 0xFF == ord('p'):
            mode = (mode+1) % 11
            print(f"changing mode to {mode}")
        # for eraser mode
        if cv2.waitKey(1) & 0xFF == ord('e'):
            print("clearing board")
            client.publish(cam_topic, f"0")
    else:
        break

    if ON_PI:
        time.sleep(0.5)
    else:
        time.sleep(0.005)

cv2.destroyAllWindows()

