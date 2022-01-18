import time
import os
from sys import exc_info
import logging

from entrance import Entrance, entrance_db, inout_logs, settings


os.environ['NO_PROXY'] = '10.50.71.240'

if __name__ == "__main__":

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


    print("Starting the entrance service...")
    entrance_db.delete_all()
    ent = Entrance()
    
    counter = 0
        
    print("Entrance service has started")
    while True:
        time.sleep(settings.measurement_delay)
        try:
            ent.catch_values()
            print(f"Din = {ent.turnstile.distance_in}")
            print(f"Dout = {ent.turnstile.distance_out}")
            log_params = ent.take_action()
            ent.reset_values()
            if log_params != {}:
                if log_params['descr'] != 'no face':
                    ent_id = entrance_db.insert(ent, log_params['emp_id'], log_params['action'])
                    counter += 1
                    log_id = inout_logs.insert_logs(log_params)
                    inout_logs.insert_log_photo(log_id, log_params['reg_photo'])
                    action_logger.info(f"ent_id = {ent_id}, log_id = {log_id}")
                    
                    if counter >= settings.max_num_records:
                        entrance_db.delete_first_record()
        except:
            action_logger.error("Failure in operation")
            action_logger.error(f"Error: {exc_info()[0]} -  {exc_info()[1]}")
            time.sleep(1)
