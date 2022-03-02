from app import db


class Entrance(db.Model):
    __tablename__ = "entrance"

    id = db.Column(db.Integer, primary_key=True)
    photo_in = db.Column(db.LargeBinary)
    photo_out = db.Column(db.LargeBinary)
    dist_in = db.Column(db.Integer)
    dist_out = db.Column(db.Integer)
    client_id = db.Column(db.Integer)
    action = db.Column(db.String(3))


    def __init__(self, photo_in, photo_out, dist_in, dist_out, client_id, action):
        self.photo_in = photo_in
        self.photo_out = photo_out
        self.dist_in = dist_in
        self.dist_out = dist_out
        self.client_id = client_id
        self.action = action


    def __repr__(self):
        return f"""Entrance Id = {self.id} : dist_in = {self.dist_in}, dist_out = {self.dist_out}, 
                   photo_in_len = {len(self.photo_in)}, photo_out_len = {len(self.photo_out)}, 
                   client_id = {self.client_id}, action = {self.action}
                """
         

    @staticmethod
    def whoIsAtEntrance_old(rec_id = None):
        if rec_id:
            query_result = Entrance.query.with_entities(
                Entrance.id, Entrance.client_id, Entrance.action
            ).filter_by(id=rec_id).first()
        else:
            query_result = Entrance.query.with_entities(
                Entrance.id, Entrance.client_id, Entrance.action
            ).order_by(Entrance.id.desc()).first()

        return query_result


    @staticmethod
    def whoIsAtEntrance(rec_id = None):
        query_result = Entrance.query.with_entities(
            Entrance.id, Entrance.client_id, Entrance.action
            ).filter(Entrance.client_id > 0).order_by(Entrance.id.desc()).first()
        
        if rec_id == query_result.id:
            return ""

        return query_result