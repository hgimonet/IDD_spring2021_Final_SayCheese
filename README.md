# [Final Project for IDD Spring 2021](https://github.com/FAR-Lab/Interactive-Lab-Hub/tree/Spring2021/Final%20Project)
# CollaBoard, a collaborative drawing and emoji board!
by Hortense Gimonet, Irene Font Peradejordi, Brandt Beckerman, Rui Maki

## What it is

This is a collaborative drawing board. You can leave graduation messages for you peers at CT!
There are multiple boards around campus, and all of them are connected. Editing on one is editing them all!

## How to Use

To get started, grab the **writing tool** (a green piece of chalk or highlighter). 
This is what you will use to interact with the Board! 

### Eraser Mode
To clear the entire board press 'e' on a laptop, or the eraser on the box.

### Drawing Mode
In drawing mode, the tool will leave a trace wherever it is detected. 
To have a break between lines or when writing letters, hide the pen behind your hand and show it again to resume painting.

### Emojis Mode
Hold the green pen in place for 3 seconds to place an emoji. 
A countdown to 3 seconds will start whenever the pen is detected in emoji mode. 
You can also hide the pen in your hand if you are still thinking about where to place the emoji.

To switch between emojis, press the capacitive buttons on the pi box, or press 'p' on a laptop.

## How It's Made

Each Pi must be equipped with a camera, a capacitive touch board, and connected to a screen.
A box to contain the Pi can be laser cut out of cardboard or wood. 
You will also need conductive wire or tape to connect the capacitive sensors to the correct buttons on the box.

### Materials

For this project, you will need:
- A [Raspberry Pi](https://www.adafruit.com/product/)
- A 12-button [Capacitive Touch Sensor Breakout](https://www.adafruit.com/product/4830)
- A screen
- Thin wood or cardboard
- Conductive wires or copper/aluminium tape
- A single bright-colored object to be detected by the camera

### Code
The only python required to run CollaBoard is [CollaBoard/emoji_node_mqtt.py](https://github.com/hgimonet/IDD_spring2021_Final_SayCheese/blob/main/CollaBoard/emoji_node_mqtt.py). 
You will also need the emoji image files in [CollaBoard/emojis](https://github.com/hgimonet/IDD_spring2021_Final_SayCheese/tree/main/CollaBoard/emojis)

Each computer running the code must be equipped with a camera or webcam. 

To run the code on the pi, you must be on the GUI. Do access the pi with the GUI, you can VNC in.
Once in the `CollaBoard` folder, you can start the program with the following command:
```
python emoji_node_mqtt.py
```


### Making the Box
The files required to laser cut and engrave the box are in [CollaBoard/Box_files](https://github.com/hgimonet/IDD_spring2021_Final_SayCheese/tree/main/CollaBoard/Box_files).
They were based on this [box](https://3axis.co/laser-cut-wooden-box-with-sliding-lid-15x15x10-3mm-mdf-template-dxf-file/075yjn3o/).

To cut and assemble the box, follow [this tutorial]().

### Assembly
1. After putting all but the last faces of the box together, securely place the Pi inside.
2. Place the camera in the camera hole
3. Connect the emojis engravings to the capacitive sensor board with the wire or tape by passing it through the holes 
   beneath the engraved emojis. The number lineup is the following:

| Number | Emoji |
|--------|-----------|
| 0 | Paintbrush Mode |
| 1 | grinning-face :grinning: |
| 2 | partying-face :partying_face:|
| 3 | shamrock :shamrock: |
| 4 | red-heart :hearts: |
| 5 | waving-hand :wave: |
| 6 | globe :earth_americas: |
| 7 | graduation-cap |
| 8 | bottle-with-popping-cork :champagne: |
| 9 | balloon 	:balloon: |
| 10 | light-bulb :bulb: |
| 11 | Eraser mode |
