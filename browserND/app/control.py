from app.models.inoutlogs import InoutLogPhotos
from requests.api import request
from app.settings import SUPER_USER, MAX_MEASUREMENT_GAP, DEF_PASS, cam_in_photo, cam_out_photo
from app.models import (Employee, User, FaceEncodings, Entrance, 
                        InOutLogs, MorePhotos, Role, Department, Job)
from app import entState
from werkzeug.security import generate_password_hash
from sqlalchemy import and_
from app import db, fr_in, fr_out
from app import utils
from sys import exc_info
from datetime import datetime, timedelta, date
from collections import OrderedDict
import time
import cv2
import base64
import requests as req



def add_employee(form):
    add_emp_table = Employee.add2EmployeeTable(form)
    if add_emp_table['status_code'] == 0:
        emp_id = add_emp_table['employee'].id
        photo = utils.extract_base64(form['jpeg_base64'])
        add2FR_service = __add2FR(emp_id, photo)
        if add2FR_service['status_code'] == 0:
            add_fe_table = FaceEncodings.add2FaceEncodingsTable(emp_id, add2FR_service['face_encodings'])
            if add_fe_table['status_code'] == 0:
                return {
                    'status_code' : 0,                # SUCCESS
                    'status' : 'OK'
                }
            else:
                # remove from FR server
                rm_fr = __removeFromFR(emp_id)
                if rm_fr['status_code'] == 0:
                    # remove from employee table
                    rm_et = Employee.removeFromEmployeeTable(add_emp_table['employee'])
                    if rm_et['status_code'] == 0:
                        return add_fe_table               #removed as expected
                    else:
                        return rm_et
                else:
                    return rm_fr
        else:
            # remove from employee table
            rm_et = Employee.removeFromEmployeeTable(add_emp_table['employee'])
            if rm_et['status_code'] == 0:
                return add2FR_service                        # removed as expected
            else:
                return rm_et

    return add_emp_table


def __add2FR(emp_id, photo):

    add_fr_in = fr_in.add_client(emp_id, photo)
    if add_fr_in['status_code'] != 4:
        return {
            'status_code' : add_fr_in['status_code'],
            'status' : 'FR IN : ' + add_fr_in['status']
        }

    add_fr_out = fr_out.add_client(emp_id, photo)
    if add_fr_out['status_code'] != 4:
        del_fr_in = fr_in.remove_client(emp_id)
        if del_fr_in['status_code'] != 7:
            return {
                'status_code' : add_fr_out['status_code'],
                'status' : 'FR OUT : ' + add_fr_out['status'] + ' FR IN record was not removed.'
            }    
        return {
            'status_code' : add_fr_out['status_code'],
            'status' : 'FR OUT : ' + add_fr_out['status']
        }
    
    return {
        'status_code' : 0,
        'status' : 'OK',
        'face_encodings' : add_fr_in['face_encodings']
    }


def __removeFromFR(emp_id):
    fr1 = fr_in.remove_client(emp_id)
    if fr1['status_code'] != 7:
        return {
            'status_code' : -3,
            'status' : f'FR IN : Could not remove client {emp_id} from FR server' 
        }
    
    fr2 = fr_out.remove_client(emp_id)
    if fr2['status_code'] != 7:
        return {
            'status_code' : -4,
            'status' : f'FR OUT : Could not remove client {emp_id} from FR server'
        }

    return {
        'status_code' : 0,
        'status' : 'OK'
    }


def all_employees(session):
    if session['role_id'] < 3:
        return Employee.AllEmployees()
    else:
        if 'emp_id' in session:
            if session['job_id'] == 2:
                return Employee.AllEmployees()
            elif session['job_id'] in [10, 11]:
                return Employee.EmployeesByDeptId(session['dept_id'])
            else:
                return []


def all_users():
    return User.AllUsers()


def all_employees_not_user():
    return User.AllEmployeesNotUser()


def get_all_emp_id_name():
    return Employee.getAllClientNames()


def get_department(dept_id):
    return Department.get_department(dept_id)


