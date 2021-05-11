# How to load a Tensorflow model using OpenCV
# Jean Vitor de Paulo Blog - https://jeanvitor.com/tensorflow-object-detecion-opencv/
# David edited some stuff
# CREDIT Multiple Color Detection in Real-Time using Python-OpenCV https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/ CREDIT

import numpy as np
import cv2
import sys
import time

# Load a model imported from Tensorflow
tensorflowNet = cv2.dnn.readNetFromTensorflow('frozen_inference_graph.pb', 'ssd_mobilenet_v2_coco_2018_03_29.pbtxt')

# parser.add_argument('--image', '-i', help = 'First image filepath on uniform background')
# image = cv2.imread(args.image)

img = None
mask_image_true_size = cv2.imread("{IMAGE LOCATION}", -1)
mask_image_true_size_p = cv2.imread("{IMAGE LOCATION}", -1)
mask_image_true_size_writing = cv2.imread("{IMAGE LOCATION}", -1)
# template = cv2.imread("/Users/brandtbeckerman/Desktop/IDD_CT_Spring_2021/IDD_FINAL/pink_limeGreen_small.jpg")
# template_grey = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
webCam = True
if (len(sys.argv) > 1 and not sys.argv[-1] == "noWindow"):
    try:
        print("I'll try to read your image")
        img = cv2.imread(sys.argv[1])
        if img is None:
            print("Failed to load image file:", sys.argv[1])
    except:
        print("Failed to load the image are you sure that:", sys.argv[1], "is a path to an image?")
else:
    try:
        print("Trying to open the Webcam.")
        cap = cv2.VideoCapture(0)
        if cap is None or not cap.isOpened():
            raise ("No camera")
        webCam = True
    except:
        img = cv2.imread("../data/test.jpg")
        print("Using default image.")

