from flask import (Blueprint, render_template, 
                   redirect, url_for, session, request, Response)
from sqlalchemy.sql.expression import select
from app import control, entState, action_logger, settings
from sys import exc_info
import json



views_blueprint = Blueprint('view', __name__)


@views_blueprint.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', main_user=session['main_user'])

    return redirect(url_for('view.login'))


@views_blueprint.route('/addemployee', methods=['GET', 'POST'])
def add_employee():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('add_employee.html')

        if request.method == 'POST':
            try:
                add_res = control.add_employee(request.form)
                if add_res['status_code'] == 0:
                    action_logger.info(
                        f"Added - {request.form['lname']} {request.form['fname']} {request.form['mname']}"
                    )
                else:
                    action_logger.info(
                        f"Not added - {add_res['status']} - {request.form['lname']} {request.form['fname']} {request.form['mname']}"
                    )
            except:
                action_logger.error(f"Error in adding: {request.form['lname']} {request.form['fname']} {request.form['mname']}")
                action_logger.error(f"view.py - add_employee - {exc_info()[0]} : {exc_info()[1]}")

            return redirect(url_for('view.all_employees'))

    return redirect(url_for('view.login'))


@views_blueprint.route('/all_employees')
def all_employees():
    if 'username' in session:
        return render_template(
            'all_employees.html',
            employees=control.all_employees(),
            in_office=control.in_office_employees()
        )

    return redirect(url_for('view.login'))


@views_blueprint.route('/employee/<emp_id>', methods=['POST', 'GET'])
def employee(emp_id):
    if 'username' in session:
        if request.method == 'GET':
            emp_info = control.get_emp_info(emp_id)                    # TODO: log the outcome
            return render_template('employee.html', emp_info=emp_info, main_user=session['main_user'])

        if request.method == 'POST':
            settings = request.json['log_settings']
            if settings == '0':
                filos =  control.employee_logs(
                    emp_id,
                    request.json['start_date'],
                    request.json['end_date'])

                return {'filos' : filos}

            if settings == '1':
                inouts = control.get_employee_inouts(
                    emp_id,
                    request.json['start_date'], 
                    request.json['end_date'])

                return {'inouts' : inouts}

    return redirect(url_for('view.login'))


@views_blueprint.route('/more_emp_photos/<emp_id>', methods=['POST', 'GET', 'DELETE'])
def more_emp_photos(emp_id):
    if 'username' in session:

        if request.method == 'GET':
            return render_template(
                'employee_more_photos.html',
                emp_id=emp_id,
                photos=control.retrieve_more_emp_photos(emp_id)
            )

        if request.method == 'POST':
            return control.add_emp_photo(
                emp_id,
                request.json['new_photo']
            )

        if request.method == 'DELETE':
            return control.delete_emp_photo(
                request.json['rec_id']
            )

    return redirect(url_for('view.login'))


@views_blueprint.route('/update_user_info', methods=['POST'])
def update_user_info():
    if 'username' in session:
        try:
            uui_res = control.update_user_info(request.form)
            if uui_res['status_code'] == 0:
                action_logger.info(
                    f"Updated info - {request.form['lname']} {request.form['fname']} {request.form['mname']}"
                )
            else:
                action_logger.info(
                    f"Could not update info - {uui_res['status']} - {request.form['lname']} {request.form['fname']} {request.form['mname']}"
                )
        except:
            action_logger.error(
                f"Error in updating info for: {request.form['lname']} {request.form['fname']} {request.form['mname']}"
            )
            action_logger.error(
                f"view.py - update_user_info - {exc_info()[0]} : {exc_info()[1]}"
            )

        return redirect(url_for("view.all_employees"))
    
    return redirect(url_for('view.login'))