def all_departments():
    return Department.AllDepartments()


def get_job(job_id):
    return Job.get_job(job_id)


def all_jobs():
    return Job.AllJobs()


def get_emp_info(emp_id):
    emp_info = {}
    emp = Employee.query.filter_by(id=emp_id).first()
    emp_info['id'] = emp_id
    emp_info['fullname'] = utils.parse_fullname(emp.name)
    emp_info['birthDate'] = datetime.strftime(emp.birth_date, '%Y-%m-%d')
    emp_info['dept_id'] = emp.department_id
    emp_info['job_id'] = emp.job_id
    emp_info['photo'] = emp.photo
    emp_info['weekly_logs'] = get_employee_weekly_logs(emp_id)

    return emp_info


def retrieve_more_emp_photos(emp_id):
    def record_to_dict(records):
        result = {
            'status_code' : records['status_code'],
            'status' : records['status'],
            'table_records' : []
        }

        for rec in records['photos']:
            result['table_records'].append(
                {'id' : rec.id, 'photo' : rec.photo, 'data_added' : rec.date_added}
            )

        return result

    records = record_to_dict(
        MorePhotos.select_emp_photos(emp_id)
    )

    records['main_photo'] = Employee.getClientPhoto(emp_id).photo

    records['full_name'] = Employee.getClientFullName(emp_id).name

    for rec in records['table_records']:
        rec['photo'] = rec['photo'].decode('utf-8')

    return records


def add_emp_photo(emp_id, photo):
    encodings = fr_out.get_encodings(
        emp_id, 
        utils.extract_base64(photo)
    )

    if encodings['status_code'] == 0:
        try:
            query_res = MorePhotos.add_record(
                emp_id, 
                bytes(photo, 'utf-8'), 
                encodings['face_encodings']
            )

        except:
            return {
                'status_code' : -20,
                'status': 'failed to add photo'
            }

        return {
            'status_code' : query_res['status_code'],
            'status' : query_res['status'],
            'id' : query_res['employee'].id,
        }
    
    return encodings



def delete_emp_photo(rec_id):
    query_res = MorePhotos.delete_record(rec_id)
    return {
        'status_code' : query_res['status_code'],
        'status' : query_res['status']
    }


def update_employee(form):
    #update employee table
    upd_emp_info = Employee.updateEmployeeInfo(form)

    if upd_emp_info['status_code'] == 0:
        #update fr server
        cust_id = form['custId']
        photo = utils.extract_base64(form['jpeg_base64'])
        upd_fr = __updateFR(
            cust_id, photo, upd_emp_info['old_photo'])

        if upd_fr['status_code'] == 0:
            #update fe table
            upd_fe = FaceEncodings.updateFaceEncoding(
                cust_id, upd_fr['face_encodings'])

            if upd_fe['status_code'] == 0:             # SUCCESS
                return {
                    'status_code' : 0,
                    'status' : 'OK'}

            rev_upd_fr = __updateFR(
                # reverse changes in FR server
                cust_id, upd_emp_info['old_photo'], photo)             

            # reverse changes in Employee table
            rev_upd_emp_info = Employee.updateEmployeeInfo(
                upd_emp_info['old_record'])               

            return upd_fe   

        # reverse changes in Employee table
        rev_upd_emp_info = Employee.updateEmployeeInfo(
            upd_emp_info['old_record'])                 

        return upd_fr
    
    return upd_emp_info


def __updateFR(emp_id, photo, old_photo):
    upd_res1 = fr_in.update_customer_photo(emp_id, photo)        
    if upd_res1['status_code'] != 0:
        upd_res1['status'] = 'FR IN ' + upd_res1['status']
        return upd_res1

    upd_res2 = fr_out.update_customer_photo(emp_id, photo)       
    if upd_res2['status_code'] != 0:                            
        upd_res1 = fr_in.update_customer_photo(emp_id, old_photo)       
        upd_res2['status'] = 'FR OUT ' + upd_res2['status']  
        return upd_res2

    return {
        'status_code' : 0,
        'status' : 'OK',
        'face_encodings' : upd_res2['face_encodings']}


