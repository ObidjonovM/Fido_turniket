from app.entrance_state import EntranceState
from flask import Flask
from app import settings
from app.face_recognition import FaceRecognition
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://fido_entrance_greet:Fido402@localhost:5432/fido_entrance_greet"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app, db)


fr_in = FaceRecognition('http://' + settings.fr_server, settings.port_in_1)
fr_out = FaceRecognition('http://' + settings.fr_server, settings.port_out_1)

entState = EntranceState()

cam_in_address = settings.cam_in_host
cam_out_address = settings.cam_out_host

# *** Logging setup ***
# create logs folder to save log files
if not os.path.exists('logs'):
    os.mkdir('logs')

# creating logger and setting its configurations
action_logger = logging.getLogger('actions')
action_logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(
    os.path.join('logs', 'actions.log')
)
f_handler.setLevel(logging.INFO)
c_handler.setLevel(logging.INFO)
f_format = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - message: %(message)s', 
    datefmt='%m/%d/%Y %H:%M:%S'
)
f_handler.setFormatter(f_format)
c_handler.setFormatter(f_format)
action_logger.addHandler(f_handler)
action_logger.addHandler(c_handler)


# import and register blueprint
from app.view import views_blueprint

app.register_blueprint(views_blueprint)