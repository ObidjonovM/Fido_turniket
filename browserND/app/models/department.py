from app import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


    @staticmethod
    def AllDepartments():
        records = {}
        try:
            records = Department.query.with_entities(Department.id, Department.name).all()
        except:
            print("Failed to query to the table")

        return records


    @staticmethod
    def get_department(dept_id):
        record = {}
        try:
            record = Department.query.filter_by(id=dept_id).first()
        except:
            print("Failed to query to the table")

        return record