from flask import Flask
from flask_restful import Api
from .fido_fr_api import FidoFaceRecognitionApi


class FidoEntrance:

    def __init__(self, gateway_name, enc_id_url, extra_enc_id_url):
        
        self.app = Flask(gateway_name)
        self.api = Api(self.app)
        self.entrance_greet = FidoFaceRecognitionApi(enc_id_url, extra_enc_id_url)

        self.api.add_resource(
            self.entrance_greet.AddClient,
            "/add_client",
            resource_class_kwargs  = {"id_encodings_map" : self.entrance_greet.get_id_encodings_map()}
        )

        self.api.add_resource(
            self.entrance_greet.GetDistance,
            "/get_distance",
            resource_class_kwargs  = {"id_encodings_map" : self.entrance_greet.get_id_encodings_map()}
        )

        self.api.add_resource(
            self.entrance_greet.RemoveClient,
            "/remove_client",
            resource_class_kwargs  = {"id_encodings_map" : self.entrance_greet.get_id_encodings_map()}
        )

        self.api.add_resource(
            self.entrance_greet.Recognize,
            "/recognize",
            resource_class_kwargs = {
                "id_encodings_map" : self.entrance_greet.get_id_encodings_map(),
            }
        )

        self.api.add_resource(
            self.entrance_greet.GetClientIDs,
            "/get_clients",
            resource_class_kwargs = {"id_encodings_map" : self.entrance_greet.get_id_encodings_map()}
        )

        self.api.add_resource(
            self.entrance_greet.UpdateCustomerPhoto,
            "/update_client_photo",
            resource_class_kwargs = {"id_encodings_map" : self.entrance_greet.get_id_encodings_map()}
        )

        self.api.add_resource(
            self.entrance_greet.PhotoEncodings,
            "/photo_encodings",
            resource_class_kwargs = {"id_encodings_map" : self.entrance_greet.get_id_encodings_map()}
        )

        self.api.add_resource(
            self.entrance_greet.RecognizeTwoLayers,
            "/recognize_two_layer",
            resource_class_kwargs = {
                "id_encodings_map" : self.entrance_greet.get_id_encodings_map(),
                "extra_id_encodings_map" : self.entrance_greet.get_extra_id_encodings_map()
            }
        )