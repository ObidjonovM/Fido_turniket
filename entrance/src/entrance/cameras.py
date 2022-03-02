import requests as reqs
import time
from sys import exc_info
from PIL import Image
import io
import os
from hikvisionapi import Client

os.environ['NO_PROXY'] = '10.50.71.240'

class Cameras:

    def __init__(self, host_in, host_out, admin, password, crop_coors):
        self.__crop_in = crop_coors['in']
        self.__crop_out = crop_coors['out']
        self.__photo_in = b'EMPTY'
        self.__photo_out = b'EMPTY'
        self.__old_photo_in = b'OLD_EMPTY'
        self.__old_photo_out = b'OLD_EMPTY'
        self.camera_in = Client(host_in, admin, password, timeout=3)
        self.camera_out = Client(host_out, admin, password, timeout=3)



    def reset_photos(self):
        self.__photo_in = b'EMPTY'
        self.__photo_out = b'EMPTY'        


    def __get_photo(self, camera):
        try:
            response = camera.Streaming.channels[102].picture(
                method='get', type='opaque_data'
            )
            if response.status_code == 200:
                return response.content
            else:
                return b'Timed out waiting for photo'
        except:
            return b'Photo could not be taken'


    def __crop_photo(self, photo, crop_coors):
        crop_bytes = b''
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
            img.close()
            crop_img.close()
            if os.path.exists('cropped.jpg'):
                os.remove('cropped.jpg')

        return crop_bytes   


    def get_camera_photo(self, camera, crop_coors):
        photo = self.__get_photo(camera)
        photo = self.__crop_photo(photo, crop_coors)
        if photo != b'NO_PHOTO':
            return photo
    
        return b''


    def different_photos(self,photo1, photo2):
        return not (photo1 == photo2)


    def in_camera_photo(self):
        self.__old_photo_in = self.__photo_in
        photo = self.get_camera_photo(self.camera_in, self.__crop_in)
        if self.different_photos(photo, self.__old_photo_in):
            if photo != b'':
                self.__photo_in = photo
        else:
            self.__photo_in = b'NO CHANGE IN PHOTO'


    def out_camera_photo(self):
        self.__old_photo_out = self.__photo_out
        photo = self.get_camera_photo(self.camera_out, self.__crop_out)
        if self.different_photos(photo, self.__old_photo_out):
            if photo != b'':
                self.__photo_out = photo
        else:
            self.__photo_out = b'NO CHANGE IN PHOTO'


    @property
    def photo_in(self):
        return self.__photo_in


    @property
    def photo_out(self):
        return self.__photo_out