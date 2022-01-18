import base64
from PIL import Image
from io import BytesIO
import numpy as np

def extract_base64(jpeg_base64):
    start_pos = jpeg_base64.find("/9j")
    if start_pos > -1:
        return jpeg_base64[start_pos:]

    return ""


def make_fullname(fname, lname, mname):
    return f"{lname} {fname} {mname}"


def bytesTobase64(_bytes):
    return base64.b64encode(_bytes)


def parse_fullname(fullname):
    fullname_list = fullname.split()
    fullname_parserd = {}
    fullname_parserd['lname'] = fullname_list[0]
    fullname_parserd['fname'] = fullname_list[1]
    if len(fullname_list) > 3:
        fullname_parserd['mname'] = " ".join(fullname_list[2:])
    else:
        fullname_parserd['mname'] = fullname_list[2]
    
    return fullname_parserd
