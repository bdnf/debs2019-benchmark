import sqlite3

conn = sqlite3.connect('debs.db')
cursor = conn.cursor()
# ['time', 'index', 'X', 'Y', 'Z']

# cursor.execute('CREATE TABLE IF NOT EXISTS scenes (timestamp DOUBLE, laser_id INTEGER, X DOUBLE, Y DOUBLE, Z DOUBLE)')
cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
                    scene INTEGER  PRIMARY KEY NOT NULL,
                    similarity_score INTEGER,
                    submitted_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime'))
                    )''')

# dummy entry
cursor.execute('''INSERT INTO predictions(scene, similarity_score, submitted_at) VALUES(101, 3, '2010-05-28T15:36:56.200')''')

conn.commit()

#measurements table
cursor.execute('''CREATE TABLE IF NOT EXISTS measurements (
                    scene INTEGER,
                    time_result INTEGER,
                    started_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime'))
                    )''')
conn.commit()

conn.close()