@views_blueprint.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' in session:
        try:
            du = control.delete_user(request.form)
            if du['status_code'] == 0:
                action_logger.info(
                    f"Deleted employee - {request.form['lname']} {request.form['fname']} {request.form['mname']}"
                )
            else:
                action_logger.info(
                    f"Failed to delete employee - {request.form['lname']} {request.form['fname']} {request.form['mname']}"
                )
        except:
            action_logger.error(
                f"Error in deleting: {request.form['lname']} {request.form['fname']} {request.form['mname']}"
            )
            action_logger.error(
                f"view.py - delete_user - {exc_info()[0]} : {exc_info()[1]}"
            )

        return redirect(url_for("view.all_employees"))

    return redirect(url_for('view.login'))


@views_blueprint.route('/logs', methods=['GET', 'POST'])
def logs():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('logs.html', main_user=session['main_user'])

        if request.method == 'POST':
            logs = control.logs(request.form)
            if logs['log_settings'] == '0':
                return render_template('filo_logs.html', logs=logs['inout_logs'])

            return render_template('view_logs.html', logs=logs['inout_logs'], 
                                log_settings=logs['log_settings'], main_user=session['main_user'])

    return redirect(url_for('view.login'))


@views_blueprint.route('/log_info/<log_id>')
def log_info(log_id):
    log, photo = control.log_info(log_id)

    try:
        name = control.client_name(log.emp_id)[0]
    except:
        name = ''
    
    return render_template('log_info.html', log=log, name=name, photo=photo)


@views_blueprint.route('/reg_photo_log_photo/', methods=['POST'])
def reg_photo_log_photo():
    return control.reg_photo_log_photo(
        request.json['log_id'], request.json['emp_id']
    )


@views_blueprint.route('/emp_log_photos', methods=['POST'])
def emp_log_photos():
    params = json.loads((request.data.decode('utf-8')))
    return control.emp_log_photos(
        params['emp_id'], params['num_photos'], params['start_log_id']
    )

@views_blueprint.route('/update_log_info', methods=['POST'])
def update_log_info():
    log_id = int(request.json['log_id'])
    emp_id = int(request.json['correct_id'])
    return control.update_log_info(log_id, emp_id)


@views_blueprint.route('/update_label_as', methods=['POST'])
def update_label_as():
    params = json.loads((request.data.decode('utf-8')))
    return control.update_label_as(params['log_id'], params['label_as'])


@views_blueprint.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('add_user.html')

        if request.method == 'POST':
            au_res = control.add_user(request.form)    # TODO: log the outcome
            return redirect(url_for("view.index"))
    
    return redirect(url_for('view.login'))



@views_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('change_password.html', 
                                    same_username=True, 
                                    old_pass_match=True,
                                    new_pass_same=True)
                                    
        if request.method == 'POST':
            chp_res = control.change_password(request.form, session)        # TODO: log the outcome
            if chp_res['status_code'] == 0:
                return redirect(url_for('view.logout'))
            elif chp_res['status_code'] == -7:
                return render_template('change_password.html', 
                                    same_username=False, 
                                    old_pass_match=True,
                                    new_pass_same=True)
            elif chp_res['status_code'] == -8:
                return render_template('change_password.html', 
                                        same_username=True, 
                                        old_pass_match=True,
                                        new_pass_same=False)
            elif chp_res['status_code'] == -9:
                return render_template('change_password.html', 
                                        same_username=True, 
                                        old_pass_match=False,
                                        new_pass_same=True)    

    return redirect(url_for('view.login'))


@views_blueprint.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('remove_users.html', users=control.get_users())

        if request.method == 'POST':
            ru_res = control.remove_user(request.form, session)       # TODO: log the outcome
            return redirect(url_for('view.index'))

    return redirect(url_for('view.login'))


