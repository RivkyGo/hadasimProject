import datetime
import tempfile
from flask import Flask, jsonify, request, send_file
import sqlite3
from dateutil.relativedelta import relativedelta
import utils
import matplotlib.pyplot as plt


app = Flask(__name__)



utils.creat_db()

@app.route('/ActivePatientsInLastMonth', methods=['GET'])
def get_ActivePatientsInLastMonth():
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    date_now = datetime.date.today()
    new_date = datetime.date(date_now.year, date_now.month - 1, date_now.day)
    first_day_of_month = new_date.replace(day=1)
    last_day_of_month = first_day_of_month + relativedelta(months=1, days=-1)
    c.execute('SELECT dateRecePositiveResult, recoveryDate FROM personalDetails WHERE '
              'dateRecePositiveResult >= ? AND dateRecePositiveResult <= ? '
              'OR recoveryDate >= ? '
              'OR recoveryDate = ? AND dateRecePositiveResult != ?',
              (first_day_of_month, last_day_of_month, first_day_of_month, None, None))
    active_patients = c.fetchall()
    Graph_active_patients_in_last_month = {}
    number_active_patients = 0
    day_in_month = first_day_of_month
    for value in active_patients:
        print(value)
    while day_in_month <= last_day_of_month:
        for date in active_patients:
            date_illness = datetime.datetime.strptime(date[0], '%Y-%m-%d').date()
            if date[1] == 'None':
                if date_illness <= day_in_month:
                    number_active_patients += 1
            else:
                date_recovery = datetime.datetime.strptime(date[1], '%Y-%m-%d').date()
                if date_illness <= day_in_month and day_in_month <= date_recovery or date_illness <= day_in_month and date_recovery is None:
                    number_active_patients += 1
        Graph_active_patients_in_last_month[str(day_in_month)] = number_active_patients
        if day_in_month == last_day_of_month:
            break
        day_in_month = day_in_month.replace(day=day_in_month.day + 1)
        number_active_patients = 0
    x = list()
    y = list()
    for date, value in Graph_active_patients_in_last_month.items():
        x.append(date)
        y.append(value)
    plt.plot(x, y)
    #
    # # customize the plot
    plt.xticks(rotation=40)
    plt.xlabel("Date")
    plt.ylabel("The number of patients")
    plt.title("Active patients in the last month")
    plt.show()
    conn.close()
    return jsonify(Graph_active_patients_in_last_month)



@app.route('/images', methods=['POST'])
def add_image():
    request_id = request.form['id']
    image_file = request.files.get('imageFile')
    image_bytes = image_file.read()  # convert to bytes
    print(type(request_id) , request_id)
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT id FROM images WHERE id = ?', (request_id,))
    ides = c.fetchall()
    if ides:
        return jsonify({"error": " This key exists in the table "})
    c.execute('SELECT id FROM personalDetails WHERE id = ?', (request_id,))
    ides = c.fetchall()
    if not ides:
        return jsonify({'error ': ' You are not a member of a health fund '})
    c.execute('INSERT INTO images (id, image) VALUES (?,?)', (request_id, sqlite3.Binary(image_bytes),))
    conn.commit()
    conn.close()
    return "OK", 200


@app.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT image FROM images WHERE id = ?', (image_id,))
    image = c.fetchone()
    conn.close()

    if image is None:
        return "Image not found", 404

    # Create a temporary file to store the image
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(image[0])
        tmp_file.flush()
        # Return the file as a response with the appropriate content type header
        return send_file(tmp_file.name, mimetype='image/jpeg'  )




@app.route('/coronaDetails', methods=['POST'])
def add_coronaDetails():
    # Add a new user to the database
    if request.method == 'POST':
        data = request.json
        # print("data", data)
        id = data['id']
        dateReceVaccin = data['dateReceVaccin']
        manufacturerVaccine = data['manufacturerVaccine']
        if id is None or dateReceVaccin is None or manufacturerVaccine is None:
            return jsonify({"error": " The values are invalid "})
        conn = sqlite3.connect('coronaStock.db')
        c = conn.cursor()
        # Checks whether such a key already exists in the table
        c.execute('SELECT * FROM coronaDetails WHERE id = ? and dateReceVaccin = ?', (id , dateReceVaccin) )
        num = c.fetchall()
        if num:
            return jsonify({"error": " This key exists in the table "})
        # Checking if there is such a member in the health fund
        c.execute('SELECT id FROM personalDetails WHERE id = ?', (id,))
        ides = c.fetchall()
        if not ides:
            return jsonify({'error ': ' You are not a member of a health fund '})
        c.execute('SELECT id FROM coronaDetails WHERE id = ?', (id,))
        ides = c.fetchall()
        print(len(ides))
        if len(ides) == 4:
            return jsonify({'error ': ' There are already 4 vaccines in the system '})

        c.execute('INSERT INTO coronaDetails (id, dateReceVaccin, manufacturerVaccine ) VALUES (?, ?,?)',
                  (id, dateReceVaccin, manufacturerVaccine))
        conn.commit()
        conn.close()
        return jsonify({"seccedd": "User added successfully"})