saved_emoji_location = []
saved_pixel_location = []
start_clock = time.clock()
start_clock_p = time.clock()
marker_clock = 0
marker_clock_p = 0
while (True):
    time_passed = time.clock() - start_clock
    time_passed_p = time.clock() - start_clock_p

    if webCam:
        ret, img = cap.read()
        img = cv2.flip(img, 1)

    rows, cols, channels = img.shape

    colors = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    final_img = img

    for emoji in saved_emoji_location:
        startY = emoji[0][1]
        startX = emoji[0][0]
        mask_image_alpha = emoji[1][:, :, 3] / 255.0
        img_alpha = 1.0 - mask_image_alpha
        for c in range(3):
            final_img[startY:startY + emoji[1].shape[0], startX:startX + emoji[1].shape[1], c] = (
                        mask_image_alpha * emoji[1][:, :, c] + \
                        img_alpha * final_img[startY:startY + emoji[1].shape[0], startX:startX + emoji[1].shape[1], c])

    # BLUE START
    blue_1 = np.array([30, 100, 30])
    blue_2 = np.array([70, 255, 255])
    # blue_1 = np.array([80, 80, 20])
    # blue_2 = np.array([255, 255, 255])
    blue_color = cv2.inRange(colors, blue_1, blue_2)
    contours_blue, _ = cv2.findContours(blue_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    scale = 1  # 1/(3-time_passed+ 0.5)

    mask_image = cv2.resize(mask_image_true_size, None, fx=scale, fy=scale)
    mask_image_alpha = mask_image[:, :, 3] / 255.0
    img_alpha = 1.0 - mask_image_alpha

    for pic, contour in enumerate(contours_blue):
        area = cv2.contourArea(contour)
        if (area > 600):
            x, y, width, height = cv2.boundingRect(contour)
            startY = y
            startX = x
            # cv2.putText(img, f"{round(3-time_passed, 2)}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 5)
            # https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
            # if not ((startY+mask_image.shape[0]) > img.shape[0]):
            if ((startY + mask_image.shape[0]) < img.shape[0]):
                if ((startX + mask_image.shape[1]) < img.shape[1]):
                    if (mask_image.shape < img.shape):
                        marker_clock = 1
                        # or not (startY < img.shape[0])\
                        # or not (startX < img.shape[1]):
                        cv2.putText(img, f"{round(3 - time_passed, 2)}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 3.0,
                                    (0, 0, 255), 5)
                        try:
                            for c in range(3):
                                final_img[startY:startY + mask_image.shape[0], startX:startX + mask_image.shape[1],
                                c] = (mask_image_alpha * mask_image[:, :, c] + \
                                      img_alpha * final_img[startY:startY + mask_image.shape[0],
                                                  startX:startX + mask_image.shape[1], c])
                            # final_img[startY:startY+mask_image.shape[0], startX:startX+mask_image.shape[1]] = mask_image
                        except:
                            pass
                        if round(3 - time_passed, 2) < 0.1:
                            saved_emoji_location.append(((startX, startY), mask_image))
                            start_clock = time.clock()
            break

    if marker_clock != 1:
        start_clock = time.clock()

    else:
        marker_clock = 0

    # PINK START
    pink_1 = np.array([150, 150, 50])
    pink_2 = np.array([240, 240, 240])
    pink_color = cv2.inRange(colors, pink_1, pink_2)
    contours_pink, _ = cv2.findContours(pink_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    scale = 1  # 1/(3-time_passed+ 0.5)

    mask_image_p = cv2.resize(mask_image_true_size_p, None, fx=scale, fy=scale)
    mask_image_alpha_p = mask_image_p[:, :, 3] / 255.0
    img_alpha_p = 1.0 - mask_image_alpha_p

    for pic, contour in enumerate(contours_pink):
        area = cv2.contourArea(contour)
        if (area > 600):
            x, y, width, height = cv2.boundingRect(contour)
            startY = y
            startX = x
            # https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
            if ((startY + mask_image_p.shape[0]) < img.shape[0]):
                if ((startX + mask_image_p.shape[1]) < img.shape[1]):
                    if (mask_image_p.shape < img.shape):
                        marker_clock_p = 1
                        cv2.putText(img, f"{round(3 - time_passed_p, 2)}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 3.0,
                                    (0, 255, 0), 5)
                        try:
                            for c in range(3):
                                final_img[startY:startY + mask_image_p.shape[0], startX:startX + mask_image_p.shape[1],
                                c] = \
                                    (mask_image_alpha_p * mask_image_p[:, :, c] + \
                                     img_alpha_p * final_img[startY:startY + mask_image_p.shape[0],
                                                   startX:startX + mask_image_p.shape[1], c])
                            # final_img[startY:startY+mask_image.shape[0], startX:startX+mask_image.shape[1]] = mask_image
                        except:
                            pass
                        if round(3 - time_passed_p, 2) < 0.1:
                            saved_emoji_location.append(((startX, startY), mask_image_p))
                            start_clock_p = time.clock()
            break

    if marker_clock_p != 1:
        start_clock_p = time.clock()

    else:
        marker_clock_p = 0

    for pixel in saved_pixel_location:
        startY = pixel[0]
        startX = pixel[1]
        # final_img[startY:startY+10, startX:startX+10] = [0, 0, 255]
        final_img[startY:startY + 10, startX:startX + 10] = [0, 0, 255]

    # Write START
    write_1 = np.array([20, 100, 100])
    write_2 = np.array([30, 255, 255])
    #    write_1 = np.array([80, 10, 10])
    #    write_2 = np.array([120, 200, 255])

    write_color = cv2.inRange(colors, write_1, write_2)
    contours_write, _ = cv2.findContours(write_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    scale_writing = 0.2  # 1/(3-time_passed+ 0.5)

    mask_image_writing = cv2.resize(mask_image_true_size_writing, None, fx=scale_writing, fy=scale_writing)
    mask_image_alpha_writing = mask_image_writing[:, :, 3] / 255.0
    img_alpha_writing = 1.0 - mask_image_alpha_writing

    for pic, contour in enumerate(contours_write):
        area = cv2.contourArea(contour)
        if (area > 30):
            x, y, width, height = cv2.boundingRect(contour)
            startY = y
            startX = x
            #  final_img[startY:startY+40, startX:startX+40] = [0, 255, 0]
            if ((startY + mask_image_writing.shape[0]) < img.shape[0]):
                if ((startX + mask_image_writing.shape[1]) < img.shape[1]):
                    if (mask_image_writing.shape < img.shape):
                        for c in range(3):
                            final_img[startY:startY + mask_image_writing.shape[0],
                            startX:startX + mask_image_writing.shape[1], c] = \
                                (mask_image_alpha_writing * mask_image_writing[:, :, c] + \
                                 img_alpha_writing * final_img[startY:startY + mask_image_writing.shape[0],
                                                     startX:startX + mask_image_writing.shape[1], c])
                        saved_pixel_location.append((startY, startX))

            break

    # Erase START
    #    erase_1 = np.array([30, 100,30])
    #    erase_2 = np.array([70, 255, 255])
    #    erase_color = cv2.inRange(colors, erase_1, erase_2)
    #    contours_erase, _ = cv2.findContours(erase_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #    for pic, contour in enumerate(contours_erase):
    #       area = cv2.contourArea(contour)
    #       if(area > 1000):
    #          print("hey")
    #          saved_pixel_location = []
    #          break

    if webCam:
        if sys.argv[-1] == "noWindow":
            print("Finished a frame")
            cv2.imwrite('detected_out.jpg', img)
            continue
        cv2.imshow('detected (press q to quit)', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
    else:
        break

cv2.imwrite('detected_out.jpg', final_img)
cv2.imshow('Image out', final_img)
cv2.waitKey(0)
cv2.destroyAllWindows()