def delete_employee(form):
    emp_id = form['custId']
    del_fe = FaceEncodings.deactivateFaceEncodings(emp_id)

    print("************* del_fe ******************")
    print(del_fe)

    if del_fe['status_code'] == 0:
        del_emp = Employee.deactivateEmployee(form)

        print("*********** del_emp ***********")
        print(del_emp)
        
        if del_emp['status_code'] == 0:
            photo = utils.extract_base64(del_emp['removed_emp'].photo)

            print("********** emp_id **********")
            print(type(emp_id))
            print(len(emp_id))
            print(emp_id)

            del_fr = __deleteFR(emp_id, photo)

            print("************ del_fr ********************")
            print(del_fr)

            if del_fr['status_code'] == 0:
                return {
                    'status_code' : 0,
                    'status' : 'OK'
                }
            else:
                # add record back to Employee table
                db.session.add(del_emp['removed_emp'])
                db.session.commit()

                # add record back to FE table
                db.session.add(FaceEncodings(emp_id, del_fe['removed_encodings']))
                db.session.commit()

                return del_fr
        else:
            # add record back to FE table
            db.session.add(FaceEncodings(emp_id, del_fe['removed_encodings']))
            db.session.commit()

            return del_emp
    
    return del_fe


def __deleteFR(emp_id, photo):
    try:
        print("deleteFR - 1")
        fr1 = fr_in.remove_client(emp_id)
        print("******* fr1 ********")
        print(fr1)
        if fr1['status_code'] != 7:
            return fr1

        print("deleteFR - 2")

        fr2 = fr_out.remove_client(emp_id)
        if fr2['status_code'] != 7:
            fr3 = fr_in.add_client(emp_id, photo)
            if fr3['status_code'] != 4:
                fr2['status'] += f'\n But record {emp_id} was removed from FR IN'
            
            return fr2
    
    except:
        status = f'record {emp_id} could not be removed from FR server.'
        status += f' Error: {exc_info()[0]} : {exc_info()[1]}'
        return {
            'status_code' : -11,
            'status' : status
        }
    
    return {
        'status_code' : 0,
        'status' : 'OK'
    }


def add_user(form, session):
    if int(form['role_id']) == 1:
        return {
            'status_code' : -4,
            'status' : f'Cannot add superuser'
        }
    if int(session['role_id']) <= 2:
        try:
            db.session.add(User(form['login'], DEF_PASS, form['role_id'], \
            form['emp_id'], form['dept_id'], form['job_id']))
            db.session.commit()
            return {
                'status_code' : 0,
                'status' : 'OK'
            }
        except:
            return {
                'status_code' : -5,
                'status' : f'Could not add new user - {exc_info()[0]} : {exc_info()[1]} '
            }
    else:
        return {
            'status_code' : -3,
            'status' : f'You cannot add a user'
        }


def change_password(form, session):
    same_login = True
    old_pass_match = True
    new_pass_same = True
    user = None
    if session['login'] != form['login']:
        same_login = False
        return {
            'status_code' : -7,
            'status' : 'User can only change his/her password'
        }
    elif form['new_password'] != form['confirm_new_password']:
        new_pass_same = False
        return {
            'status_code' : -8,
            'status' : 'New password field is not same as entered password'
        }
    else:
        user = User.query.filter_by(login=session['login']).first()
        if not user.check_password(form['old_password']):
            old_pass_match = False
            return {
                'status_code' : -9,
                'status' : 'Old password did not match'
            }

    if all([same_login, old_pass_match, new_pass_same]):
        user.password_hash = generate_password_hash(form['new_password'])
        db.session.add(user)
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }


