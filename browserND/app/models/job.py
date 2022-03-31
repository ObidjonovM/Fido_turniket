from app import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


    @staticmethod
    def AllJobs():
        records = {}
        try:
            records = Job.query.with_entities(Job.id, Job.name).all()
        except:
            print("Failed to query to the table")

        return records


    @staticmethod
    def get_job(job_id):
        record = {}
        try:
            record = Job.query.filter_by(id=job_id).first()
        except:
            print("Failed to query to the table")

        return record