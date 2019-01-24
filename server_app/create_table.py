import sqlite3

conn = sqlite3.connect('debs.db')
cursor = conn.cursor()
# ['time', 'index', 'X', 'Y', 'Z']

# cursor.execute('CREATE TABLE IF NOT EXISTS scenes (timestamp DOUBLE, laser_id INTEGER, X DOUBLE, Y DOUBLE, Z DOUBLE)')
cursor.execute('''CREATE TABLE predictions (
                    scene INTEGER  PRIMARY KEY NOT NULL,
                    accuracy FLOAT,
                    precision FLOAT,
                    recall FLOAT,
                    prediction_speed INTEGER,
                    requested_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime')),
                    submitted_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime'))
                    )''')
conn.commit()

conn.close()
