from app import db
from app import utils
from datetime import datetime
from sys import exc_info


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    department = db.Column(db.String(150), nullable=False)
    job = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    date_modified = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)


    def __init__(self, name, birth_date, department, job, photo):
        self.name = name
        self.birth_date = birth_date
        self.department = department
        self.job = job
        self.photo = photo
        now = datetime.today()
        self.date_added = now
        self.date_modified = now


    def __repr__(self):
        return f"Customer Id = {self.id} : {self.name} - {self.department} - {self.job}"


    @staticmethod
    def add2EmployeeTable(cust_info):
        try:
            fullname = utils.make_fullname(cust_info['fname'],
            cust_info['lname'], cust_info['mname'])
            new_emp = Employee(fullname, 
            datetime.strptime(cust_info['birthDate'], '%Y-%m-%d'),
            cust_info['dept'], cust_info['job'], cust_info['jpeg_base64'])
            db.session.add(new_emp)

        except:
            db.session.rollback()
            return {
                'status_code' : -2,
                'status' : f'Could not add to the Employees table {exc_info()[0]} : {exc_info()[1]}'
            }

        db.session.commit()
        db.session.refresh(new_emp)

        return {
            'status_code' : 0,
            'status' : 'OK',
            'employee' : new_emp
        }


    @staticmethod
    def getAllClientNames():
        employees = {}
        try:
            records = Employee.query.with_entities(Employee.id, Employee.name).filter_by(active=True).all()
            for r in records:
                employees[r[0]] = r[1]

        except:
            print("Failed to query to the table")

        return employees


    @staticmethod
    def getClientPhoto(client_id):
        return Employee.query.with_entities(
            Employee.photo
        ).filter_by(id=client_id).first()


    @staticmethod
    def getClientFullName(client_id):
        return Employee.query.with_entities(
            Employee.name
        ).filter_by(id=client_id).first()


    @staticmethod
    def getPhotoAndName(client_id):
        return Employee.query.with_entities(
            Employee.name,
            Employee.photo
        ).filter_by(id=client_id).first()


    @staticmethod
    def removeFromEmployeeTable(emp):
        # Removes permanently from the database. 
        try:
            db.session.delete(emp)
        except:
            db.session.rollback()
            return {
                'status_code' : -5,
                'status' : f'Could not remove record with ID {emp.id} from employee table {exc_info()[0]} : {exc_info()[1]}'
            }
        
        db.session.commit()
        return {
            'status_code' : 0,
            'status' : 'OK',
            'employee' : emp
        }


    @staticmethod
    def updateEmployeeInfo(form):
        try:
            emp = Employee.query.filter_by(id=form['custId']).first()
            emp_old = emp
            emp.name = utils.make_fullname(form['fname'], form['lname'], form['mname'])
            emp.birth_date = form['birthDate']
            emp.department = form['dept']
            emp.job = form['job']
            old_photo = utils.extract_base64(emp.photo)
            emp.photo = form['jpeg_base64']
            emp.date_modified = datetime.today()
            db.session.add(emp)
        
        except:
            db.session.rollback()
            return {
                'status_code' : -7,
                'status' : f'Could not update the Employee table info {exc_info()[0]} : {exc_info()[1]} '
                }

        db.session.commit()
        return {
            'status_code' : 0,
            'old_photo' : old_photo,
            'old_record' : emp_old,
            'status' : 'OK'
            }


    @staticmethod
    def deactivateEmployee(cust_info):        #deactivate the employee
        try:
            emp = Employee.query.filter_by(id=cust_info['custId']).first()
            removed_emp = emp
            emp.active = False
            db.session.add(emp)
        
        except:
            db.session.rollback()
            return {
                'status_code' : -10,
                'status' : f'Record could not be deactivated in Employee table {exc_info()[0]} : {exc_info()[1]}'
            }

        db.session.commit()
        return {
            'status_code' : 0,
            'removed_emp' : removed_emp,
            'status' : 'OK' 
        }