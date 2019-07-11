""" Tests SRT library and creates SRT file for testing with main """

from datetime import timedelta
from srt.srt import *

interval = timedelta(seconds=1)
content = ["Test 1", "Hello, and again,", "welcome to the Aperture Science\ncomputer-aided enrichment center."]
subtitles = [Subtitle(index=1, start=interval*(x*3+1), end=interval*(x*3+2), content=content[x]) for x in range(3)]
print(compose(subtitles))

old = """
digit_found_regions = []
for i, num in enumerate(NUMS):
    print("Looking for {}".format(num))
    for region in pyautogui.locateAllOnScreen(num, grayscale=True):
        digit_found_regions.append(region)
if not digit_found_regions:
    raise Exception("Searched the screen for TC digits, but couldn't find any.")
digit_found_regions.sort(key=lambda r: r.left - r.top)
tc_start_region = digit_found_regions[0]
for i in range(8):
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
"""