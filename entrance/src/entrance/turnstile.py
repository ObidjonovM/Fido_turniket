import requests
import re
import time

class Turnstile:
    def __init__(self, host):
        self.host = host
        self.__dist_in = 1_000_000
        self.__dist_out = 1_000_000


    def let_customer_in(self):
        resp = requests.get(
            self.host, params={"cmd" : "openindoor"}, timeout=2
        )
        return str(resp.content)


    def let_customer_out(self):
        resp = requests.get(
            self.host, params={"cmd" : "openoutdoor"}, timeout=2
        )
        return str(resp.content)

    
    def get_distances(self):
        try:
            resp = requests.get(
                self.host, params = {"cmd" : "distances"}, timeout=2
            )
            if (resp.status_code == 200):
                self.__dist_in,  self.__dist_out = map(int, re.findall('\d+', str(resp.content)))
            else:
                self.reset_distances()
                
        except:
            print("Turnstile did not respond in expected time")


    def reset_distances(self):
        self.__dist_in = 1_000_000
        self.__dist_out = 1_000_000



    @property
    def distance_in(self):
        return self.__dist_in

    @property
    def distance_out(self):
        return self.__dist_out
    

