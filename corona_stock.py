import sqlite3


def creat_db():
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS personalDetails
                    (firstLastName  TEXT NOT NULL,
                    id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT,
                    city TEXT NOT NULL,
                    street TEXT NOT NULL,
                    number INTEGER NOT NULL,
                    dateOfBirth DATE NOT NULL,
                    telephone TEXT NOT NULL,
                    mobilePhone TEXT NOT NULL,
                    dateRecePositiveResult DATE,
                    recoveryDate DATE
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS coronaDetails
                    (id INTEGER NOT NULL ,
                    dateReceVaccin DATE NOT NULL,
                    manufacturerVaccine TEXT NOT NULL,
                    PRIMARY KEY (id, dateReceVaccin),
                    FOREIGN KEY (id) REFERENCES personalDetails(id)
                    )''')


    c.execute('''CREATE TABLE  IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image BLOB,
                FOREIGN KEY (id) REFERENCES personalDetails(id)
                );''')

    conn.commit()
    conn.close()

def get_num_vaccinations(id):
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT id FROM coronaDetails WHERE id = ?', (id,))
    schema = c.fetchall()
    if not schema:
        return None
    c.execute('SELECT count(id) FROM coronaDetails WHERE id = ?', (id,))
    schema = c.fetchall()
    conn.close()
    return schema[0][0]




def execute_query(query, args=()):
    conn = sqlite3.connect('coronaStock.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_image_from_db(image_id):
    query = 'SELECT image FROM images WHERE id = ?'
    result = execute_query(query, (image_id,))
    if result:
        return result[0][0]
    else:
        return None
