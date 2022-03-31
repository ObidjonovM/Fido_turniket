from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from .job import Job
from .employee import Employee
from .department import Department
from .role import Role


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    emp_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))


    def __init__(self, login, password, role_id, emp_id, dept_id, job_id):
        self.login = login
        self.password_hash = generate_password_hash(password)
        self.role_id = role_id
        self.emp_id = emp_id
        self.department_id = dept_id
        self.job_id = job_id


    def __repr__(self):
        return f"id : {self.id}, login : '{self.login}', role_id : {self.role_id}, \
        emp_id : {self.emp_id}, department_id : {self.department_id}, job_id : {self.job_id}"


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    @staticmethod
    def AllUsers():
        records = {}
        try:
            records = db.session.query(User, Role). \
            filter(User.role_id == Role.id, User.id.notin_([1,5])). \
            order_by(User.role_id).all()
        except:
            print("Failed to query to the table")

        return records


    @staticmethod
    def AllEmployeesNotUser():
        records = {}
        try:
            query = db.session.query(Employee.id)
            query = query.filter(User.emp_id == Employee.id).subquery()
            records = db.session.query(Employee, Department, Job). \
            filter(Employee.id.notin_(query), Employee.department_id == Department.id, \
            Employee.job_id == Job.id, Employee.active == True). \
            order_by(Employee.name).all()

        except:
            print("Failed to query to the table")

        return records