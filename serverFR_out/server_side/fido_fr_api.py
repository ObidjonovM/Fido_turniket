from face_recognition.api import face_encodings
from flask_restful import Resource, reqparse
import numpy as np
import face_recognition as fr
import base64
from PIL import Image
from io import BytesIO
from collections import OrderedDict
import numpy as np
import requests



class MotherApiClass(Resource):
    
    def __init__(self, id_encodings_map):
        super().__init__()
        self.id_encodings_map = id_encodings_map
        self.img_bytes = None
        self.client_id = None
        self.threshold = None
        self.photo_arr = None
        self.parser = self.__set_up_parser() 


    def __set_up_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument("img_bytes", type=str, required=True, help="image bytes are not provided")
        parser.add_argument("client_id", type=int, required=True, help="Invalid client ID")
        return parser


    def get_args(self):
        args = self.parser.parse_args()
        self.img_bytes = args["img_bytes"]
        self.client_id = args["client_id"]



    def __set_photo_arr(self):
        try:
            im = Image.open(BytesIO(base64.b64decode(self.img_bytes)))
            im = im.convert('RGB')
            self.photo_arr = np.array(im)
            return True

        except:
            return False


    def get_photo_arr(self):
        return self.photo_arr


    def reset_last_inputs(self):
        self.img_bytes = None
        self.client_id = None
        self.threshold = None
        self.photo_arr = None


    def get_largest_face_index(self, face_locations):
        areas = []
        for fc in face_locations:
            top, right, bottom, left = fc
            areas.append(abs((bottom-top)*(right-left)))
        
        return areas.index(max(areas))



    def get_face_locations(self, img_path, one_person_photo=True):
        if self.__set_photo_arr():
            face_locations = fr.face_locations(self.photo_arr)
        else:
            return {
                "status_code" : 1,
                "status" : "Provided photo is not valid",
                "face_locations" : []
            }
        if face_locations == []:
            return {
                "status_code" : 2,
                "status" : "No face was detected in the given photo",
                "face_locations" : []
            }

        if len(face_locations) > 1:
            fi = self.get_largest_face_index(face_locations)
            face_locations = [face_locations[fi]]
            if one_person_photo:
                return {
                    "status_code" : 3,
                    "status" : "More than one face is detected in the given photo",
                    "face_locations" : []
                }
            else:
                fi = self.get_largest_face_index(face_locations)
                face_locations = [face_locations[fi]]

        return {
            "status_code" : 0,
            "status" : "OK",
            "face_locations" : face_locations
        }


