import sqlite3

import phonenumbers


def is_valid_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

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
                    PRIMARY KEY (id, dateReceVaccin)
                    )''')

    c.execute('''CREATE TABLE  IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image BLOB
                );''')

    c.execute('SELECT * FROM personalDetails')
    rows = c.fetchall()
    for row in rows:
        print(row)
    c.execute('SELECT * FROM coronaDetails')
    rows = c.fetchall()
    for row in rows:
        print(row)
    # c.execute('SELECT * FROM images')
    # rows = c.fetchall()
    # for row in rows:
    #     print(row)

    conn.commit()
    conn.close()
