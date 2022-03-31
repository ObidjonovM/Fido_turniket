from app import db
from sqlalchemy import and_, select
from sqlalchemy.sql import func


class InOutLogs(db.Model):
    __tablename__ = "inout_logs_new"

    log_id = db.Column(db.Integer, primary_key=True)
    reg_time = db.Column(db.DateTime, nullable=False)
    emp_id = db.Column(db.Integer, nullable=False)
    descr = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(3), nullable=False)
    label_as = db.Column(db.String(10), nullable=False)
    dist_in = db.Column(db.Integer, nullable=False)
    dist_out = db.Column(db.Integer, nullable=False)
    face_dist = db.Column(db.Float, nullable=False)
    face_coors = db.Column(db.String(40), nullable=False)

    
    def __init__(self, reg_time, emp_id, descr, action, label_as, dist_in, dist_out, face_dist, face_coors):
        self.reg_time = reg_time
        self.emp_id = emp_id
        self.descr = descr
        self.action = action
        self.label_as = label_as
        self.dist_in = dist_in
        self.dist_out = dist_out
        self.face_dist = face_dist
        self.face_coors = face_coors


    def __repr__(self):
        return f"Log Id = {self.log_id} : {self.reg_time} - {self.emp_id} - {self.action} - {self.descr}"


    @staticmethod
    def get_photos(emp_id, num_photos, log_id_start=None):
        query_base = InOutLogs.query.join(
            InoutLogPhotos, InOutLogs.log_id == InoutLogPhotos.log_id
        ).with_entities(InoutLogPhotos.log_id, InoutLogPhotos.log_photo)

        if log_id_start:
            query = query_base.filter(
                InOutLogs.emp_id == emp_id, InOutLogs.log_id < log_id_start
            )
        else:
            query = query_base.filter(InOutLogs.emp_id == emp_id)

        return query.order_by(InOutLogs.log_id.desc()).limit(num_photos).all()


    @staticmethod
    def get_employee_logs(emp_id, start_date, end_date):
        return InOutLogs.query.filter(
                InOutLogs.reg_time.between(start_date, end_date)
            ).filter(InOutLogs.emp_id == emp_id).with_entities(
                InOutLogs.reg_time, InOutLogs.action, 
                InOutLogs.log_id, InOutLogs.emp_id
            ).order_by(InOutLogs.log_id).all()
    
    
    @staticmethod
    def get_employees_logs_in(start_date, end_date):
        records = {}
        try:
            query = db.session.query(InOutLogs.emp_id, func.min(InOutLogs.reg_time))
            records = query.filter(InOutLogs.reg_time.between(start_date, end_date), InOutLogs.action == 'in').group_by(InOutLogs.emp_id).all()
        except:
            print("Failed to query to the table")

        return records
    
    
    @staticmethod
    def get_employees_logs_out(start_date, end_date):
        records = {}
        try:
            query = db.session.query(InOutLogs.emp_id, func.max(InOutLogs.reg_time))
            records = query.filter(InOutLogs.reg_time.between(start_date, end_date), InOutLogs.action == 'out').group_by(InOutLogs.emp_id).all()
        except:
            print("Failed to query to the table")

        return records


    @staticmethod
    def update_label_as(_log_id, label_as):
        status_code = 0
        status = 'OK'
        _label_as = ''

        try:
            if label_as == 'CORRECT' or label_as == 'WRONG':
                rec = InOutLogs.query.filter_by(log_id=_log_id).first()
                rec.label_as = label_as
                db.session.add(rec)
                _label_as = label_as

            else:
                status_code = -2
                status = f'Invalid value received: {label_as}'

        except:
            db.session.rollback()
            status_code = -1
            status = f'Could not update the value in label_as cell {exc_info()[0]} : {exc_info()[1]} '

        if status == 'OK':
            commit = db.session.commit()
        
        return {
        'status_code' : status_code,
        'status' : status,
        'label_as' : _label_as
        }


    @staticmethod
    def update_emp_id(log_id, emp_id):
        try:
            log = InOutLogs.query.filter_by(log_id=log_id).first()
            log.emp_id = emp_id
            db.session.add(log)
            
        except:
            db.session.rollback()
            return {
                'status_code' : -1,
                'status' : f'Could not update the InOutLogs table info {exc_info()[0]} : {exc_info()[1]} '
            }

        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK'
        }


class InoutLogPhotos(db.Model):
    __tablename__ = "inout_log_photos"

    log_id = db.Column(db.Integer, primary_key=True)
    log_photo = db.Column(db.LargeBinary, nullable=False)


    def __init__(self, log_id, log_photo):
        self.log_id = log_id
        self.log_photo = log_photo


    @staticmethod
    def get_log_photo(log_id):
        return InoutLogPhotos.query.filter_by(log_id=log_id).first()