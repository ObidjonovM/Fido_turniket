from app.models.employee import Employee
from enum import unique
from app import db
from app import utils
from datetime import datetime
from sys import exc_info


class MorePhotos(db.Model):
    __tablename__ = "more_photos"

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    photo = db.Column(db.LargeBinary, nullable=False)
    photo_encodings = db.Column(db.Text, unique=True, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)


    def __init__(self, emp_id, photo, photo_encodings):
        self.emp_id = emp_id
        self.photo = photo
        self.photo_encodings = photo_encodings
        self.date_added = datetime.today()


    @staticmethod
    def add_record(emp_id, photo, photo_encodings):
        try:
            rec = MorePhotos(emp_id, photo, photo_encodings)
            db.session.add(rec)
        
        except:
            db.session.rollback()
            return {
                'status_code' : -2,
                'status' : f'Could not add to the more_photos table {exc_info()[0]} : {exc_info()[1]}'
            }

        db.session.commit()
        db.session.refresh(rec)
        
        return {
            'status_code' : 0,
            'status' : 'OK',
            'employee' : rec
        }


    @staticmethod
    def select_all_empID_encodings():
        try:
            records = MorePhotos.query.with_entities(
                MorePhotos.emp_id, MorePhotos.photo_encodings
            ).all()
        
        except:
            return {
                'status_code' : -9,
                'status' : f'Could not get records {exc_info()[0]} : {exc_info()[1]}'
            }

        return {
            'status_code' : 0,
            'status' : 'OK',
            'records' : records
        }


    @staticmethod
    def select_emp_records(emp_id):
        try:
            records = MorePhotos.query.filter_by(emp_id=emp_id).all()
        
        except:
            return {
                'status_code' : -3,
                'status' : f'Could not get records of emp_id={emp_id}; {exc_info()[0]} : {exc_info()[1]}'
            }
        
        return {
            'status_code' : 0,
            'status' : 'OK',
            'records' : records
        }


    @staticmethod
    def select_emp_encodings(emp_id):
        try:
            encodings = MorePhotos.query.with_entities(
                MorePhotos.id, MorePhotos.photo_encodings, MorePhotos.date_added
            ).filter_by(emp_id=emp_id).all()

        except:
            return {
                'status_code' : -4,
                'status' : f'Could not get encodings of emp_id={emp_id}; {exc_info()[0]} : {exc_info()[1]}'
            }

        return {
            'status_code' : 0,
            'status' : 'OK',
            'encodings' : encodings
        }


    @staticmethod
    def select_emp_photos(emp_id):
        try:
            photos = MorePhotos.query.with_entities(
                MorePhotos.id, MorePhotos.photo, MorePhotos.date_added
            ).filter_by(emp_id=emp_id).all()

        except:
            return {
                'status_code' : -5,
                'status' : f'Could not get photos of emp_id={emp_id}; {exc_info()[0]} : {exc_info()[1]}'
            }

        return {
            'status_code' : 0,
            'status' : 'OK',
            'photos' : photos
        }


    @staticmethod
    def update_record(new_rec):
        pass                    # not needed for now


    @staticmethod
    def delete_record(rec_id):
        try:
            record = MorePhotos.query.filter_by(id=rec_id).first()
            db.session.delete(record)
        except:
            db.session.rollback()
            return {
                'status_code' : -7,
                'status' : f'Could not remove record with id = {rec_id}; {exc_info()[0]} : {exc_info()[1]}'
            }

        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK',
            'record' : record
        }


    @staticmethod
    def delete_emp_records(emp_id):
        try:
            delete_q = MorePhotos.__table__.delete().where(MorePhotos.emp_id == emp_id)
            db.session.execute(delete_q)
        except:
            db.session.rollback()
            return {
                'status_code' : -8,
                'status' : f'Could not remove records with emp_id = {emp_id}; {exc_info()[0]} : {exc_info()[1]}'
            }

        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK',
        }