# The number of members who are not vaccinated
@app.route('/numNotVaccinated')
def get_numNotVaccinated():
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT count(id) FROM personalDetails WHERE id not in ('
              'SELECT DISTINCT id FROM coronaDetails )')
    schema = c.fetchall()
    conn.close()
    return jsonify(schema)


# the values of a particular person
@app.route('/coronaDetails/<int:id>')
def get_record(id):
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT * FROM coronaDetails WHERE id = ?', (id,))
    schema = c.fetchall()
    conn.close()
    return jsonify(schema)


# The number of vaccinations a particular person has received
@app.route('/numVaccinations/<int:id>')
def get_numVaccinations(id):
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT count(id) FROM coronaDetails WHERE id = ?', (id,))
    schema = c.fetchall()
    conn.close()
    return jsonify(schema)


@app.route('/adrresses')
def get_addres():
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT city,street FROM personalDetails ')
    names = c.fetchall()
    conn.close()
    return jsonify(names)


@app.route('/personalDetails/<int:id>', methods=['GET'])
def get_schema_by_id(id):
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT * FROM personalDetails WHERE id = ?', (id,))
    schema = c.fetchone()
    conn.close()
    return jsonify(schema)

@app.route('/personalDetails', methods=['GET'])
def get_personalDetails():
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT * FROM personalDetails')
    users = c.fetchall()
    return jsonify(users)


@app.route('/personalDetails', methods=['POST'])
def add_personalDetails():
    # Add a new personal to the database
    data = request.json
    name = data['firstLastName']
    id = data['id']
    city = data['city']
    street = data['street']
    number = data['number']
    dateOfBirth = data['dateOfBirth']
    telephone = data['telephone']
    mobilePhone = data['mobilePhone']
    dateRecePositiveResult = data['dateRecePositiveResult']
    recoveryDate = data['recoveryDate']
    if not name.isalpha():
        return jsonify({"error": " Must contain only letters "})
    if name is None or id is None or city is None or street is None or number is None or dateOfBirth is None or telephone is None or mobilePhone is None:
        return jsonify({"error": " The values are invalid "})
    # If the recovery date is earlier than the sick date
    if recoveryDate != None and dateRecePositiveResult == None:
        return jsonify({"error": " The values are invalid "})
    if recoveryDate < dateRecePositiveResult:
        return jsonify({"error": " The date of recovery is earlier than the date of illness "})
    dateOfBirth1 = datetime.datetime.strptime(dateOfBirth, '%Y-%m-%d').date()
    if dateOfBirth1 > datetime.date.today():
        return jsonify({"error": " Date of birth is incorrect"})
    id1 = str(id)
    if not len(id1) == 9:
        return jsonify({'invalid sintax ': ' id must be len = 9 '})
    if not id1.isdigit():
        return jsonify({'invalid sintax ': ' Must contain only numbers '})
    # if not is_valid_phone_number(mobilePhone):
    #     return jsonify({'invalid sintax ': ' The phone number '})
    conn = sqlite3.connect('coronaStock.db')
    c = conn.cursor()
    c.execute('SELECT id FROM personalDetails WHERE id = ?', (id,))
    ides = c.fetchall()
    if ides :
        return jsonify({"error": " This key exists in the table "})
    c.execute(
        'INSERT INTO personalDetails (firstLastName, id,city,street,number,dateOfBirth,telephone,mobilePhone, dateRecePositiveResult , recoveryDate  ) VALUES (?, ?,?,?,?,?,?,?,?,?)',
        (name, id, city, street, number, dateOfBirth, telephone, mobilePhone, dateRecePositiveResult, recoveryDate))
    conn.commit()
    conn.close()
    return jsonify({"seccedd": "User added successfully"})


if __name__ == '__main__':
    app.run()





