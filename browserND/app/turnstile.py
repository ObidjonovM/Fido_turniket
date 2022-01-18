import requests
import re

class Turnstile:
    def __init__(self, host):
        self.host = host

    def let_customer_in(self):
        resp = requests.get(
            self.host, params={"cmd" : "openindoor"}
        )
        return str(resp.content)


    def let_customer_out(self):
        resp = requests.get(
            self.host, params={"cmd" : "openoutdoor"}
        )
        return str(resp.content)

    
    def get_distances(self):
        resp = requests.get(
            self.host, params = {"cmd" : "distances"}
        )
        return map(int, re.findall('\d+', str(resp.content)))
        
        