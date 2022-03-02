from os.path import join

SECRET_KEY = b"b5f451ca5ac523cf2244e946eb150e3c"

# database settings parameters
SUPER_USER = "timur.babadjanov"                    # super user to add or delete users
ENTRANCE_USER = "entrance"


# face recognition settings parameters
fr_server = "10.50.50.212"
port_in_1 = "5075"
port_out_1 = "5076"
thresh = 0.49


# turnstile settings
door_host = "http://10.50.70.187:80"


# camera hosts
cam_in_host = "rtsp://admin:FidoBiznes402@10.50.71.220:554/Streaming/Channels/102"
cam_out_host = "rtsp://admin:FidoBiznes402@10.50.71.221:554/Streaming/Channels/102"


# photo locations
cam_in_photo = join("..", "camera_in", "camera_in_photo.jpg")
cam_out_photo = join("..", "camera_out", "camera_out_photo.jpg")


# entrance settings
MAX_MEASUREMENT_GAP = 5.0                      # second(s)
