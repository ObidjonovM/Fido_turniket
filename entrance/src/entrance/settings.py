import os


#delay between measurements
measurement_delay = 1             # second(s)

# maximum number of records in entrance table
max_num_records = 100

# browserND app settings
browserND_host = "https://10.50.50.212:5080"

# turnstile settings
turnstile_host = "http://10.50.70.187:80"
max_dist = 70

# camera settings
camera_in = "http://10.50.71.220"
camera_out = "http://10.50.71.221"
user = "admin"
password = "FidoBiznes402"
crop_coordinates = {
    'in' : (600, 100, 1400, 1000),           # left, upper, right, lower
    'out' : (300, 100, 1300, 1000) 
}


# face recognition server 
face_host = "http://10.50.50.212"
face_in = face_host + ":5075"
face_out = face_host + ":5076"
thresh = 0.46


# db settings
db_path = os.path.join("entrance", "db_settings", "database.ini")

