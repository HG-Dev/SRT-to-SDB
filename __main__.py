''' Main SST manipulating script '''

import cv2
import pyautogui
import pygetwindow
import numpy as np
from mss import mss
from srt.srt import parse
from cv.screenreading import ScreenReader, Region

NUMS = ["img/{}.png".format(i) for i in range(10)]
SCREEN = mss()
DIGIT_REGIONS = [] #Digit region dictionaries
AUDIO_ORIGIN = []
CV_DIGITS = [cv2.threshold(cv2.imread(x, cv2.IMREAD_GRAYSCALE), 20, 0, cv2.THRESH_TOZERO)[1] for x in NUMS]
# CV_DIGIT_HISTOGRAMS = [cv2.calcHist([digit], [0], None, [24], [0, 256]) for digit in CV_DIGITS]
TEST_SRT = "test.srt"

def main():
    """ Main body """
    # pylint: disable=no-member
    if switch_to_sst_input():
        sst_calibrate()
        srt_content = ""
        with open(TEST_SRT, encoding="utf8") as infile:
            srt_content = infile.read()
        srt_subtitles = parse(srt_content)
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
    size_x, size_y = pyautogui.size()
    # Find place TC meter (##:##:##:##)
    digit_points = ScreenReader.FindPatternRegionsOnScreen(
        ScreenReader.DIGIT_PATTERNS,
        Region(0, int(size_y/2), int(size_x/2), int(size_y/2))
    )
    y_instance_dict = {}
    for y, x, c in digit_points:
        y_instance_dict.setdefault(y, 0)
        y_instance_dict[y] += 1
    if len(y_instance_dict.keys()) > 3:
        raise Exception("Error: Too many digits at different heights. Try searching a smaller area.")
    elif len(y_instance_dict.keys()) > 1:
        # Iron out template search mistakes by forcing equal height
        # OpenCV's template search is not pixel perfect.
        correct_y = max(y_instance_dict.keys(), key=(lambda k: y_instance_dict[k]))
        # Apply correct_y to list
        digit_points = [(correct_y, x, char) for y, x, char in digit_points]
    digit_points.sort(key=lambda r: r[0] + r[1])
    number_str = ""
    for y, x, c in digit_points[0:8]:
        number_str += c
        new_region = Region(top=y, left=x, width=7, height=11)
        DIGIT_REGIONS.append(new_region)
    print(number_str)
    print(sst_read_tc())


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
    tc_str = ScreenReader.MatchPatternRegions(
        ScreenReader.DIGIT_PATTERNS,
        DIGIT_REGIONS
    )
    i = 0
    hours = 10 * int(tc_str[i]) + int(tc_str[i+1])
    i = i + 2
    minutes = 10 * int(tc_str[i]) + int(tc_str[i+1])
    i = i + 2
    seconds = 10 * int(tc_str[i]) + int(tc_str[i+1])
    i = i + 2
    frames = 10 * int(tc_str[i]) + int(tc_str[i+1])
    return (hours, minutes, seconds, frames)

if __name__ == "__main__":
    main()
