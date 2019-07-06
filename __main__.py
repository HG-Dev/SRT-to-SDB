''' Main SST manipulating script '''

import cv2
import pyautogui
import pygetwindow
import numpy as np
from mss import mss
import srt

NUMS = ["img/{}.png".format(i) for i in range(10)]
SCREEN = mss()
DIGIT_REGIONS = []
AUDIO_ORIGIN = []
CV_DIGITS = [cv2.threshold(cv2.imread(x, cv2.IMREAD_GRAYSCALE), 20, 0, cv2.THRESH_TOZERO)[1] for x in NUMS]
# CV_DIGIT_HISTOGRAMS = [cv2.calcHist([digit], [0], None, [24], [0, 256]) for digit in CV_DIGITS]
TEST_VALS = "30256512"
TEST_SRT = "test.srt"

def main():
    """ Main body """
    # pylint: disable=no-member
    if switch_to_sst_input():
        sst_calibrate()
        srt_content = ""
        with open(TEST_SRT, encoding="utf8") as infile:
            srt_content = infile.read()
        #sst_input_loop(srt_content)
        pyautogui.moveTo(x=1280, y=720, duration=1)


def switch_to_sst_input():
    try:
        sst_window = pygetwindow.getWindowsWithTitle("SSTG1")[0]
        sst_window.maximize()
        sst_window.activate()
        return True
    except Exception:
        pyautogui.alert(text="Please open SST and start a new file", title="Error", button='OK')
    return False

def sst_calibrate():
    size = pyautogui.size()
    # Find place TC meter (00:00:00:00)
    digit_found_regions = []
    for i, num in enumerate(NUMS):
        for region in pyautogui.locateAllOnScreen(num):
            digit_found_regions.append(region)
    digit_found_regions.sort(key=lambda r: r.left - r.top)
    tc_start_region = digit_found_regions[0]
    for i in range(0, 8):
        offset = 8 * (i + int(i/2))
        DIGIT_REGIONS.append({"top": tc_start_region.top, "left": tc_start_region.left+offset, "width": 7, "height": 11})
    AUDIO_ORIGIN = {"top": DIGIT_REGIONS[0]["top"]+98, "left": DIGIT_REGIONS[0]["left"]-124}
    DIGIT_REGIONS.reverse()
    # Record current time
    tc_start = sst_read_tc()
    print(tc_start)
    pyautogui.moveTo(x=AUDIO_ORIGIN["left"], y=AUDIO_ORIGIN["top"])
    pyautogui.drag(xOffset=300, duration=2, pause=1, tween=pyautogui.easeOutCirc)
    tc_finish = sst_read_tc()
    print(tc_finish)
    if (tc_finish < tc_start):
        tc_finish = tc_finish + 30
    print(str(tc_finish[3] - tc_start[3]))


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
    raise Exception("Could not find any digit (searched {})".format(monitor))

if __name__ == "__main__":
    main()
