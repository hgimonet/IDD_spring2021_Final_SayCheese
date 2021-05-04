import paho.mqtt.client as mqtt
import uuid

import time


# some other examples
# topic = 'IDD/a/fun/topic'

# this is the callback that gets called once we connect to the broker.
# we should add our subscribe functions here as well
outputs = {}


def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe('IDD/Saycheese/Cameras/#')


# you can subsribe to as many topics as you'd like
# client.subscribe('some/other/topic')


# this is the callback that gets called each time a message is recived
def on_message(client, userdata, msg):
    print(f"topic: {msg.topic} msg: {msg.payload.decode('UTF-8')}")
    # print(str(msg.topic))
    cam_idx = str(msg.topic)
    # print(cam_idx)
    outputs[cam_idx] = msg.payload.decode('UTF-8')
    # print(outputs)

# Every client needs a random ID
client = mqtt.Client(str(uuid.uuid1()))
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
    val = "don't take picture"

    photo = set(outputs.values())
    if len(photo) == 1:
        if list(photo)[0] == "ready":
            val = "take picture"

    client.publish("IDD/Saycheese/TakePic", val)
    print(val)

    time.sleep(0.1)