@views_blueprint.route("/entrance", methods=['GET', 'POST'])
def entrance():
    if 'username' in session:
        if request.method == 'GET':
            control.setNameIdMap()
            if session['username'] == settings.ENTRANCE_USER:
                control.manage_birthday_state('GET')

            return render_template("entrance.html", ent_state=control.entrance_state())
        
        if request.method == 'POST':
            resp = control.entrance_state()
            client_id = resp['client_id']
            if client_id > 0:
                try:
                    resp['clientName'] = entState.getClientNameIdMap()[client_id]
                except:
                    control.setNameIdMap()
                    resp['clientName'] = entState.getClientNameIdMap()[client_id]
            else:
                resp['clientName'] = ''

            if session['username'] == settings.ENTRANCE_USER:
                resp['birthday'] = control.manage_birthday_state('POST', client_id)
                if resp['birthday']:
                    entState.add_to_celebrated_list(client_id)

            return resp

    return redirect(url_for('view.login'))   
    


@views_blueprint.route("/entrance_new", methods=['GET', 'POST'])
def entrance_new():
    if 'username' in session:
        if request.method == 'GET':
            control.setNameIdMap()
            if session['username'] == settings.ENTRANCE_USER:
                control.manage_birthday_state('GET')

            return render_template("entrance_new.html", ent_state=control.entrance_state())
        
        if request.method == 'POST':
            resp = control.entrance_state()
            client_id = resp['client_id']
            if client_id > 0:
                try:
                    resp['clientName'] = entState.getClientNameIdMap()[client_id]
                except:
                    control.setNameIdMap()
                    resp['clientName'] = entState.getClientNameIdMap()[client_id]
            else:
                resp['clientName'] = ''

            if session['username'] == settings.ENTRANCE_USER:
                resp['birthday'] = control.manage_birthday_state('POST', client_id)
                if resp['birthday']:
                    entState.add_to_celebrated_list(client_id)

            return resp

    return redirect(url_for('view.login'))   


@views_blueprint.route('/in_video_feed')
def video_feed_in():
    return Response(control.stream_photos('IN'), mimetype='multipart/x-mixed-replace; boundary=frame')


@views_blueprint.route('/out_video_feed')
def video_feed_out():
    return Response(control.stream_photos('OUT'), mimetype='multipart/x-mixed-replace; boundary=frame')


@views_blueprint.route('/in_current_photo', methods=['POST'])
def in_current_photo():
    return control.get_photo('IN')


@views_blueprint.route('/out_current_photo', methods=['POST'])
def out_current_photo():
    return control.get_photo('OUT')


@views_blueprint.route("/happybirthday", methods=['GET'])
def happybirthday():
    if 'username' in session:
        return render_template("happybirthday.html")

    return redirect(url_for('view.login'))   
    

@views_blueprint.route("/get_all_encodings", methods=['POST'])
def get_all_encodings():
    return control.get_all_encodings()


@views_blueprint.route("/get_all_extra_encodings", methods=['POST'])
def get_all_extra_encodings():
    return control.get_all_extra_encodings()


@views_blueprint.route("/get_current_weather", methods=['POST'])
def get_current_weather():
    return control.get_current_weather()


@views_blueprint.route("/get_three_day_weather", methods=['POST'])
def get_three_day_weather():
    return control.get_three_day_weather()


@views_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' not in session:
        user_exists = True
        wrong_password = False
        if request.method == "POST":
            user_exists, wrong_password = control.login(request.form, session)
            if user_exists and not wrong_password:
                return redirect(url_for('view.index'))

        return render_template("login.html", user_exists=user_exists, wrong_password=wrong_password)
    
    return redirect(url_for('view.index'))


@views_blueprint.route("/logout")
def logout():
    if 'username' in session:
        session.pop("username", None)
        session.pop("main_user", None)
    
    return redirect(url_for("view.login"))


########## template filters ##########

@views_blueprint.app_template_filter('get_date')
def get_date(datetime_object):
    if hasattr(datetime_object, 'date'):
        return str(datetime_object.date())

    return datetime_object


@views_blueprint.app_template_filter('get_time')
def get_time(datetime_object):
    if hasattr(datetime_object, 'time'):
        return str(datetime_object.time()).split(".")[0]

    return datetime_object