from os import path
import re


def escape_path(path):
    return path.replace(' ', '\ ')


def extract_gopro_id(file_name):
    '''return ID of given video file name, as string'''
    pattern = 'GOPR(.*).MP4'
    m = re.search(pattern, file_name)
    if m:
        return m.group(1)


def get_gopro_fragment_name(gopro_id, fragment_id):
    return 'GP{}{}.MP4'.format(format(fragment_id, '02'), gopro_id)
