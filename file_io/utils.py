''' JSON dict IO '''

import json
from os import rename, remove

class FileIO:
    ''' Collection of static methods for getting stuff out of files. '''
    @staticmethod
    def get_json_dict(filepath):
        ''' Returns the entire JSON dict in a given file. '''
        with open(filepath, encoding="utf8") as infile:
            return json.load(infile)

    @staticmethod
    def save_json_dict(filepath, dictionary):
        ''' Saves a JSON dict, overwriting or creating a given file. '''
        if not any(dictionary):
            return False
        with open(filepath+".tmp", 'w', encoding="utf8") as outfile:
            json.dump(dictionary, outfile, ensure_ascii=False, indent=4)
        try:
            remove(filepath)
        except FileNotFoundError:
            pass
        rename(filepath+".tmp", filepath)
        return True

    @staticmethod
    def test_dict_safety(dictionary):
        try:
            return json.dumps(dictionary, ensure_ascii=False, indent=4)
        except TypeError as e:
            print("This dictionary cannot be saved.\n{}".format(str(e)))
            short_typename = str(e).split()[3]
            for key, val in dictionary.items():
                if short_typename in str(type(val)):
                    print("{} is a {}.".format(key, type(val)))
                    print(val)
                    print("Please implement a JSON safe serialization method.")
            return False
        return True
        