def change_user(form, session):
    user = None
    if int(session['role_id']) <= 2:
        try:
            user = User.query.filter_by(id=form['user_id']).first()
            if int(user.role_id) > int(session['role_id']) and int(form['role_id']) >= int(session['role_id']):
                user.role_id = form['role_id']
                db.session.add(user)
                db.session.commit()
                return {
                    'status_code' : 0,
                    'status' : 'OK'
                }

            return {
                'status_code' : -10,
                'status' : "You can't update"
            }

        except:
            return {
                'status_code' : -11,
                'status' : 'Could not update the user from database'
            }

    else:
        return {
            'status_code' : -12,
            'status' : "You are not allowed to update"
        }


def get_users():
    return User.query.with_entities(User.login).all()


def get_user(id):
    return User.query.filter_by(id = id).first()


def remove_user(user_id, session):
    if int(session['role_id']) <= 2:
        try:
            user = User.query.filter_by(id=user_id).first()
            if int(user.role_id) > int(session['role_id']):
                db.session.delete(user)
                db.session.commit()
                return {
                    'status_code' : 0,
                    'status' : 'OK'
                }

            return {
                'status_code' : -10,
                'status' : "You can't delete"
            }

        except:
            return {
                'status_code' : -11,
                'status' : 'Could not delete the user from database'
            }
    else:
        return {
            'status_code' : -12,
            'status' : "You are not allowed to delete"
        }


def login(form, session):
    user_exists = True
    wrong_password = False
    user = User.query.filter_by(login=form['login']).first()

    if user is None:
        return False, wrong_password
    else:
        if user.check_password(form['password']):
            session['login'] = user.login
            session['role_id'] = user.role_id
            if user.emp_id != None:
                session['emp_id'] = user.emp_id
                session['dept_id'] = user.department_id
                session['job_id'] = user.job_id
            
            return user_exists, wrong_password
        
        return user_exists, True


def add_department(form):
    try:
        db.session.add(Department(form['name']))
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }
    except:
        return {
            'status_code' : -5,
            'status' : f'Could not add new department - {exc_info()[0]} : {exc_info()[1]} '
        }


def change_department(form):
    department = None
    try:
        department = Department.query.filter_by(id=form['dept_id']).first()
        department.name = form['name']
        db.session.add(department)
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }

    except:
        return {
            'status_code' : -11,
            'status' : 'Could not update the department from database'
        }


def add_job(form):
    try:
        db.session.add(Job(form['name']))
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }
    except:
        return {
            'status_code' : -5,
            'status' : f'Could not add new job - {exc_info()[0]} : {exc_info()[1]} '
        }


def change_job(form):
    job = None
    try:
        job = Job.query.filter_by(id=form['job_id']).first()
        job.name = form['name']
        db.session.add(job)
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }

    except:
        return {
            'status_code' : -11,
            'status' : 'Could not update the job from database'
        }


def add_role(form):
    try:
        db.session.add(Role(form['name']))
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }
    except:
        return {
            'status_code' : -5,
            'status' : f'Could not add new role - {exc_info()[0]} : {exc_info()[1]} '
        }


def get_roles_by_equals_small(role_id):
    return Role.query.with_entities(Role.id, Role.name). \
        filter(Role.id >= role_id, Role.id != 1, Role.id != 4).all()


def get_roles_by_small(role_id):
    return Role.query.with_entities(Role.id, Role.name).filter(Role.id > role_id).all()


def remove_role(form):
    try:
        if form['name'] == SUPER_USER:
            db.session.delete(
                Role.query.filter_by(id=form['role_id']).first())
            db.session.commit()
            return {
                'status_code' : 0,
                'status' : 'OK'
            }
        
        return {
            'status_code' : -10,
            'status' : "Super user can't be remove"
        }

    except:
        return {
            'status_code' : -11,
            'status' : 'Could not delete the user from database'
        }


def get_all_encodings():
    return FaceEncodings.get_all_encodings()


def get_all_extra_encodings():
    def str2vec(vec_str):
        vec_list = []
        lines = vec_str.strip()[1:-1].splitlines()
        for line in lines:
            vec_list.extend(map(float, line.split()))
        return vec_list
        
    empID_encodings_map = {}
    records = MorePhotos.select_all_empID_encodings()
    
    if records['status_code'] == 0:
        for rec in records['records']:
            vector = str2vec(rec.photo_encodings)
            if rec.emp_id in empID_encodings_map:
                empID_encodings_map[rec.emp_id].append(vector)
            else:
                empID_encodings_map[rec.emp_id] = [vector]

    return empID_encodings_map


