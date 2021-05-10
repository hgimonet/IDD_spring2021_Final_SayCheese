import time
import board
import busio

import adafruit_mpr121

i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

mode = 0 ## Drawing mode by default

while True:
    for i in range(12):
        if mpr121[i].value:
            if i == 0:
                mode = i # DRAWING MODE
                print("Drawing mode")
            else:
                mode = i # EMOJI MODE
                print(f"Draw the Emoji number {i}")
    time.sleep(0.25)  # Small delay to keep from spamming output messages.