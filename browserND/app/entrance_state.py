import os
from os.path import join, exists
from datetime import datetime
import pickle
from sys import exc_info

class EntranceState:

    def __init__(self):
        self.__measurement_id = None
        self.__requested_time = 0
        self.__photo_in = ""
        self.__photo_out = ""
        self.__birthdays = {}
        self.__name_id_map = {}            # name id map for all employees
        self.__temp_folder = None
        self.__setup_temp_folder('temp')
        self.__cel_path = self.setup_celebrated_list()['cl_path']
        
    

    def __setup_temp_folder(self, temp_folder):
        if not exists(temp_folder):
            os.mkdir(temp_folder)

        self.__temp_folder = temp_folder
            

    def setup_birthday_list(self, birthdays):
        from_cl_file = pickle.load(
            open(self.__cel_path,'rb')
        )
        from_cl_file['birthdays'] = birthdays
        pickle.dump(
            from_cl_file,
            open(self.__cel_path, 'wb')
        )
        self.__birthdays = {
            'date' : datetime.now().today(),
            'birthdays' : birthdays
        }


    def is_birthday_list_current(self):
        if 'date' in self.__birthdays.keys():
            if datetime.now().today() == self.__birthdays['date']:
                return True
        
        return False


    def setup_celebrated_list(self):
        today = datetime.now().today()
        files = os.listdir(self.__temp_folder)
        cl_file = f'celebrated_{today.day}_{today.month}_{today.year}.pickle'

        # removing older celebrated_list files
        for f in files:
            if f.startswith('celebrated') and f != cl_file:
                os.remove(
                    join(self.__temp_folder, f)
                )
        
        # check if cl_file exists
        cl_path = join(self.__temp_folder, cl_file)
        if exists(cl_path):
            return {
                'status_code' : 1,
                'status' : f'{cl_path} already exists',
                'cl_path' : cl_path
            }
        else:
            cel_list =  {
                'cl_path' : cl_path,
                'today' : f'{today.day}/{today.month}/{today.year}',
                'the_list' : []
            }

            if 'birthdays' in self.__birthdays.keys():
                cel_list['birthdays'] = self.__birthdays['birthdays']
            else:
                cel_list['birthdays'] = {}

            pickle.dump(
                cel_list,
                open(cl_path, 'wb')
            )
            return {
                'status_code' : 2,
                'status' : f'New {cl_path} path was created',
                'cl_path' : cl_path
            }


    def is_celebrated_list_current(self):
        today = datetime.now().today()
        cl_path = join(
            self.__temp_folder,
            f'celebrated_{today.day}_{today.month}_{today.year}.pickle'
        )

        return cl_path == self.__cel_path



    def is_celebrated_path_current(self):
        today = datetime.now().today()
        cl_file = f'celebrated_{today.day}_{today.month}_{today.year}.pickle'
        return self.__cel_path == cl_file


    def reset_birthday_fields(self):
        self.__temp_folder = None
        self.__setup_temp_folder('temp')
        self.__cel_path = self.setup_celebrated_list()['cl_path']

        
    def add_to_celebrated_list(self, client_id):
        try:
            from_cl_file = pickle.load(
                open(self.__cel_path,'rb')
            )
            from_cl_file['the_list'].append(client_id)
            pickle.dump(
                from_cl_file,
                open(self.__cel_path, 'wb')
            )
            return True
        except:
            return False


    def is_celebrated(self, client_id):
        try:
            from_cl_file = pickle.load(
               open(self.__cel_path, 'rb') 
            )
            if client_id in from_cl_file['birthdays'].keys():
                result = {
                    'status' : 'OK',
                    'birthday' : True,
                    'name' : from_cl_file['birthdays'][client_id]
                }
                if client_id in from_cl_file['the_list']:
                    result['celebrated'] = True
                else:
                    result['celebrated'] = False
                return result
            else:
                return {
                    'status' : 'OK',
                    'birthday' : False,
                    'celebrated' : False
                }
        except:

            return {
                'status' : f'Error - {exc_info()[0]} : {exc_info()[1]}',
                'birthday' : False,
                'celebrated' : False
            }


    def getMeasurementId(self):
        return self.__measurement_id


    def getRequestedTime(self):
        return self.__requested_time


    def setMeasurementId(self, newId):
        self.__measurement_id = newId


    def setRequestedTime(self, newTime):
        self.__requested_time = newTime


    def incrMeasurementId(self, inc_by = 1):
        self.__measurement_id += inc_by


    def getPhotoIn(self):
        return self.__photo_in


    def setPhotoIn(self, photo_in):
        self.__photo_in = photo_in


    def getPhotoOut(self):
        return self.__photo_out


    def setPhotoOut(self, photo_out):
        self.__photo_out = photo_out


    def getClientNameIdMap(self):
        return self.__name_id_map


    def setClientNameIdMap(self, name_id_map):
        self.__name_id_map = name_id_map


    

    def reset(self):
        self.__measurement_id = None
        self.__requested_time = 0
        self.__photo_in = ""
        self.__photo_out = ""