def setNameIdMap():
    status_code = 0
    status = 'OK'
    try:
        entState.setClientNameIdMap(
            Employee.getAllClientNames()
        )

    except:
        status_code = -14
        status = 'Failed to get client name to ID map'

    return {
        'status_code' : status_code,
        'status' : status
    }


def birthday_list():
    birthdays = {}
    today = datetime.today()

    records = Employee.query.with_entities(
        Employee.id,
        Employee.name,
        Employee.birth_date).all()

    for r in records:
        if (today.day == r[2].day) and (today.month == r[2].month):
            birthdays[r[0]] = r[1]

    return birthdays


def manage_birthday_state(method, client_id = None):
    method = method.lower()
    birthday = False

    if method == 'get':
        setup_birthday_state()

    elif method == 'post':
        celeb_info = get_celeb_info(client_id)
        if celeb_info['birthday'] and not celeb_info['celebrated']:
            birthday = True

    return birthday

def setup_birthday_state():

    if not entState.is_celebrated_path_current():
        entState.reset_birthday_fields()

    if (not entState.is_birthday_list_current()) or (not entState.is_celebrated_list_current()):    
        entState.setup_celebrated_list()
        entState.setup_birthday_list(
            birthday_list()
        )


def update_birthday_state():
    if not entState.is_celebrated_list_current():
        entState.setup_celebrated_list() 
    
    if not entState.is_birthday_list_current():
        entState.setup_birthday_list(
            birthday_list()
        )


def get_celeb_info(client_id):
    if not entState.is_celebrated_path_current():
        entState.reset_birthday_fields()

    update_birthday_state()
    return entState.is_celebrated(client_id)


def entrance_state():
    time_gap = time.time() - entState.getRequestedTime()

    if time_gap > MAX_MEASUREMENT_GAP or entState.getMeasurementId() is None:
        requestId = None
    else:
        requestId = entState.getMeasurementId() + 1

    status_code = 0
    status = 'OK'
    try:
        ent_rec = Entrance.whoIsAtEntrance(requestId)
        rec_id = ent_rec.id
        client_id = ent_rec.client_id
        entState.setMeasurementId(ent_rec.id)
        action = ent_rec.action

    except:
        entState.setMeasurementId(None)
        status_code = -13
        status = f'Could not extract record - {exc_info()[0]} : {exc_info()[1]} '
        client_id = -2
        rec_id = -1
        action = 'unknown'

    entState.setRequestedTime(time.time())
    return {
        'status_code' : status_code,
        'status' : status,
        'client_id' : client_id,
        'rec_id' : rec_id,
        'action' : action
    }


def gen_frames(address, camera_side):
    camera = cv2.VideoCapture(address)
    while True:
        if camera.isOpened():
            success, frame = camera.read()
            if not success:
                print("could not capture frame from: " + address)
                camera.release()
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                save_photo(frame, camera_side)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            print("could not open connection with: " + address)
            break


def save_photo(photo, camera_side):
    camera_side = camera_side.lower()
    if camera_side == 'in':
        entState.setPhotoIn(photo)

    if camera_side == 'out':
        entState.setPhotoOut(photo)


def stream_photos(camera_side):
    camera_side = camera_side.lower()
    photo = b''
    if camera_side == 'in':
        while True:
            time.sleep(0.15)
            with open(cam_in_photo, 'rb') as f:
                photo = f.read()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + photo + b'\r\n')
    
    if camera_side == 'out':
        while True:
            time.sleep(0.15)
            with open(cam_out_photo, 'rb') as f:
                photo = f.read()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + photo + b'\r\n')
        



def get_photo(camera_side):
    camera_side = camera_side.lower()
    photo = b''
    if camera_side == 'in':
        with open(cam_in_photo, 'rb') as f:
            photo = f.read()

    if camera_side == 'out':
        with open(cam_out_photo, 'rb') as f:
            photo = f.read()
    
    return photo
    

