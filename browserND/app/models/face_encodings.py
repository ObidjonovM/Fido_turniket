from app import db
from sys import exc_info
from sqlalchemy import and_


class FaceEncodings(db.Model):
    __tablename__ = "face_encodings"

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey("employees.id"), unique=True, nullable=False)
    face_encodings = db.Column(db.Text, unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, emp_id, face_encodings):
        self.emp_id = emp_id
        self.face_encodings = face_encodings


    @staticmethod    
    def add2FaceEncodingsTable(emp_id, face_encodings):
        try:
            fe = FaceEncodings(emp_id, face_encodings)
            db.session.add(fe)
        
        except:
            db.rollback()
            return {
                'status_code' : -2,
                'status' : f'Could not add to the FaceEncodings table {exc_info()[0]} : {exc_info()[1]}'
            }

        db.session.commit()
        db.session.refresh(fe)

        return {
            'status_code' : 0,
            'status' : 'OK',
            'fe_record' : fe
        }


    @staticmethod
    def updateFaceEncoding(emp_id, face_encodings):
        try:
            fe = FaceEncodings.query.filter(and_(FaceEncodings.emp_id==emp_id, FaceEncodings.active==True)).first()
            old_encodings = fe.face_encodings
            db.session.query(FaceEncodings).filter(
                    and_(FaceEncodings.emp_id==emp_id, FaceEncodings.active==True)
                ).update({'face_encodings' : face_encodings})
        
        except:
            db.session.rollback()
            return {
                'status_code' : -8,
                'status' : f'Face encodings could not be updated in db {exc_info()[0]} : {exc_info()[1]}'}
        
        db.session.commit()
        return {
                'status_code' : 0,
                'status' : 'OK',
                'old_encodings' : old_encodings
            }


    @staticmethod
    def deactivateFaceEncodings(emp_id):
        try:
            fe = FaceEncodings.query.filter(and_(FaceEncodings.emp_id==emp_id, FaceEncodings.active==True)).first()
            encodings = fe.face_encodings
            db.session.query(FaceEncodings).filter(
                and_(FaceEncodings.emp_id==emp_id, FaceEncodings.active==True)
            ).update({'active' : False})
        
        except:
            db.session.rollback()
            return {
                'status_code' : -9,
                'status' : f'Record could not be deactivated from FE table {exc_info()[0]} : {exc_info()[1]}'
            }
        
        db.session.commit()
        return {
            'status_code' : 0,
            'removed_encodings' : encodings,
            'status' : 'OK'
        }


    @staticmethod
    def get_all_encodings():
        def str2vec(vec_str):
            vec_list = []
            lines = vec_str.strip()[1:-1].splitlines()
            for line in lines:
                vec_list.extend(map(float, line.split()))
            return vec_list

        fec_map = {}
        for r in FaceEncodings.query.filter_by(active=True).all():
            fec_map[r.emp_id] = str2vec(r.face_encodings)
            
        return fec_map