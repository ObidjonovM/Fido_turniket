import requests as reqs
import time
from sys import exc_info
from PIL import Image
import io
import os

os.environ['NO_PROXY'] = '10.50.71.240'

class Cameras:

    def __init__(self, host_in, host_out, crop_coors):
        self.__host_in = host_in
        self.__host_out = host_out
        self.__crop_in = crop_coors['in']
        self.__crop_out = crop_coors['out']
        self.__photo_in = b'EMPTY'
        self.__photo_out = b'EMPTY' 


    def __get_photo(self, host):
        try:
            resp =  reqs.post(
                host,
                timeout=3,                        # waits 3 seconds before timing out
                verify=False
            )
            if resp.status_code == 200:
                return resp.content
            
            else:
                return b'Timed out waiting for photo'    

        except reqs.exceptions.ConnectionError:
            return b'Connection aborted'

        except:
            return b'Photo could not be taken'


    def __crop_photo(self, photo, crop_coors):
        try:
            img = Image.open(io.BytesIO(photo))
            crop_img = img.crop(crop_coors)
            crop_img.save('cropped.jpg')
            with open('cropped.jpg', 'rb') as f:
                crop_bytes = f.read()
        except:
            print('Photo could not be cropped')
            crop_bytes = b'NO_PHOTO'
        finally:
            if os.path.exists('cropped.jpg'):
                os.remove('cropped.jpg')
        
        return crop_bytes   


    def in_camera_photo(self):
        photo = self.__get_photo(self.__host_in)
        photo = self.__crop_photo(photo, self.__crop_in)
        if photo != b'NO_PHOTO':
            self.__photo_in = photo


    def out_camera_photo(self):
        photo = self.__get_photo(self.__host_out)
        photo = self.__crop_photo(photo, self.__crop_out)
        if photo != b'NO_PHOTO':
            self.__photo_out = photo


    @property
    def photo_in(self):
        return self.__photo_in

    @property
    def photo_out(self):
        return self.__photo_out