def str_to_datetime(str_date, maximize=False):
    year, month, day = map(int, str_date.split("-"))
    if maximize:
        return datetime(year, month, day, 3, 59, 59, 999999) + timedelta(days=1)

    return datetime(year, month, day, 4, 0, 0, 0)


def split_logs_into_days(inout_logs):
    split_io_logs = []         # list of daily inout logs
    daily_logs = []
    for io_log in inout_logs:
        if daily_logs == []:
            daily_logs.append(io_log)
        else:
            currDT = io_log[0]                    # current datetime
            prevDT = daily_logs[-1][0]            # previous datetime
            if prevDT.day == currDT.day:
                if currDT.hour >= 4:            # start counting from 4 AM
                    if prevDT.hour < 4:
                        split_io_logs.append(daily_logs)
                        daily_logs = [io_log]
                    else:
                        daily_logs.append(io_log)
            else:
                if currDT.hour < 4:             # stops counting at 3:59:59 AM
                    daily_logs.append(io_log)
                else:
                    split_io_logs.append(daily_logs)
                    daily_logs = [io_log]

    split_io_logs.append(daily_logs)
    return split_io_logs


def inout_to_filo_logs(inout_logs):
    # first in and last out (filo) logs 
    filo_logs = OrderedDict()     

    # Extracting the first entrance and the last exit 
    for log in inout_logs:
        emp_id = log.emp_id
    
        if emp_id not in filo_logs:
            filo_logs[emp_id] = {
                'in' : None, 'out' : None, 'total_time' : 0, 
                'last_action' : log.action, 'last_reg_time' : log.reg_time
            }
            filo_logs[emp_id][log.action] = log
    
        else:
            if not filo_logs[emp_id]['in'] and log.action == 'in':
                filo_logs[emp_id]['in'] = log
            elif log.action == 'out':
                filo_logs[emp_id]['out'] = log

            if filo_logs[emp_id]['last_action'] == 'in' and log.action == 'out':
                filo_logs[emp_id]['total_time'] += (log.reg_time - filo_logs[emp_id]['last_reg_time']).seconds

            filo_logs[emp_id]['last_action'] = log.action
            filo_logs[emp_id]['last_reg_time'] = log.reg_time

    return filo_logs


def combine_to_filo_logs(split_io_logs):
    '''
    Combine daily filos into one list of filos
    '''
    all_filo_logs = inout_to_filo_logs(split_io_logs[0])  # initialize
    
    for io_log in split_io_logs[1:]:
        # get filos for that day
        filos = inout_to_filo_logs(io_log)

        # combine each filo into all_filo_logs
        for emp_id, record in filos.items():
            if emp_id in all_filo_logs:
                all_filo_logs[emp_id]['total_time'] += record['total_time']
                all_filo_logs[emp_id]['last_action'] = record['last_action']
                all_filo_logs[emp_id]['last_reg_time'] = record['last_reg_time']
                all_filo_logs[emp_id]['out'] = record['out']
            else:
                all_filo_logs[emp_id] = record

    return all_filo_logs


def from_seconds_to_hour_minutes(seconds):
    hours = seconds // 3600
    minutes = seconds % 3600 // 60
    return f"{hours} часов {minutes} минут"


def toRenderingFormat(filo_logs):
    # Convert to convenient format for rendering
    filo_logs_list = []
    for _, v in filo_logs.items():
        log = {}
        if v['in']:
            log['name'] = v['in'].name
            log['time_in'] = v['in'].reg_time
            log['log_id_in'] = v['in'].log_id

        else:
            log['time_in'] = '-'
            log['log_id_in'] = '-'

        if v['out']:
            log['time_out'] = v['out'].reg_time
            log['log_id_out'] = v['out'].log_id

            if log['time_in'] == '-':              # In log not available
                log['name'] = v['out'].name
        else:
            log['time_out'] = '-'
            log['log_id_out'] = '-'

        log['total_time'] = v['total_time']
        log['formatted_time'] = from_seconds_to_hour_minutes(v['total_time'])

        filo_logs_list.append(log)

    return filo_logs_list    


