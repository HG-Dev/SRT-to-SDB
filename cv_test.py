import time
import numpy as np
import cv2
import mss
import numpy
from cv.screenreading import CharPattern

NUMS = ["img/{}.png".format(i) for i in range(10)]
CV_DIGITS = [cv2.threshold(cv2.imread(x, cv2.IMREAD_GRAYSCALE), 140, 255, cv2.THRESH_BINARY)[1] for x in NUMS]
for i, digit in enumerate(CV_DIGITS):
    test = CharPattern(str(i), bitmap=digit, save_to_file=True)
    assert test.signature_match(test.bitmap)


with mss.mss() as sct:
    cv2.namedWindow("OpenCV", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("OpenCV", 140, 220)
    i = 2
    img = CV_DIGITS[i]
    img_sub = img
    
    pattern = CharPattern("2")
    #pattern.generate_signature()

    while "Processing":

        # Display the picture
        cv2.imshow("OpenCV", img_sub)

        # Press "q" to quit
        key = cv2.waitKey(25)
        if key == ord("c"):
            i = i + 1
            if i > 8:
                print("Rolling back")
                i = 0
            img_sub = cv2.subtract(img, CV_DIGITS[i])
            signature = {}
            print(img_sub)
            print(img_sub[(5,1)])
            print(cv2.findNonZero(img_sub)[1][0])
            for y, row in enumerate(img_sub):
                for x, cell in enumerate(row):
                    signature[(x, y)] = bool(cell)
            print(signature)
            #findNonZero returns an array of point arrays
            #cv2.findNonZero(img_sub)[pt][0][x or y]

        if key == ord("d"):
            img_sub = cv2.subtract(CV_DIGITS[i], img)
        if key == ord("e"):
            print(pattern.bitmap)
            print(img)
            img_sub = pattern.bitmap
        if key == ord("q"):
            cv2.destroyAllWindows()
            break
