import requests


class FaceRecognition:

    def __init__(self, host, port):
        self.host = host
        self.port = port


    def __make_url(self, end_point):
        return self.host + ":" + self.port + end_point


    def __post_client_id_photo(self, end_point, client_id, photo):
        post_data = {
            "client_id" : client_id,
            "img_bytes" : photo
        }
        return requests.post(
            self.__make_url(end_point),
            post_data
        ).json()


    def add_client(self, client_id, photo):
        return self.__post_client_id_photo(
            "/add_client",
            client_id,
            photo
        )


    def get_distance(self, client_id, photo):
        return self.__post_client_id_photo(
            "/get_distance",
            client_id,
            photo
        )


    def remove_client(self, client_id):
        data = {
            "client_id" : client_id,
        }
        return requests.delete(
            self.__make_url("/remove_client"),
            data=data
        ).json()


    def recognize(self, photo, threshold, action):
        post_data = {
            "img_bytes" : photo,
            "threshold" : threshold,
            "action" : action
        }
        return requests.post(
            self.__make_url("/recognize"),
            post_data
        ).json()


    def save_changes(self):
        return requests.post(
            self.__make_url("/save_changes"),
        ).json()


    def get_client_ids(self):
        return requests.get(
            self.__make_url("/get_clients"),
        ).json()


    def update_customer_photo(self, client_id, photo):
        return self.__post_client_id_photo(
            "/update_client_photo",
            client_id,
            photo
        )


    def get_encodings(self, client_id, photo):
        return self.__post_client_id_photo(
            "/photo_encodings",
            client_id,
            photo
        )