import threading
import requests as reqs
import os
import base64
import json
from datetime import datetime, date
from time import time

from .turnstile import Turnstile
from .cameras import Cameras
from . import settings


class Entrance:

    MIN_REP_ENT_INTERVAL = 3

    def __init__(self):
        os.environ['NO_PROXY'] = settings.face_host
        self.cameras = Cameras(
            settings.camera_in, settings.camera_out,
            settings.user, settings.password,
            settings.crop_coordinates
        )
        self.turnstile = Turnstile(settings.turnstile_host)
        self.last_entered_id = None
        self.last_exit_id = None
        self.last_entered_time = 0
        self.last_exit_time = 0
        self.today = date.today()

    
    def catch_values(self):
        self.turnstile.get_distances()
        side = 'none'

        if self.turnstile.distance_in <= settings.max_dist:
            self.cameras.in_camera_photo()
            side = 'in'
            
            if self.turnstile.distance_out <= settings.max_dist:
                self.cameras.out_camera_photo()
                side = 'both'
            
        elif self.turnstile.distance_out <= settings.max_dist:
            self.cameras.out_camera_photo()
            side = 'out'
        
        return side


    def take_action(self):
        params = {}
        if self.turnstile.distance_in <= settings.max_dist:
            resp_body = self.__who_is_there(settings.face_in, self.cameras.photo_in, settings.thresh)
            params = self.__get_action_params(resp_body, self.cameras.photo_in, 'in')
            if params['action'] == 'in':
                if params['emp_id'] != self.last_entered_id and str(params['emp_id']) != '-1':   
                    self.turnstile.let_customer_in()
                    self.last_entered_id = params['emp_id']
                    self.last_entered_time = time()
                
                elif time() - self.last_entered_time >= self.MIN_REP_ENT_INTERVAL:
                    self.turnstile.let_customer_in()
                    self.last_entered_id = params['emp_id']
                    self.last_entered_time = time()  
                
                else:
                    params = {}

        if self.turnstile.distance_out <= settings.max_dist:

            resp_body = self.__who_is_there(settings.face_out, self.cameras.photo_out, settings.thresh)
            params = self.__get_action_params(resp_body, self.cameras.photo_out, 'out')
            print("params['emp_id']")
            print(params['emp_id'])
            print("self.last_exit_id")
            print(self.last_exit_id)
            if params['action'] == 'out':
                if params['emp_id'] != self.last_exit_id and str(params['emp_id']) != '-1':
                    self.turnstile.let_customer_out()
                    self.last_exit_id = params['emp_id']
                    self.last_exit_time = time()

                elif time() - self.last_exit_time >= self.MIN_REP_ENT_INTERVAL:
                    self.turnstile.let_customer_out()
                    self.last_exit_id = params['emp_id']
                    self.last_exit_time = time()

                else:
                    params = {}

        return params


    def reset_values(self):
        self.cameras.reset_photos()
        self.turnstile.reset_distances()


    def getBirthdayList(self, http_addr):
        try:
           resp = reqs.post(http_addr + '/birthday_list', verify=False)
           return json.loads(resp.content.decode('utf-8'))

        except:
           return {}


    def updateBirthdayList(self, http_addr):
        if self.today != date.today():
            self.today = date.today()
            self.getBirthdayList(http_addr)



    def __who_is_there(self, http_addr, photo, thresh):
        params = {'img_bytes' : base64.b64encode(photo), 
                  'threshold' : thresh}

        resp = reqs.post(http_addr+'/recognize_two_layer', data=params)
        if resp.status_code == 200:
            return json.loads(resp.content.decode('utf-8'))
        
        return -1                 # failed request


    def __get_action_params(self, resp_body, photo, action):
       emp_id = -1
       _action = 'noa'
       desc = 'no desc'
       face_locations = []
       face_distance = -1.0

       
       if resp_body == -1:
           desc = 'failed request'
       
       else:
           st_code = resp_body['status_code']
           if st_code == 1:
               desc = 'corrupted image'
           elif st_code == 2:
               desc = 'no face'
           elif st_code == 3:
               desc = 'many faces'
           elif st_code == 9:
               desc = 'unknown face'
               face_locations = resp_body['face_locations'][0]
               face_distance = resp_body['face_distance']
           elif st_code == 0:
               desc = 'OK'
               _action = action
               emp_id = resp_body['client_id']
               face_locations = resp_body['face_locations'][0]
               face_distance = resp_body['face_distance']
       
       return {
           'emp_id' : emp_id,
           'action' : _action,
           'reg_photo' : photo,
           'descr' : desc,
           'dist_in' : self.turnstile.distance_in,
           'dist_out' : self.turnstile.distance_out,
           'face_locations' : face_locations,
           'face_distance' : face_distance
       }   





   
