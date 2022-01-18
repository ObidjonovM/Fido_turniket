import psycopg2 as pg2
from psycopg2.extensions import quote_ident


class MotherDB:
    
    conn = None

    def __init__(self, db_params):
        self.conn = pg2.connect(**db_params)


    def execute_query(self, sql, params=None, returns_value=True):
        cur = self.conn.cursor()

        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        ret_val = ''        
        if returns_value:
            ret_val = cur.fetchone()[0]
        
        self.conn.commit()
        cur.close()

        return ret_val


    def close(self):
        self.conn.close()



class InOutLogsDB(MotherDB):

    def insert_logs(self, values):
        sql = """
        INSERT INTO inout_logs_new (reg_time, emp_id, descr, action, label_as, dist_in, dist_out, face_dist, face_coors)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING log_id
        """        
        return self.execute_query(sql,
            (values['emp_id'], values['descr'], values['action'], '-',
            values['dist_in'], values['dist_out'], values['face_distance'], str(values['face_locations']))
        )

    def insert_log_photo(self, log_id, reg_photo):
        sql = """
        INSERT INTO inout_log_photos (log_id, log_photo) VALUES (%s, %s)
        """

        return self.execute_query(sql, (log_id, pg2.Binary(reg_photo)), False)
    


class EntranceDB(MotherDB):
     

    def insert(self, ent_values, client_id=-2, action='noa'):
        params = (pg2.Binary(ent_values.cameras.photo_in), pg2.Binary(ent_values.cameras.photo_out),
                  ent_values.turnstile.distance_in, ent_values.turnstile.distance_out,
                  client_id, action)
        sql = f"""
        INSERT INTO entrance(photo_in, photo_out, dist_in, dist_out, client_id, action)
        VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;"""
        
        return self.execute_query(sql, params) 


    def get(self, end_id):
        pass


    def delete_first_record(self):
        sql = """
        DELETE FROM entrance WHERE id IN
	(SELECT id FROM entrance ORDER BY id ASC LIMIT 1)
        RETURNING id;
	"""
        return self.execute_query(sql) 


    def delete_all(self):
        sql = f"""
        DELETE FROM entrance;
        """
        self.execute_query(sql, returns_value=False)
        

    def update(self, end_id, ent_values):
        pass


    def delete(self, end_id):
        pass


