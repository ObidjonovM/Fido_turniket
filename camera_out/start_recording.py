import cv2
import time
import logging
import os
from sys import exc_info


rstp_address = "rtsp://admin:FidoBiznes402@10.50.71.221:554/Streaming/Channels/102"


def save_photo(photo):
    with open('camera_out_photo.jpg', 'wb') as cf:
        cf.write(photo)



if __name__ == '__main__':

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
    
    # Starting the recording process
    print('Starting to record "video"')
    camera = cv2.VideoCapture(rstp_address, cv2.CAP_FFMPEG)
    #camera = cv2.VideoCapture(rstp_address)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    while True:
        time.sleep(0.01)
        try:
            if camera.isOpened():
                success, frame = camera.read()
                if not success:
                    action_logger.info("Could not capture frame from: " + rstp_address)
                    camera.release()
                    time.sleep(1)
                    camera = cv2.VideoCapture(rstp_address, cv2.CAP_FFMPEG)
                    #camera = cv2.VideoCapture(rstp_address)
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                else:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    save_photo(frame)
            else:
                action_logger.info("Could not open connection with: " + rstp_address)
                camera.release()
                time.sleep(1)
                #camera = cv2.VideoCapture(rstp_address)
                camera = cv2.VideoCapture(rstp_address, cv2.CAP_FFMPEG)
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        except:
            action_logger.error(f"Error occured {exc_info()[0]} : {exc_info()[1]}")
            time.sleep(1)
