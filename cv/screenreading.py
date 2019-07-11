''' Compile-time configuration data for hg_tweetfeeder.bot '''
import cv2
import numpy as np
from collections import namedtuple
from ast import literal_eval
from pyautogui import size
from mss import mss
from file_io.utils import FileIO as IO
from json import JSONDecodeError

Region = namedtuple('Region', ['left', 'top', 'width', 'height'])
SCREEN = mss()
#cv2.namedWindow("OpenCV Debug", cv2.WINDOW_NORMAL)

class CharPattern:
    """
    A binary pattern describing unique on/off points for one character.
    (char, bitmap, save_to_file)
    """
    SIG_FULL = 0
    SIG_OPTIMIZED = 1
    SAVEPATH = "config/char_{}.txt"

    def __init__(self, char, bitmap=None, save_to_file=False):
        ''' Load information from a file if it exists '''
        self.char = char        #The char this pattern represents
        self.bitmap = bitmap    #A numpy array for white/black image data
        self.signature = {}     #A python dict of [x y]:[True or False]
        if bitmap is None:
            #Assume file exists, try to update from it
            self.__dict__.update(self._savedata)
        if not any(self.signature):
            self.generate_signature()
        if save_to_file and char:
            self._save()

    @property
    def _savedata(self):
        """
        If the class is uninitialized, returns a dictionary that can be used
        to reinstantiate the class. Otherwise, returns a dictionary that can be
        saved as JSON to reinstantiate this class later.
        return {"bitmap":[], "signature":self.signature}
        """
        output = {}
        if self.bitmap is None:
            try:
                json_dict = IO.get_json_dict(self.SAVEPATH.format(self.char))
                output["bitmap"] = np.asarray(json_dict["bitmap"], np.uint8)
                output["signature"] = {
                    literal_eval(key): val
                    for key, val in json_dict["signature"].items()
                }
            except FileNotFoundError:
                #No prior file exists
                pass
        else:
            # Prepare to save. We know at least that bitmap exists
            output = {}
            try:
                output["bitmap"] = self.bitmap.tolist()
            except AttributeError:
                output["bitmap"] = self.bitmap
            output["signature"] = {
                "({}, {})".format(key[0], key[1]): val
                for key, val in self.signature.items()
            }
        return output

    def _save(self):
        ''' Save to file to conserve signature processing time '''
        if IO.test_dict_safety(self._savedata):
            IO.save_json_dict(self.SAVEPATH.format(self.char), self._savedata)

    def import_bitmap(self, img):
        ''' Create binary string from image data '''
        self.bitmap = img
        self.generate_signature()

    def generate_signature(self, method=0, other_img=None):
        """
        A signature dictionary is a key->bool series used to tell if a given
        image contains a certain character.
        Add/subtract images to find unique points
        For each other character, subtract one from the other to find
        one "on" point and one "off" point
        """
        if self.bitmap is None:
            return None
        if method == self.SIG_OPTIMIZED:
            raise NotImplementedError()
        else:
            self.signature.clear()
            width = self.bitmap.shape[1]
            x, y = (0, 0)
            for i, cell in enumerate(np.nditer(self.bitmap)):
                self.signature[(int(i/width), i % width)] = bool(cell)

        return self.signature

    def signature_match(self, bin_img, threshold=0.95):
        """
        Takes a binary image (each pixel 0 or not 0) and applies
        the signature dictionary to the image to confirm a match.
        """
        if not any(self.signature):
            if not any(np.nditer(bin_img)):
                return True
            return False
        incorrect = 0
        total = len(self.signature.items())
        for element, active in self.signature.items():
            if bool(bin_img[element]) != active:
                incorrect += 1
        if (total - incorrect) / total > threshold:
            return True
        return False

class ScreenReader:
    ''' Acquires visual information from the screen like digits. '''
    DIGIT_PATTERNS = [CharPattern(str(x)) for x in range(10)]
    FULLSCREEN_REGION = Region(0, 0, size()[0], size()[1])
    DEBUG_IMG = np.zeros((11, 7), np.uint8)

    def __init__(self):
        '''  '''
        self._total_tweets = 0

    @staticmethod
    def FindPatternRegionsOnScreen(patterns, region: Region):
        """
        Returns a list of regions at which one can find
        successfully identified patterns.
        """
        screen_grab = SCREEN.grab(ScreenReader.FULLSCREEN_REGION._asdict())
        search_img = np.array(screen_grab)
        s_width, s_height = screen_grab.size
        if not region:
            region = Region(0, 0, s_width, s_height)
        else:
            x, y, w, h = region
            if (x > s_width
                or y > s_height
                or w > s_width
                or y > s_height):
                raise ValueError("Given region exceeds the bounds of the screen.")
        #Crop search area from original screen grab
        search_img = search_img[
            region.top:region.top+region.height,
            region.left:region.left+region.width
        ]
        search_img = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)
        search_img = cv2.threshold(search_img, 140, 255, cv2.THRESH_BINARY)[1]
        output = []
        for digit in ScreenReader.DIGIT_PATTERNS:
            search_res = cv2.matchTemplate(search_img, digit.bitmap, cv2.TM_CCOEFF_NORMED)
            search_res = np.where(search_res >= 0.95)
            #Ideally, all hits should be unique
            output = [*output, *[(y + region.top, x + region.left, digit.char) for (y, x) in zip(*search_res)]]
        return output

    @staticmethod
    def MatchPatternAtRegion(patterns, region: Region):
        """
        Given a Region, go through a list of patterns until
        a signature matches the content of the region.
        """
        search_img = np.array(SCREEN.grab(region._asdict()))
        search_img = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)
        search_img = cv2.threshold(search_img, 140, 255, cv2.THRESH_BINARY)[1]
        ScreenReader.DEBUG_IMG = np.concatenate((ScreenReader.DEBUG_IMG, search_img), axis=1)
        cv2.imshow("OpenCV Debug", ScreenReader.DEBUG_IMG)
        #cv2.resizeWindow("OpenCV Debug", ScreenReader.DEBUG_IMG.shape[1] * 10, ScreenReader.DEBUG_IMG.shape[0] * 10)
        for pattern in patterns:
            if pattern.signature_match(search_img):
                return pattern.char
        raise ValueError("No pattern matched given region.")

    @staticmethod
    def MatchPatternRegions(patterns, regions):
        """
        Given a list of patterns and regions,
        deliver a single string that represents them.
        """
        assert len(patterns) > 1
        output_str = ""
        for region in regions:
            output_str += ScreenReader.MatchPatternAtRegion(patterns, region)
        return output_str


    @staticmethod
    def QueryUserForPatternFound():
        """
        Idea: Reduce search time by asking the user to make a
        rectangle around the area that must be searched
        """
        pass
