import psycopg2 as pg2
from config import config


db_params = config()
conn = pg2.connect(**db_params)
cur = conn.cursor()

cmd_entrance_table = """
CREATE TABLE entrance (
	id SERIAL PRIMARY KEY,
	photo_in BYTEA NOT NULL,
        photo_out BYTEA NOT NULL,
        dist_in INTEGER NOT NULL,
	dist_out INTEGER NOT NULL,
        client_id INTEGER NOT NULL,
        action VARCHAR(3) NOT NULL)
"""

cur = conn.cursor()

cur.execute(cmd_entrance_table)

cur.close()

conn.commit()

conn.close()





