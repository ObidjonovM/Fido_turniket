import os
from server_side.fido_entrance import FidoEntrance


os.environ['NO_PROXY'] = '10.50.50.212'

ENCS_ID_URL = "https://10.50.50.212:5080/get_all_encodings"

# EXTRA_ENCS_ID_URL = "https://10.50.50.212:5080/get_all_extra_encodings"
EXTRA_ENCS_ID_URL = "https://10.50.50.212:5080/get_all_extra_encodings"


entrance = FidoEntrance(__name__, ENCS_ID_URL, EXTRA_ENCS_ID_URL)

# entrance.app.run(host="10.50.50.212", port=5075, debug=True)          # server IN

#entrance.app.run(host="10.50.50.212", port=5076, debug=True)         # server OUT



def start_app():
    return entrance.app    
