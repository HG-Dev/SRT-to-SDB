""" Tests SRT library and creates SRT file for testing with main """

from datetime import timedelta
from srt.srt import *

interval = timedelta(seconds=1)
content = ["Test 1", "Hello, and again,", "welcome to the Aperture Science\ncomputer-aided enrichment center."]
subtitles = [Subtitle(index=1, start=interval*(x*3+1), end=interval*(x*3+2), content=content[x]) for x in range(3)]
print(compose(subtitles))

