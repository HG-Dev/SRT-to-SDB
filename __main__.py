''' Main SST manipulating script '''

import pyautogui
import pygetwindow

NUMS = ["img/{}.png".format(i) for i in range(10)]
DIGIT_REGIONS = []
for i in range(0, 8):
    offset = 8 * (i + int(i/2))
    DIGIT_REGIONS.append((234-offset, 834, 7, 11))

def main():
    """ Main body for starting up and terminating Tweetfeeder bot """
    # pylint: disable=no-member
    if switch_to_sst_input():
        sst_input_loop()

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

def sst_read_tc():
    """ Return: (hr, min, sec, frames) """
    # Get frame
    frames = 10 * num_at_coords(DIGIT_REGIONS[1]) + num_at_coords(DIGIT_REGIONS[0])
    seconds = 10 * num_at_coords(DIGIT_REGIONS[3]) + num_at_coords(DIGIT_REGIONS[2])
    minutes = 10 * num_at_coords(DIGIT_REGIONS[5]) + num_at_coords(DIGIT_REGIONS[4])
    hours = 10 * num_at_coords(DIGIT_REGIONS[7]) + num_at_coords(DIGIT_REGIONS[6])
    return (hours, minutes, seconds, frames)

def num_at_coords(coords):
    """ Return: integer """
    for i, num in enumerate(NUMS):
        try:
            pyautogui.locateOnScreen(num, region=coords, grayscale=True)
            return i
        except Exception:
            pass
    raise Exception("Could not find any digit")

if __name__ == "__main__":
    main()