def get_first_ins_last_outs(inout_logs):
    # Split inout_logs into multiple days
    split_io_logs = split_logs_into_days(inout_logs)   # split_io_logs - list of split inout_logs

    # Add up total time spent in office for each employee for the given period
    filo_logs = combine_to_filo_logs(split_io_logs)

    # Convert to convenient format for rendering
    return toRenderingFormat(filo_logs)


def get_expected_work_time(start_date, end_date):
    work_seconds = 8 * 60 * 60
    _day = timedelta(days=1)
    bdays = 1                       # business days
    start_date = str_to_datetime(start_date)
    end_date = str_to_datetime(end_date)
    
    if start_date == end_date:
        return work_seconds

    while start_date < end_date:
        if start_date.weekday() < 5:        # not weekend
            bdays += 1
        start_date += _day

    return bdays * work_seconds


def evaluate_attendence(filo_logs, start_date, end_date):
    expected_work_time = get_expected_work_time(start_date, end_date)

    for filo in filo_logs:
        if expected_work_time == 0:
            filo['normative'] = 100
        else:
            filo['normative'] = round((filo['total_time'] / expected_work_time) * 100, 2)

    return filo_logs


def logs(request_info):
    start_date = str_to_datetime(request_info['start_date'])
    end_date = str_to_datetime(request_info['end_date'], True)
    log_settings = request_info['log_settings']

    query = db.session.query(InOutLogs, Employee)
    if log_settings == '0' or log_settings == '1':
        query = query.join(Employee, InOutLogs.emp_id == Employee.id)

    else:
        query =  query.outerjoin(Employee, InOutLogs.emp_id == Employee.id)

    inout_logs = query.filter(and_(
                    (InOutLogs.reg_time >= start_date),
                    (InOutLogs.reg_time <= end_date))
                ).with_entities(
                    InOutLogs.reg_time, Employee.name, InOutLogs.emp_id, InOutLogs.descr, 
                    InOutLogs.action, InOutLogs.log_id, InOutLogs.label_as, InOutLogs.dist_in, 
                    InOutLogs.dist_out, InOutLogs.face_dist, InOutLogs.face_coors 
                ).order_by(InOutLogs.log_id).all()

    if log_settings == '0':
        inout_logs = get_first_ins_last_outs(inout_logs)         # output is actually filo logs
        inout_logs = evaluate_attendence(
            inout_logs, request_info['start_date'], request_info['end_date']
        )        # adding attendence (in %) column

    return {
        'log_settings' : log_settings, 
        'inout_logs' : inout_logs,
    }


def in_office_employees():
    today = datetime.today().strftime('%Y-%m-%d')
    today_logs = logs({
            'start_date' : today,
            'end_date' : today,
            'log_settings' : '1'
    })

    in_office = {}
    for log in today_logs['inout_logs']:
        in_office[log.emp_id] = log.action

    return in_office


def employee_logs(emp_id, start_date, end_date):
    def get_employee_filos(daily_logs):
        filo_logs = []
        for logs in daily_logs:
            filo_logs.append(inout_to_filo_logs(logs))

        return filo_logs

    def render_daily_logs(filo_logs):
        NORMATIVE = 8 * 60 * 60
        logs = []
        for filo in filo_logs:
            log = {}
            if filo != {}:
                _, record = filo.popitem()
                if record['in']:
                    log['time_in'] = record['in']
                else:
                    log['time_in'] = '-'
                
                if record['out']:
                    log['time_out'] = record['out']
                else:
                    log['time_out'] = '-'

                log['total_time'] = record['total_time']
                log['formatted_time'] = from_seconds_to_hour_minutes(record['total_time'])
                log['normative'] = round(100 * record['total_time'] / NORMATIVE, 2)
            logs.append(log)

        return logs

    # gets employee's filo logs for the given date interval
    start_date_dt = str_to_datetime(start_date)
    end_date_dt = str_to_datetime(end_date, True)

    daily_logs = split_logs_into_days(
            InOutLogs.get_employee_logs(emp_id, start_date_dt, end_date_dt)
        )

    filo_logs = get_employee_filos(daily_logs)

    return render_daily_logs(filo_logs)


