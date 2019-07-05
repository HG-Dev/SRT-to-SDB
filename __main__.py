''' Main SST manipulating script '''

import cv2
import pyautogui
import pygetwindow
import numpy as np
from mss import mss

NUMS = ["img/{}.png".format(i) for i in range(10)]
SCREEN = mss()
DIGIT_REGIONS = []
for i in range(0, 8):
    offset = 8 * (i + int(i/2))
    DIGIT_REGIONS.append({"top": 834, "left": 234-offset, "width": 7, "height": 11})
CV_DIGITS = [cv2.threshold(cv2.imread(x, cv2.IMREAD_GRAYSCALE), 20, 0, cv2.THRESH_TOZERO)[1] for x in NUMS]
# CV_DIGIT_HISTOGRAMS = [cv2.calcHist([digit], [0], None, [24], [0, 256]) for digit in CV_DIGITS]
TEST_VALS = "30256512"

def main():
    """ Main body for starting up and terminating Tweetfeeder bot """
    # pylint: disable=no-member
    if switch_to_sst_input():
        sst_input_loop()
        pyautogui.moveTo(x=1280, y=720, duration=1)
    cv2.destroyAllWindows()

def switch_to_sst_input():
    try:
        sst_window = pygetwindow.getWindowsWithTitle("SSTG1")[0]
        sst_window.maximize()
        sst_window.activate()
        return True
    except Exception:
        pyautogui.alert(text="Please open SST and start a new file", title="Error", button='OK')
    return False


def sst_input_loop():

    size = pyautogui.size()
    pyautogui.leftClick(x=50, y=size[1]-125, interval=0.3)
    # Record current time
    tc = sst_read_tc()
    print(tc)

def monitor_to_ltwh_tuple(monitor):
    return (monitor["left"], monitor["top"], monitor["width"], monitor["height"])

def sst_read_tc():
    """ Return: (hr, min, sec, frames) """
    i = 0
    frames = 10 * num_at_region(i+1) + num_at_region(i)
    i = i + 2
    seconds = 10 * num_at_region(i+1) + num_at_region(i)
    i = i + 2
    minutes = 10 * num_at_region(i+1) + num_at_region(i)
    i = i + 2
    hours = 10 * num_at_region(i+1) + num_at_region(i)
    # i = 0
    # left = monitor_to_ltwh_tuple(DIGIT_REGIONS[i+1])
    # right = monitor_to_ltwh_tuple(DIGIT_REGIONS[i])
    # frames = 10 * num_at_region(left) + num_at_region(right)
    # i = i + 2
    # left = monitor_to_ltwh_tuple(DIGIT_REGIONS[i+1])
    # right = monitor_to_ltwh_tuple(DIGIT_REGIONS[i])
    # seconds = 10 * num_at_region(left) + num_at_region(right)
    # i = i + 2
    # left = monitor_to_ltwh_tuple(DIGIT_REGIONS[i+1])
    # right = monitor_to_ltwh_tuple(DIGIT_REGIONS[i])
    # minutes = 10 * num_at_region(left) + num_at_region(right)
    # i = i + 2
    # left = monitor_to_ltwh_tuple(DIGIT_REGIONS[i+1])
    # right = monitor_to_ltwh_tuple(DIGIT_REGIONS[i])
    # hours = 10 * num_at_region(left) + num_at_region(right)
    return (hours, minutes, seconds, frames)

def num_at_region(reg_index):
    """ Return: integer """
    monitor = DIGIT_REGIONS[reg_index]
    for i, cv_digit in enumerate(CV_DIGITS):
        ss_digit = np.array(SCREEN.grab(monitor))
        ss_digit = cv2.cvtColor(ss_digit, cv2.COLOR_BGR2GRAY)
        ss_digit = cv2.threshold(ss_digit, 20, 0, cv2.THRESH_TOZERO)[1]
        overlaid = cv2.add(cv_digit, ss_digit)
        overlaid_nb = cv2.countNonZero(overlaid)
        ss_digit_nb = cv2.countNonZero(ss_digit)
        cv_digit_nb = cv2.countNonZero(cv_digit)
        if overlaid_nb == ss_digit_nb == cv_digit_nb:
            return i
    raise Exception("Could not find any digit")

if __name__ == "__main__":
    main()