class FidoFaceRecognitionApi:

    id_encs_url = None
    extra_id_encs_url = None
    up_to_date = {
        'add_client' : True,
        'get_distance' : True,
        'remove_client' : True
    }


    @staticmethod
    def load_data():
        resp = requests.post(FidoFaceRecognitionApi.id_encs_url, verify=False).json()
        return {k : np.array(v) for (k,v) in resp.items()}    


    @staticmethod
    def load_extra_data():
        resp_dict = {}
        resp = requests.post(FidoFaceRecognitionApi.extra_id_encs_url, verify=False).json()
        for k, vectors in resp.items():
            resp_dict[k] = []
            for vector in vectors:
                resp_dict[k].append(np.array(vector))
        
        return resp_dict


    def __init__(self, id_encs_url, extra_encs_url):
        FidoFaceRecognitionApi.id_encs_url = id_encs_url
        FidoFaceRecognitionApi.extra_id_encs_url = extra_encs_url
        self.id_encodings_map = FidoFaceRecognitionApi.load_data()
        self.extra_id_encodings_map = FidoFaceRecognitionApi.load_extra_data()


    # def __load_data(self):
    #     resp = requests.post(self.id_encs_url, verify=False).json()
    #     return {k : np.array(v) for (k,v) in resp.items()}


    # def __load_extra_data(self):
    #     resp_dict = {}
    #     resp = requests.post(self.extra_id_encs_url, verify=False).json()
    #     for k, vectors in resp.items():
    #         resp_dict[k] = []
    #         for vector in vectors:
    #             resp_dict[k].append(np.array(vector))
        
    #     return resp_dict


    def get_id_encodings_map(self):
        return FidoFaceRecognitionApi.load_data()


    def get_extra_id_encodings_map(self):
        return FidoFaceRecognitionApi.load_extra_data()


    class AddClient(MotherApiClass):

        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)


        def __add_record(self, encs, id):
            if id in self.id_encodings_map.keys():
                return False
            self.id_encodings_map[id] = encs
            return True


        def post(self):
            self.reset_last_inputs()
            self.get_args()
            face_locations = self.get_face_locations(self.img_bytes)
            if face_locations["status"] == "OK":
                face_encodings = fr.face_encodings(
                    self.get_photo_arr(),
                    face_locations["face_locations"]
                )[0]
                if self.__add_record(face_encodings, self.client_id):
                    return {
                        "status_code" : 4,
                        "status" : f"Client {self.client_id} has been added to the database.",
                        "face_encodings" : np.array_str(face_encodings)
                    }
                return {
                        "status_code" : 5,
                        "status" : f"Client {self.client_id} already exists in the database."
                }
            return {
                "status_code" : face_locations["status_code"],
                "status" : face_locations["status"]
            }


    class GetDistance(MotherApiClass):

        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)    


        def calculate_distance(self, face_locations):
            face_encodings = fr.face_encodings(
                self.get_photo_arr(),
                face_locations
            )[0]
            distance = fr.face_distance(
                [self.id_encodings_map[self.client_id]],
                face_encodings
            )
            return np.sum(distance)   


        def get(self):
            self.reset_last_inputs()
            self.get_args()
            if self.client_id in self.id_encodings_map.keys():
                face_locations = self.get_face_locations(self.img_bytes)
                if face_locations["status"] == "OK":
                    distance = self.calculate_distance(
                        face_locations["face_locations"]
                    )
                    return {
                        "status_code" : 0,
                        "status" : "OK",
                        "distance" : distance
                    }
                return {
                    "status_code" : face_locations["status_code"],
                    "status" : face_locations["status"],
                    "distance" : -1
                }
            return {
                "status_code" : 6,
                "status" : f"Client with ID = {self.client_id} is not found in the database",
                "distance" : -1
            }


    class RemoveClient(MotherApiClass):

        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)


        def get_args(self):
            parser = self.parser.copy()
            parser.remove_argument("img_bytes")
            args = parser.parse_args()
            self.client_id = args["client_id"]
            

        def delete(self):
            self.reset_last_inputs()
            self.get_args()

            if str(self.client_id) in self.id_encodings_map.keys():
                del self.id_encodings_map[self.client_id]
                return {
                    "status_code" : 7,
                    "status" : f"Client with ID {self.client_id} is removed from database"
                }
            return {
                "status_code" : 8,
                "status" : f"Client with ID {self.client_id} is not found in database"
            }


    class Recognize(MotherApiClass):
        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)


        def get_args(self):
            parser = self.parser.copy()
            parser.add_argument("threshold", type=float, required=True, help="Threshold value is not provided")
            parser.remove_argument("client_id")
            args = parser.parse_args()
            self.img_bytes = args["img_bytes"]
            self.threshold = args["threshold"]


        def post(self):
            self.reset_last_inputs()
            self.get_args()
            face_locations = self.get_face_locations(self.img_bytes, False)
            if face_locations["status"] == "OK":
                client_ids = list(self.id_encodings_map.keys())
                encodings = list(self.id_encodings_map.values())
                face_enc = fr.face_encodings(
                    self.get_photo_arr(),
                    face_locations["face_locations"]
                )[0]
                distances = fr.face_distance(
                    encodings,
                    face_enc
                )
                min_dist_index = np.argmin(distances)
                if distances[min_dist_index] <= self.threshold:
                    return {
                        "status_code" : 0,
                        "status" : "OK",
                        "client_id" : client_ids[min_dist_index]
                    }
                return {
                    "status_code" : 9,
                    "status" : "This person could not be recognized",
                    "client_id" : -1
                }
            return {
                "status_code" : face_locations["status_code"],
                "status" : face_locations["status"],
                "client_id" : -1
            }


    class GetClientIDs(MotherApiClass):
        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)


        def get(self):
            return {
                "client_ids" : list(self.id_encodings_map.keys())
            }


    class UpdateCustomerPhoto(MotherApiClass):
        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)


        def __customer_exists(self, id):
            return str(id) in self.id_encodings_map.keys()


        def __update_customer(self, encs, id):
            try:
                self.id_encodings_map[id] = encs
                return True
            except BaseException as err:
                print(f"The record could not be updated: {err}")
                return False


        def post(self):
            self.reset_last_inputs()
            self.get_args()
            if self.__customer_exists(self.client_id):
                face_locations = self.get_face_locations(self.img_bytes)
                if face_locations["status"] == "OK":
                    face_encodings = fr.face_encodings(
                        self.get_photo_arr(),
                        face_locations["face_locations"]
                    )[0]
                    if self.__update_customer(face_encodings, self.client_id):
                        return {
                            "status_code" : 0,
                            "face_encodings" : np.array_str(face_encodings),
                            "status" : "OK"
                        }
                    return {
                        "status_code" : 9,
                        "status" : "Mijoz rasmi yangilanmadi"
                    }
                return {
                        "status_code" : face_locations["status_code"],
                        "status" : face_locations["status"]
                    }
            return {
                "status_code" : 10,
                "status" : "Mijoz IDsi bazada topilmadi"
            }


    class PhotoEncodings(MotherApiClass):
        
        def __init__(self, id_encodings_map):
            super().__init__(id_encodings_map)
            

        def post(self):
            self.reset_last_inputs()
            self.get_args()
            face_locations = self.get_face_locations(self.img_bytes)
            if face_locations["status"] == "OK":
                try:
                    face_encodings = fr.face_encodings(
                        self.get_photo_arr(),
                        face_locations["face_locations"]
                    )[0]

                except:
                    return {
                        "status_code" : 11,
                        "status" : "Mijoz kodirovkasi aniqlanmadi"
                    }

                return {
                    "status_code" : 0,
                    "status" : "OK",
                    "face_encodings" : np.array_str(face_encodings)
                }
            
            return {
                "status_code" : face_locations["status_code"],
                "status" : face_locations["status"]
            }


    class RecognizeTwoLayers(Recognize):

        def __init__(self, id_encodings_map, extra_id_encodings_map):
            super().__init__(id_encodings_map)
            self.extra_id_encodings_map = extra_id_encodings_map


        def get_closest_ids(self, face_enc, num_indexes, max_val=1):
            closest_ids = OrderedDict()
            client_ids = list(self.id_encodings_map.keys())
            encodings = list(self.id_encodings_map.values())
            distances = fr.face_distance(encodings, face_enc)

            for _ in range(num_indexes):
                min_dist_index = np.argmin(distances)
                closest_ids[client_ids[min_dist_index]] = distances[min_dist_index]
                distances[min_dist_index] = max_val

            return closest_ids


        def get_best_match(self, face_enc, closest_ids):
            best_match = -1
            min_aver_dist = float('inf')

            for k,v in closest_ids.items():
                if k not in self.extra_id_encodings_map:        # in case client_id does not exist in extra_id_encodings_map
                    return {
                        "client_id" : closest_ids.popitem(False)[0],        # return the client_id with a closest distance
                        "face_distance" : 0                   # TODO later !!!!!!!
                    }

                distances = fr.face_distance(
                    np.array(self.extra_id_encodings_map[k]), 
                    face_enc
                )
                aver_dist = (np.sum(distances) + v) / (len(distances) + 1)
                if aver_dist < min_aver_dist:
                    min_aver_dist = aver_dist
                    best_match = int(k)

            if min_aver_dist <= self.threshold:
                return {
                    "client_id" : int(best_match),
                    "face_distance" : min_aver_dist
                }

            return {
                    "client_id" : -1,
                    "face_distance" : min_aver_dist
                }


        def post(self):
            self.reset_last_inputs()
            self.get_args()
            face_locations = self.get_face_locations(self.img_bytes, False)

            if face_locations["status"] == "OK":
                face_enc = fr.face_encodings(
                    self.get_photo_arr(),
                    face_locations["face_locations"]
                )[0]

                closest_ids = self.get_closest_ids(face_enc, 3)
                best_match = self.get_best_match(face_enc, closest_ids)

                if best_match["client_id"] != -1:
                    return {
                        "status_code" : 0,
                        "status" : "OK",
                        "client_id" : best_match["client_id"],
                        "face_locations" : face_locations["face_locations"],
                        "face_distance" : best_match["face_distance"]
                        }

                else:
                    return {
                    "status_code" : 9,
                    "status" : "This person could not be recognized",
                    "client_id" : -1,
                    "face_locations" : face_locations["face_locations"],
                    "face_distance" : best_match["face_distance"]
                    }

            return {
                "status_code" : face_locations["status_code"],
                "status" : face_locations["status"],
                "client_id" : -1,
                "face_locations" : [],
                "face_distance" : -1
            }