def get_employee_inouts(emp_id, start_date, end_date):
    return {
        'inouts' : InOutLogs.get_employee_logs(
                        emp_id, 
                        str_to_datetime(start_date), 
                        str_to_datetime(end_date, True)
                    )
    }


def get_employee_weekly_logs(emp_id):
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    return employee_logs(
            emp_id, 
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )


def get_employees_daily_logs_in(start_date):
    start_date = start_date
    end_date = start_date + timedelta(days=1)
    result =  InOutLogs.get_employees_logs_in(
            start_date,
            end_date
        )

    time_in = {}
    for log in result:
        if hasattr(log[1], 'time'):
            time_in[log[0]] = str(log[1].time()).split(".")[0]

    return time_in


def get_employees_daily_logs_out(start_date):
    start_date = start_date
    end_date = start_date + timedelta(days=1)
    result =  InOutLogs.get_employees_logs_out(
            start_date,
            end_date
        )

    time_out = {}
    for log in result:
        if hasattr(log[1], 'time'):
            time_out[log[0]] = str(log[1].time()).split(".")[0]

    return time_out


def log_info(log_id):
    log = InOutLogs.query.filter_by(log_id=log_id).first()  
    photo = 'data:image/jpeg;base64,' + utils.extract_base64(
        utils.bytesTobase64(log.reg_photo).decode('utf-8')
    )
    return log, photo


def client_name(client_id):
    return Employee.query.with_entities(Employee.name).filter_by(id=client_id).first()


def reg_photo_log_photo(log_id, emp_id):
    try:
        log_info = InoutLogPhotos.get_log_photo(log_id)
        if emp_id != '-1':
            reg_photo = Employee.getClientPhoto(emp_id).photo
        else:
            reg_photo = ''

        log_photo = 'data:image/jpeg;base64,' + utils.extract_base64(
            utils.bytesTobase64(log_info.log_photo).decode('utf-8')
        )

    except:
        return {
            'status_code' : -13,
            'status' : f'Could not extract record - {exc_info()[0]} : {exc_info()[1]} '
        }

    return {
        'status_code' : 0,
        'status' : 'OK',
        'emp_id' : emp_id,
        'log_photo' : log_photo,
        'reg_photo' : reg_photo
    }
        

def emp_log_photos(emp_id, num_photos, start_log_id=None):
    log_id_photo_list = []
    for rec in InOutLogs.get_photos(emp_id, num_photos, start_log_id):
        log_id_photo_list.append(
            {
                'log_id' : rec.log_id, 
                'photo' : 'data:image/jpeg;base64,' + 
                          base64.b64encode(rec.log_photo).decode('utf-8')
            }
        )

    return {'records' : log_id_photo_list}


def update_log_info(log_id, emp_id):
    # first get employee info
    record = Employee.getPhotoAndName(emp_id)

    # update current log
    result = InOutLogs.update_emp_id(log_id, emp_id)
    result['fullname'] = ''
    result['photo'] = b''

    if result['status_code'] == 0:
        result['fullname'] = record[0]
        result['photo'] = record[1]

    return result


def get_current_weather():
    weather = req.get("http://api.openweathermap.org/data/2.5/weather?q=Tashkent,Uzbekistan&APPID=87ea10a19e895caef5319978b09d9bb6&lang=ru&units=metric")
    return weather.json()


def get_three_day_weather():
    forecast = req.get("http://api.weatherapi.com/v1/forecast.json?key=eb2d3032f2a14fe089655010212408&q=Tashkent&days=3&aqi=no&alerts=no&lang=ru")
    return forecast.json()


def update_label_as(log_id, label_as):
    return InOutLogs.update_label_as(log_id, label_as)
