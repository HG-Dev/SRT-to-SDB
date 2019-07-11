from collections import namedtuple

#{"top": 160, "left": 160, "width": 160, "height": 135}

Region = namedtuple('Region', ['top', 'left', 'width', 'height'])
test = Region(0,0,1920,1080)
print(test)
print(test.top)
print(test._asdict()['top'])
