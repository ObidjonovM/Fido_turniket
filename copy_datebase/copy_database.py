import psycopg2 as pg2

conn = pg2.connect("host=localhost dbname=fido_entrance_greet user=fido_entrance_greet password='Fido402'")

cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS employees_backup (
	id INT PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	birth_date DATE NOT NULL,
	department VARCHAR(150) NOT NULL,
	job VARCHAR(50) NOT NULL,
	photo TEXT NOT NULL,
	date_added TIMESTAMP NOT NULL,
	date_modified TIMESTAMP NOT NULL);
''')

cur.execute("SELECT id, name, birth_date, department, job, photo, date_added, date_modified FROM employees ORDER BY id");

records = cur.fetchall()
for record in records:
    print(f"record {record[0]}")
    cur.execute('''
	INSERT INTO employees_backup (id, name, birth_date, department, job, photo, date_added, date_modified)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    ''', record)

conn.commit()

cur.close()

conn.close()
